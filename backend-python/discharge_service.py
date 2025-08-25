"""
Patient Discharge Report Generator - Integrated Version
=====================================================

Comprehensive discharge report system that generates detailed reports
including admission details, treatments, equipment usage, staff assignments,
and discharge recommendations.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from database import (
    SessionLocal, Patient, Bed, User, Staff, Equipment,
    TreatmentRecord, EquipmentUsage, StaffAssignment, DischargeReport
)

class PatientDischargeReportGenerator:
    """Generate comprehensive discharge reports for patients."""
    
    def __init__(self):
        self.session = SessionLocal()
    
    def generate_discharge_report(self, 
                                bed_id: str, 
                                discharge_date: datetime = None,
                                discharge_condition: str = "stable",
                                discharge_destination: str = "home",
                                discharge_instructions: str = "",
                                follow_up_required: str = "",
                                generated_by_user_id: str = None,
                                patient_id: str = None) -> Dict[str, Any]:
        """
        Generate a comprehensive discharge report for a patient.
        """
        
        try:
            # Get bed information
            bed = self.session.query(Bed).filter(Bed.id == uuid.UUID(bed_id)).first()
            if not bed:
                return {"success": False, "message": "Bed not found"}
            
            # Check if bed is currently occupied or was recently discharged
            patient = None
            admission_date = None
            
            # If a patient_id is explicitly provided, use that as authoritative
            if patient_id:
                try:
                    patient = self.session.query(Patient).filter(Patient.id == uuid.UUID(patient_id)).first()
                except Exception:
                    patient = None
                if patient:
                    admission_date = self._find_admission_date_for_patient_bed(patient.id, bed_id)
            
            if not patient:
                if bed.patient_id:
                    # Bed is currently occupied
                    patient = bed.patient
                    admission_date = bed.admission_date
                else:
                    # Bed is available, check if it was recently discharged
                    # Look for the most recent patient assignment through historical data
                    patient = self._find_recent_patient_for_bed(bed_id)
                    if patient:
                        admission_date = self._find_admission_date_for_patient_bed(patient.id, bed_id)
                
            if not patient:
                return {"success": False, "message": "No patient found for this bed (current or recent)"}
            
            # Use discharge date from bed if available, otherwise use current time
            if bed.discharge_date:
                discharge_date = bed.discharge_date
            else:
                discharge_date = discharge_date or datetime.now()
            
            discharge_date = discharge_date or datetime.now()
            admission_date = admission_date or bed.admission_date or (datetime.now() - timedelta(days=1))
            length_of_stay = (discharge_date - admission_date).days
            
            # Generate report sections
            report_data = {
                "patient_summary": self._get_patient_summary(patient, bed, admission_date, discharge_date),
                "treatment_summary": self._get_treatment_summary(patient.id, admission_date, discharge_date),
                "equipment_summary": self._get_equipment_summary(patient.id, admission_date, discharge_date),
                "staff_summary": self._get_staff_summary(patient.id, admission_date, discharge_date),
                "medications": self._get_medications_summary(patient.id, admission_date, discharge_date),
                "procedures": self._get_procedures_summary(patient.id, admission_date, discharge_date)
            }
            
            # Create discharge report record
            report_number = f"DR-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Get or find a user for generated_by
            if not generated_by_user_id:
                # Try to find a doctor or any user as fallback
                default_user = self.session.query(User).filter(User.role == 'doctor').first()
                if not default_user:
                    default_user = self.session.query(User).first()
                if default_user:
                    generated_by_user_id = str(default_user.id)
            
            discharge_report = DischargeReport(
                patient_id=patient.id,
                bed_id=uuid.UUID(bed_id),
                generated_by=uuid.UUID(generated_by_user_id) if generated_by_user_id else None,
                report_number=report_number,
                admission_date=admission_date,
                discharge_date=discharge_date,
                length_of_stay_days=length_of_stay,
                patient_summary=json.dumps(report_data["patient_summary"]),
                treatment_summary=json.dumps(report_data["treatment_summary"]),
                equipment_summary=json.dumps(report_data["equipment_summary"]),
                staff_summary=json.dumps(report_data["staff_summary"]),
                medications=json.dumps(report_data["medications"]),
                procedures=json.dumps(report_data["procedures"]),
                discharge_instructions=discharge_instructions,
                follow_up_required=follow_up_required,
                discharge_condition=discharge_condition,
                discharge_destination=discharge_destination
            )
            
            self.session.add(discharge_report)
            self.session.commit()
            
            # Generate formatted report
            formatted_report = self._format_discharge_report(report_data, discharge_report)
            
            return {
                "success": True,
                "report_id": str(discharge_report.id),
                "report_number": report_number,
                "patient_name": f"{patient.first_name} {patient.last_name}",
                "formatted_report": formatted_report,
                "raw_data": report_data
            }
            
        except Exception as e:
            self.session.rollback()
            return {"success": False, "message": f"Failed to generate discharge report: {str(e)}"}
        finally:
            self.session.close()
    
    def _get_patient_summary(self, patient, bed, admission_date, discharge_date) -> Dict[str, Any]:
        """Get patient demographic and admission summary."""
        # Ensure dates are datetime objects
        if isinstance(admission_date, str):
            admission_date = datetime.fromisoformat(admission_date)
        if isinstance(discharge_date, str):
            discharge_date = datetime.fromisoformat(discharge_date)
            
        # Calculate length of stay safely
        length_of_stay = (discharge_date - admission_date).days
        if length_of_stay < 0:
            length_of_stay = 0
        
        return {
            "patient_id": str(patient.id),
            "patient_number": patient.patient_number,
            "name": f"{patient.first_name} {patient.last_name}",
            "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
            "gender": patient.gender,
            "blood_type": patient.blood_type,
            "allergies": patient.allergies,
            "emergency_contact": {
                "name": patient.emergency_contact_name,
                "phone": patient.emergency_contact_phone
            },
            "bed_info": {
                "bed_number": bed.bed_number,
                "room": bed.room.room_number if bed.room else None,
                "bed_type": bed.bed_type,
                "department": bed.room.department.name if bed.room and bed.room.department else None
            },
            "admission_date": admission_date.isoformat(),
            "discharge_date": discharge_date.isoformat(),
            "length_of_stay_days": length_of_stay
        }
    
    def _get_treatment_summary(self, patient_id, admission_date, discharge_date) -> List[Dict[str, Any]]:
        """Get all treatments during the stay."""
        treatments = self.session.query(TreatmentRecord).filter(
            TreatmentRecord.patient_id == patient_id,
            TreatmentRecord.start_date >= admission_date,
            TreatmentRecord.start_date <= discharge_date
        ).all()
        
        return [{
            "treatment_type": t.treatment_type,
            "treatment_name": t.treatment_name,
            "description": t.description,
            "doctor": f"{t.doctor.first_name} {t.doctor.last_name}" if t.doctor else "Unknown",
            "start_date": t.start_date.isoformat(),
            "end_date": t.end_date.isoformat() if t.end_date else None,
            "status": t.status,
            "effectiveness": t.effectiveness,
            "notes": t.notes
        } for t in treatments]
    
    def _get_equipment_summary(self, patient_id, admission_date, discharge_date) -> List[Dict[str, Any]]:
        """Get all equipment used during the stay."""
        equipment_usage = self.session.query(EquipmentUsage).filter(
            EquipmentUsage.patient_id == patient_id,
            EquipmentUsage.start_time >= admission_date,
            EquipmentUsage.start_time <= discharge_date
        ).all()
        
        return [{
            "equipment_name": eu.equipment.name if eu.equipment else "Unknown",
            "equipment_type": eu.equipment.category.name if eu.equipment and eu.equipment.category else "Unknown",
            "purpose": eu.purpose,
            "start_time": eu.start_time.isoformat(),
            "end_time": eu.end_time.isoformat() if eu.end_time else None,
            "duration_minutes": eu.duration_minutes,
            "operated_by": f"{eu.staff.user.first_name} {eu.staff.user.last_name}" if eu.staff and eu.staff.user else "Unknown",
            "readings": eu.readings,
            "notes": eu.notes
        } for eu in equipment_usage]
    
    def _get_staff_summary(self, patient_id, admission_date, discharge_date) -> List[Dict[str, Any]]:
        """Get all staff assignments during the stay."""
        staff_assignments = self.session.query(StaffAssignment).filter(
            StaffAssignment.patient_id == patient_id,
            StaffAssignment.start_date <= discharge_date,
            (StaffAssignment.end_date >= admission_date) | (StaffAssignment.end_date.is_(None))
        ).all()
        
        return [{
            "staff_name": f"{sa.staff.user.first_name} {sa.staff.user.last_name}" if sa.staff and sa.staff.user else "Unknown",
            "position": sa.staff.position if sa.staff else "Unknown",
            "department": sa.staff.department.name if sa.staff and sa.staff.department else "Unknown",
            "assignment_type": sa.assignment_type,
            "start_date": sa.start_date.isoformat(),
            "end_date": sa.end_date.isoformat() if sa.end_date else discharge_date.isoformat(),
            "shift": sa.shift,
            "responsibilities": sa.responsibilities,
            "notes": sa.notes
        } for sa in staff_assignments]
    
    def _get_medications_summary(self, patient_id, admission_date, discharge_date) -> List[Dict[str, Any]]:
        """Get medication treatments."""
        medications = self.session.query(TreatmentRecord).filter(
            TreatmentRecord.patient_id == patient_id,
            TreatmentRecord.treatment_type == "medication",
            TreatmentRecord.start_date >= admission_date,
            TreatmentRecord.start_date <= discharge_date
        ).all()
        
        return [{
            "medication_name": m.treatment_name,
            "dosage": m.dosage,
            "frequency": m.frequency,
            "duration": m.duration,
            "prescribed_by": f"{m.doctor.first_name} {m.doctor.last_name}" if m.doctor else "Unknown",
            "start_date": m.start_date.isoformat(),
            "end_date": m.end_date.isoformat() if m.end_date else None,
            "status": m.status,
            "side_effects": m.side_effects,
            "effectiveness": m.effectiveness
        } for m in medications]
    
    def _get_procedures_summary(self, patient_id, admission_date, discharge_date) -> List[Dict[str, Any]]:
        """Get procedure treatments."""
        procedures = self.session.query(TreatmentRecord).filter(
            TreatmentRecord.patient_id == patient_id,
            TreatmentRecord.treatment_type.in_(["procedure", "surgery", "therapy"]),
            TreatmentRecord.start_date >= admission_date,
            TreatmentRecord.start_date <= discharge_date
        ).all()
        
        return [{
            "procedure_name": p.treatment_name,
            "type": p.treatment_type,
            "description": p.description,
            "performed_by": f"{p.doctor.first_name} {p.doctor.last_name}" if p.doctor else "Unknown",
            "date": p.start_date.isoformat(),
            "status": p.status,
            "effectiveness": p.effectiveness,
            "notes": p.notes
        } for p in procedures]
    
    def _format_discharge_report(self, data, report_record) -> str:
        """Format the discharge report as a comprehensive document."""
        patient = data["patient_summary"]
        
        report = f"""
# PATIENT DISCHARGE REPORT
**Report Number:** {report_record.report_number}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## PATIENT INFORMATION
**Name:** {patient['name']}
**Patient ID:** {patient['patient_number']}
**Date of Birth:** {patient['date_of_birth']}
**Gender:** {patient['gender']}
**Blood Type:** {patient['blood_type']}
**Allergies:** {patient['allergies'] or 'None reported'}

**Emergency Contact:**
- **Name:** {patient['emergency_contact']['name'] or 'Not provided'}
- **Phone:** {patient['emergency_contact']['phone'] or 'Not provided'}

---

## ADMISSION & DISCHARGE DETAILS
**Admission Date:** {patient['admission_date']}
**Discharge Date:** {patient['discharge_date']}
**Length of Stay:** {patient['length_of_stay_days']} days
**Discharge Condition:** {report_record.discharge_condition}
**Discharge Destination:** {report_record.discharge_destination}

**Bed Information:**
- **Bed Number:** {patient['bed_info']['bed_number']}
- **Room:** {patient['bed_info']['room']}
- **Department:** {patient['bed_info']['department']}
- **Bed Type:** {patient['bed_info']['bed_type']}

---

## TREATMENT SUMMARY
"""
        
        # Add treatments
        if data["treatment_summary"]:
            for treatment in data["treatment_summary"]:
                report += f"""
### {treatment['treatment_name']} ({treatment['treatment_type']})
- **Doctor:** {treatment['doctor']}
- **Duration:** {treatment['start_date']} to {treatment['end_date'] or 'Ongoing'}
- **Status:** {treatment['status']}
- **Effectiveness:** {treatment['effectiveness'] or 'Not assessed'}
- **Description:** {treatment['description']}
- **Notes:** {treatment['notes'] or 'None'}
"""
        else:
            report += "\nNo treatments recorded during this stay.\n"
        
        # Add medications
        report += "\n---\n\n## MEDICATIONS\n"
        if data["medications"]:
            for med in data["medications"]:
                report += f"""
### {med['medication_name']}
- **Dosage:** {med['dosage']}
- **Frequency:** {med['frequency']}
- **Duration:** {med['duration']}
- **Prescribed by:** {med['prescribed_by']}
- **Status:** {med['status']}
- **Side Effects:** {med['side_effects'] or 'None reported'}
"""
        else:
            report += "\nNo medications prescribed during this stay.\n"
        
        # Add procedures
        report += "\n---\n\n## PROCEDURES\n"
        if data["procedures"]:
            for proc in data["procedures"]:
                report += f"""
### {proc['procedure_name']} ({proc['type']})
- **Performed by:** {proc['performed_by']}
- **Date:** {proc['date']}
- **Status:** {proc['status']}
- **Effectiveness:** {proc['effectiveness'] or 'Not assessed'}
- **Description:** {proc['description']}
"""
        else:
            report += "\nNo procedures performed during this stay.\n"
        
        # Add equipment usage
        report += "\n---\n\n## EQUIPMENT USED\n"
        if data["equipment_summary"]:
            for eq in data["equipment_summary"]:
                report += f"""
### {eq['equipment_name']} ({eq['equipment_type']})
- **Purpose:** {eq['purpose']}
- **Operated by:** {eq['operated_by']}
- **Duration:** {eq['duration_minutes']} minutes
- **Period:** {eq['start_time']} to {eq['end_time'] or 'End of stay'}
- **Notes:** {eq['notes'] or 'None'}
"""
        else:
            report += "\nNo equipment usage recorded during this stay.\n"
        
        # Add staff assignments
        report += "\n---\n\n## STAFF ASSIGNMENTS\n"
        if data["staff_summary"]:
            for staff in data["staff_summary"]:
                report += f"""
### {staff['staff_name']} - {staff['position']}
- **Department:** {staff['department']}
- **Role:** {staff['assignment_type']}
- **Period:** {staff['start_date']} to {staff['end_date']}
- **Shift:** {staff['shift'] or 'All day'}
- **Responsibilities:** {staff['responsibilities'] or 'Standard care'}
"""
        else:
            report += "\nNo specific staff assignments recorded.\n"
        
        # Add discharge instructions and follow-up
        report += f"""
---

## DISCHARGE INSTRUCTIONS
{report_record.discharge_instructions or 'Standard discharge instructions apply.'}

## FOLLOW-UP CARE REQUIRED
{report_record.follow_up_required or 'No specific follow-up required.'}

---

**Report Generated By:** Hospital Management System
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return report
    
    def _find_recent_patient_for_bed(self, bed_id: str) -> Optional[Patient]:
        """Find the most recent patient who was assigned to this bed."""
        try:
            # Primary fallback: check bed turnover logs for the most recent previous patient
            try:
                from database import BedTurnover  # local import to avoid circular refs at module load
                recent_turnover = (self.session.query(BedTurnover)
                                   .filter(BedTurnover.bed_id == uuid.UUID(bed_id))
                                   .order_by(BedTurnover.discharge_time.desc())
                                   .first())
                if recent_turnover and recent_turnover.previous_patient_id:
                    patient = self.session.query(Patient).filter(
                        Patient.id == recent_turnover.previous_patient_id
                    ).first()
                    if patient:
                        return patient
            except Exception as e:
                # Continue with legacy fallbacks
                print(f"Turnover fallback lookup failed: {e}")

            # Look through treatment records for recent activity on this bed
            recent_treatment = (self.session.query(TreatmentRecord)
                              .filter(TreatmentRecord.bed_id == uuid.UUID(bed_id))
                              .order_by(TreatmentRecord.start_date.desc())
                              .first())
            
            if recent_treatment:
                return self.session.query(Patient).filter(
                    Patient.id == recent_treatment.patient_id
                ).first()
            
            # Look through equipment usage for recent activity
            recent_equipment = (self.session.query(EquipmentUsage)
                              .filter(EquipmentUsage.bed_id == uuid.UUID(bed_id))
                              .order_by(EquipmentUsage.start_time.desc())
                              .first())
            
            if recent_equipment:
                return self.session.query(Patient).filter(
                    Patient.id == recent_equipment.patient_id
                ).first()
            
            # Look through staff assignments
            recent_assignment = (self.session.query(StaffAssignment)
                               .filter(StaffAssignment.bed_id == uuid.UUID(bed_id))
                               .order_by(StaffAssignment.created_at.desc())
                               .first())
            
            if recent_assignment:
                return self.session.query(Patient).filter(
                    Patient.id == recent_assignment.patient_id
                ).first()
            
            return None
            
        except Exception as e:
            print(f"Error finding recent patient: {e}")
            return None

    def _find_admission_date_for_patient_bed(self, patient_id: uuid.UUID, bed_id: str) -> Optional[datetime]:
        """Find the admission date for a patient on a specific bed."""
        try:
            # Ensure patient_id is UUID
            if isinstance(patient_id, str):
                patient_id = uuid.UUID(patient_id)
                
            # Look for the earliest treatment record for this patient on this bed
            earliest_treatment = (self.session.query(TreatmentRecord)
                                .filter(
                                    TreatmentRecord.patient_id == patient_id,
                                    TreatmentRecord.bed_id == uuid.UUID(bed_id)
                                )
                                .order_by(TreatmentRecord.start_date.asc())
                                .first())
            
            if earliest_treatment:
                return earliest_treatment.start_date
            
            # Look for the earliest equipment usage
            earliest_equipment = (self.session.query(EquipmentUsage)
                                .filter(
                                    EquipmentUsage.patient_id == patient_id,
                                    EquipmentUsage.bed_id == uuid.UUID(bed_id)
                                )
                                .order_by(EquipmentUsage.start_time.asc())
                                .first())
            
            if earliest_equipment:
                return earliest_equipment.start_time
            
            # Look for the earliest staff assignment
            earliest_assignment = (self.session.query(StaffAssignment)
                                 .filter(
                                     StaffAssignment.patient_id == patient_id,
                                     StaffAssignment.bed_id == uuid.UUID(bed_id)
                                 )
                                 .order_by(StaffAssignment.created_at.asc())
                                 .first())
            
            if earliest_assignment:
                return earliest_assignment.created_at
            
            # Default to a reasonable estimate (1 day before now)
            return datetime.now() - timedelta(days=1)
            
        except Exception as e:
            print(f"Error finding admission date: {e}")
            # Default fallback without invalid .strip()
            return datetime.now() - timedelta(days=1)

# Convenience function for easy import
def generate_patient_discharge_report(**kwargs):
    """Generate a discharge report."""
    generator = PatientDischargeReportGenerator()
    return generator.generate_discharge_report(**kwargs)
