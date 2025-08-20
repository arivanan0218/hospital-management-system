"""Discharge Report Agent - manages discharge workflow and related clinical records."""
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List
from .base_agent import BaseAgent

try:
    from discharge_service import PatientDischargeReportGenerator
    from discharge_report_models import TreatmentRecord, EquipmentUsage, StaffAssignment
    from database import SessionLocal
    from sqlalchemy import and_
    DISCHARGE_DEPS = True
except ImportError:
    DISCHARGE_DEPS = False

class DischargeAgent(BaseAgent):
    def __init__(self):
        super().__init__("Discharge Report Agent", "discharge_agent")
        self.generator = PatientDischargeReportGenerator() if DISCHARGE_DEPS else None

    def get_tools(self) -> List[str]:
        return [
            # Existing discharge tools
            "generate_discharge_report",
            "add_treatment_record_simple",
            "add_equipment_usage_simple",
            "assign_staff_to_patient_simple",
            "complete_equipment_usage_simple",
            "list_discharge_reports",
            
            # Bed Turnover Management Tools
            "start_bed_turnover_process",
            "complete_bed_cleaning",
            "get_bed_status_with_time_remaining",
            "add_patient_to_queue",
            "get_patient_queue",
            "assign_next_patient_to_bed",
            "update_turnover_progress",
            "get_bed_turnover_details",
            "mark_equipment_for_cleaning",
            "complete_equipment_cleaning",
            "get_equipment_turnover_status"
        ]

    def get_capabilities(self) -> List[str]:
        return [
            "Generate comprehensive discharge reports",
            "Capture treatments / equipment usage / staff assignments",
            "Finalize equipment usage records",
            "List existing discharge reports"
        ]

    # ---- Tool Implementations ----
    def generate_discharge_report(self, bed_id: str, discharge_condition: str = "stable", discharge_destination: str = "home") -> Dict[str, Any]:
        if not DISCHARGE_DEPS or not self.generator:
            return {"success": False, "message": "Discharge dependencies not available"}
        result = self.generator.generate_discharge_report(bed_id=bed_id, discharge_condition=discharge_condition, discharge_destination=discharge_destination)
        self.log_interaction(query=f"Generate discharge report for bed {bed_id}", response=result.get("message",""), tool_used="generate_discharge_report")
        return result

    def add_treatment_record_simple(self, patient_id: str, doctor_id: str, treatment_type: str, treatment_name: str) -> Dict[str, Any]:
        if not DISCHARGE_DEPS:
            return {"success": False, "message": "Discharge dependencies not available"}
        from database import SessionLocal, TreatmentRecord as CoreTreatmentRecord  # ensure main models
        db = SessionLocal()
        try:
            tr = CoreTreatmentRecord(
                patient_id=uuid.UUID(patient_id),
                doctor_id=uuid.UUID(doctor_id),
                treatment_type=treatment_type,
                treatment_name=treatment_name,
                start_date=datetime.now()
            )
            db.add(tr)
            db.commit()
            db.refresh(tr)
            db.close()
            return {"success": True, "data": {"id": str(tr.id)}}
        except Exception as e:
            db.rollback()
            db.close()
            return {"success": False, "message": str(e)}

    def add_equipment_usage_simple(self, patient_id: str, equipment_id: str, staff_id: str, purpose: str) -> Dict[str, Any]:
        if not DISCHARGE_DEPS:
            return {"success": False, "message": "Discharge dependencies not available"}
        from database import SessionLocal, EquipmentUsage as CoreEquipmentUsage
        db = SessionLocal()
        try:
            eu = CoreEquipmentUsage(
                patient_id=uuid.UUID(patient_id),
                equipment_id=uuid.UUID(equipment_id),
                staff_id=uuid.UUID(staff_id),
                purpose=purpose,
                start_time=datetime.now(),
            )
            db.add(eu)
            db.commit()
            db.refresh(eu)
            db.close()
            return {"success": True, "data": {"id": str(eu.id)}}
        except Exception as e:
            db.rollback()
            db.close()
            return {"success": False, "message": str(e)}

    def assign_staff_to_patient_simple(self, patient_id: str, staff_id: str, assignment_type: str) -> Dict[str, Any]:
        if not DISCHARGE_DEPS:
            return {"success": False, "message": "Discharge dependencies not available"}
        from database import SessionLocal, StaffAssignment as CoreStaffAssignment
        db = SessionLocal()
        try:
            sa = CoreStaffAssignment(
                patient_id=uuid.UUID(patient_id),
                staff_id=uuid.UUID(staff_id),
                assignment_type=assignment_type,
                start_date=datetime.now()
            )
            db.add(sa)
            db.commit()
            db.refresh(sa)
            db.close()
            return {"success": True, "data": {"id": str(sa.id)}}
        except Exception as e:
            db.rollback()
            db.close()
            return {"success": False, "message": str(e)}

    def complete_equipment_usage_simple(self, usage_id: str) -> Dict[str, Any]:
        if not DISCHARGE_DEPS:
            return {"success": False, "message": "Discharge dependencies not available"}
        from database import SessionLocal, EquipmentUsage as CoreEquipmentUsage
        db = SessionLocal()
        try:
            usage = db.query(CoreEquipmentUsage).filter(CoreEquipmentUsage.id == uuid.UUID(usage_id)).first()
            if not usage:
                db.close()
                return {"success": False, "message": "Usage not found"}
            usage.end_time = datetime.now()
            usage.status = "completed"
            db.commit()
            db.refresh(usage)
            db.close()
            return {"success": True, "data": {"id": str(usage.id), "status": usage.status}}
        except Exception as e:
            db.rollback()
            db.close()
            return {"success": False, "message": str(e)}

    def list_discharge_reports(self, patient_id: str = None) -> Dict[str, Any]:
        if not DISCHARGE_DEPS:
            return {"success": False, "message": "Discharge dependencies not available"}
        from database import SessionLocal, DischargeReport
        db = SessionLocal()
        try:
            q = db.query(DischargeReport)
            if patient_id:
                q = q.filter(DischargeReport.patient_id == uuid.UUID(patient_id))
            reports = q.order_by(DischargeReport.created_at.desc()).limit(25).all()
            data = []
            for r in reports:
                data.append({
                    "report_id": str(r.id),
                    "report_number": r.report_number,
                    "patient_id": str(r.patient_id),
                    "discharge_date": r.discharge_date.isoformat() if r.discharge_date else None,
                    "condition": r.discharge_condition,
                    "destination": r.discharge_destination
                })
            db.close()
            return {"success": True, "reports": data, "total": len(data)}
        except Exception as e:
            db.close()
            return {"success": False, "message": str(e)}

    # ---- Bed Turnover Management Tools ----

    def start_bed_turnover_process(self, bed_id: str, previous_patient_id: str = None, turnover_type: str = "standard", priority_level: str = "normal") -> Dict[str, Any]:
        """Initiate bed turnover process after patient discharge."""
        if not DISCHARGE_DEPS:
            return {"success": False, "message": "Discharge dependencies not available"}
        
        from database import SessionLocal, BedTurnover, Bed
        db = SessionLocal()
        try:
            # Check if bed exists and get current status
            bed = db.query(Bed).filter(Bed.id == uuid.UUID(bed_id)).first()
            if not bed:
                db.close()
                return {"success": False, "message": "Bed not found"}
            
            # Create new bed turnover record
            turnover = BedTurnover(
                bed_id=uuid.UUID(bed_id),
                previous_patient_id=uuid.UUID(previous_patient_id) if previous_patient_id else None,
                status="initiated",
                turnover_type=turnover_type,
                priority_level=priority_level,
                discharge_time=datetime.now(),
                estimated_cleaning_duration=60 if turnover_type == "deep_clean" else 45
            )
            
            db.add(turnover)
            
            # Update bed status to cleaning
            bed.status = "cleaning"
            bed.updated_at = datetime.now()
            
            db.commit()
            db.refresh(turnover)
            
            result = {
                "success": True,
                "turnover_id": str(turnover.id),
                "bed_id": bed_id,
                "status": turnover.status,
                "estimated_duration": turnover.estimated_cleaning_duration,
                "priority": priority_level,
                "message": f"Bed turnover process initiated for bed {bed.bed_number}"
            }
            
            db.close()
            return result
            
        except Exception as e:
            db.rollback()
            db.close()
            return {"success": False, "message": str(e)}

    def complete_bed_cleaning(self, turnover_id: str, inspector_id: str = None, inspection_passed: bool = True, inspector_notes: str = "") -> Dict[str, Any]:
        """Complete bed cleaning process and mark bed as ready."""
        if not DISCHARGE_DEPS:
            return {"success": False, "message": "Discharge dependencies not available"}
        
        from database import SessionLocal, BedTurnover, Bed
        db = SessionLocal()
        try:
            turnover = db.query(BedTurnover).filter(BedTurnover.id == uuid.UUID(turnover_id)).first()
            if not turnover:
                db.close()
                return {"success": False, "message": "Turnover record not found"}
            
            # Update turnover record
            turnover.cleaning_end_time = datetime.now()
            turnover.status = "cleaning_complete"
            turnover.inspection_passed = inspection_passed
            turnover.inspector_notes = inspector_notes
            
            if inspector_id:
                turnover.assigned_inspector_id = uuid.UUID(inspector_id)
            
            if inspection_passed:
                turnover.status = "ready"
                turnover.ready_time = datetime.now()
                
                # Update bed status
                bed = db.query(Bed).filter(Bed.id == turnover.bed_id).first()
                if bed:
                    bed.status = "available"
                    bed.updated_at = datetime.now()
            
            db.commit()
            db.refresh(turnover)
            
            result = {
                "success": True,
                "turnover_id": str(turnover.id),
                "status": turnover.status,
                "inspection_passed": inspection_passed,
                "cleaning_duration": (turnover.cleaning_end_time - turnover.cleaning_start_time).seconds // 60 if turnover.cleaning_start_time else None,
                "message": "Bed cleaning completed successfully" if inspection_passed else "Bed cleaning completed but failed inspection"
            }
            
            db.close()
            return result
            
        except Exception as e:
            db.rollback()
            db.close()
            return {"success": False, "message": str(e)}

    def get_bed_status_with_time_remaining(self, bed_id: str) -> Dict[str, Any]:
        """Get bed status with estimated time remaining for current process."""
        if not DISCHARGE_DEPS:
            return {"success": False, "message": "Discharge dependencies not available"}
        
        from database import SessionLocal, BedTurnover, Bed
        db = SessionLocal()
        try:
            bed = db.query(Bed).filter(Bed.id == uuid.UUID(bed_id)).first()
            if not bed:
                db.close()
                return {"success": False, "message": "Bed not found"}
            
            # Get active turnover process
            turnover = db.query(BedTurnover).filter(
                BedTurnover.bed_id == uuid.UUID(bed_id),
                BedTurnover.status.in_(["initiated", "cleaning"])
            ).first()
            
            result = {
                "success": True,
                "bed_id": bed_id,
                "bed_number": bed.bed_number,
                "current_status": bed.status,
                "room_number": bed.room.room_number if bed.room else "Unknown",
            }
            
            if turnover:
                now = datetime.now()
                
                if turnover.status == "cleaning" and turnover.cleaning_start_time:
                    elapsed = (now - turnover.cleaning_start_time).seconds // 60
                    remaining = max(0, turnover.estimated_cleaning_duration - elapsed)
                    result.update({
                        "process_status": "cleaning",
                        "time_remaining_minutes": remaining,
                        "estimated_completion": (turnover.cleaning_start_time + timedelta(minutes=turnover.estimated_cleaning_duration)).isoformat(),
                        "progress_percentage": min(100, (elapsed / turnover.estimated_cleaning_duration) * 100)
                    })
                else:
                    result.update({
                        "process_status": "initiated",
                        "time_remaining_minutes": turnover.estimated_cleaning_duration,
                        "progress_percentage": 0
                    })
            else:
                result.update({
                    "process_status": "none",
                    "time_remaining_minutes": 0,
                    "progress_percentage": 100
                })
            
            db.close()
            return result
            
        except Exception as e:
            db.close()
            return {"success": False, "message": str(e)}

    def add_patient_to_queue(self, patient_id: str, department_id: str, bed_type_required: str = "general", priority_level: str = "normal", medical_condition: str = "") -> Dict[str, Any]:
        """Add patient to bed assignment queue."""
        if not DISCHARGE_DEPS:
            return {"success": False, "message": "Discharge dependencies not available"}
        
        from database import SessionLocal, PatientQueue, Patient, Department
        db = SessionLocal()
        try:
            # Get next queue position
            max_position = db.query(PatientQueue).filter(
                PatientQueue.department_id == uuid.UUID(department_id)
            ).count()
            
            queue_entry = PatientQueue(
                patient_id=uuid.UUID(patient_id),
                department_id=uuid.UUID(department_id),
                queue_position=max_position + 1,
                bed_type_required=bed_type_required,
                priority_level=priority_level,
                medical_condition=medical_condition,
                status="waiting"
            )
            
            db.add(queue_entry)
            db.commit()
            db.refresh(queue_entry)
            
            # Get patient and department names for response
            patient = db.query(Patient).filter(Patient.id == uuid.UUID(patient_id)).first()
            department = db.query(Department).filter(Department.id == uuid.UUID(department_id)).first()
            
            result = {
                "success": True,
                "queue_id": str(queue_entry.id),
                "patient_name": f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
                "department_name": department.name if department else "Unknown",
                "queue_position": queue_entry.queue_position,
                "priority_level": priority_level,
                "estimated_wait_time": self._calculate_estimated_wait_time(db, department_id, queue_entry.queue_position)
            }
            
            db.close()
            return result
            
        except Exception as e:
            db.rollback()
            db.close()
            return {"success": False, "message": str(e)}

    def get_patient_queue(self, department_id: str = None, status: str = "waiting") -> Dict[str, Any]:
        """Get current patient queue for bed assignments."""
        if not DISCHARGE_DEPS:
            return {"success": False, "message": "Discharge dependencies not available"}
        
        from database import SessionLocal, PatientQueue, Patient, Department
        db = SessionLocal()
        try:
            query = db.query(PatientQueue).join(Patient).join(Department)
            
            if department_id:
                query = query.filter(PatientQueue.department_id == uuid.UUID(department_id))
            
            if status:
                query = query.filter(PatientQueue.status == status)
            
            queue_entries = query.order_by(PatientQueue.priority_level.desc(), PatientQueue.queue_position).all()
            
            queue_data = []
            for entry in queue_entries:
                queue_data.append({
                    "queue_id": str(entry.id),
                    "patient_id": str(entry.patient_id),
                    "patient_name": f"{entry.patient.first_name} {entry.patient.last_name}",
                    "patient_number": entry.patient.patient_number,
                    "department_name": entry.department.name,
                    "queue_position": entry.queue_position,
                    "priority_level": entry.priority_level,
                    "bed_type_required": entry.bed_type_required,
                    "medical_condition": entry.medical_condition,
                    "wait_time_minutes": (datetime.now() - entry.queue_entry_time).seconds // 60,
                    "status": entry.status
                })
            
            result = {
                "success": True,
                "queue": queue_data,
                "total_waiting": len([e for e in queue_data if e["status"] == "waiting"]),
                "departments": list(set([e["department_name"] for e in queue_data]))
            }
            
            db.close()
            return result
            
        except Exception as e:
            db.close()
            return {"success": False, "message": str(e)}

    def assign_next_patient_to_bed(self, bed_id: str, department_id: str = None) -> Dict[str, Any]:
        """Automatically assign next patient in queue to available bed."""
        if not DISCHARGE_DEPS:
            return {"success": False, "message": "Discharge dependencies not available"}
        
        from database import SessionLocal, PatientQueue, Bed, Patient, Department
        db = SessionLocal()
        try:
            # Verify bed is available
            bed = db.query(Bed).filter(Bed.id == uuid.UUID(bed_id)).first()
            if not bed or bed.status != "available":
                db.close()
                return {"success": False, "message": "Bed is not available for assignment"}
            
            # Find next patient in queue
            query = db.query(PatientQueue).filter(PatientQueue.status == "waiting")
            
            if department_id:
                query = query.filter(PatientQueue.department_id == uuid.UUID(department_id))
            elif bed.room and bed.room.department:
                query = query.filter(PatientQueue.department_id == bed.room.department_id)
            
            next_patient = query.order_by(
                PatientQueue.priority_level.desc(), 
                PatientQueue.queue_position
            ).first()
            
            if not next_patient:
                db.close()
                return {"success": False, "message": "No patients waiting in queue"}
            
            # Assign bed to patient
            next_patient.assigned_bed_id = uuid.UUID(bed_id)
            next_patient.assignment_time = datetime.now()
            next_patient.status = "assigned"
            
            # Update bed status
            bed.status = "occupied"
            bed.current_patient_id = next_patient.patient_id
            bed.updated_at = datetime.now()
            
            # Update any active bed turnover
            from database import BedTurnover
            turnover = db.query(BedTurnover).filter(
                BedTurnover.bed_id == uuid.UUID(bed_id),
                BedTurnover.status == "ready"
            ).first()
            
            if turnover:
                turnover.next_patient_id = next_patient.patient_id
                turnover.status = "assigned"
                turnover.next_assignment_time = datetime.now()
            
            db.commit()
            
            # Get patient details for response
            patient = db.query(Patient).filter(Patient.id == next_patient.patient_id).first()
            
            result = {
                "success": True,
                "assignment": {
                    "bed_id": bed_id,
                    "bed_number": bed.bed_number,
                    "patient_id": str(next_patient.patient_id),
                    "patient_name": f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
                    "patient_number": patient.patient_number if patient else "Unknown",
                    "room_number": bed.room.room_number if bed.room else "Unknown",
                    "assignment_time": next_patient.assignment_time.isoformat()
                },
                "message": f"Patient {patient.first_name} {patient.last_name} assigned to bed {bed.bed_number}"
            }
            
            db.close()
            return result
            
        except Exception as e:
            db.rollback()
            db.close()
            return {"success": False, "message": str(e)}

    def _calculate_estimated_wait_time(self, db, department_id: str, queue_position: int) -> int:
        """Calculate estimated wait time based on queue position and average turnover time."""
        # Simple estimation: assume 90 minutes average turnover time
        from database import BedTurnover
        avg_turnover_time = 90  # minutes
        
        # Get number of patients ahead in queue
        patients_ahead = queue_position - 1
        
        # Estimate based on average turnover times
        estimated_minutes = patients_ahead * avg_turnover_time
        
        return max(0, estimated_minutes)

    # Additional helper methods for equipment and staff management

    def mark_equipment_for_cleaning(self, equipment_id: str = None, bed_id: str = None, equipment_ids: List[str] = None, cleaning_type: str = "surface") -> Dict[str, Any]:
        """Mark equipment for cleaning during bed turnover."""
        if not DISCHARGE_DEPS:
            return {"success": False, "message": "Discharge dependencies not available"}
        
        from database import SessionLocal, BedTurnover, EquipmentTurnover
        db = SessionLocal()
        try:
            # Handle single equipment_id parameter (new API)
            if equipment_id and not bed_id and not equipment_ids:
                # Simple case - mark single equipment for cleaning
                from datetime import datetime
                equipment_turnover = EquipmentTurnover(
                    equipment_id=uuid.UUID(equipment_id),
                    status="cleaning",
                    start_time=datetime.now(),
                    cleaning_type=cleaning_type
                )
                db.add(equipment_turnover)
                db.commit()
                
                result = {
                    "success": True,
                    "equipment_id": equipment_id,
                    "status": "marked_for_cleaning",
                    "cleaning_type": cleaning_type,
                    "message": f"Equipment {equipment_id} marked for {cleaning_type} cleaning"
                }
                db.close()
                return result
            
            # Handle original API (bed_id + equipment_ids list)
            if not bed_id or not equipment_ids:
                db.close()
                return {"success": False, "message": "Either provide equipment_id alone, or both bed_id and equipment_ids"}
                
            # Get active turnover for this bed
            turnover = db.query(BedTurnover).filter(
                BedTurnover.bed_id == uuid.UUID(bed_id),
                BedTurnover.status.in_(["initiated", "cleaning"])
            ).first()
            
            if not turnover:
                db.close()
                return {"success": False, "message": "No active turnover found for this bed"}
            
            equipment_records = []
            for equipment_id in equipment_ids:
                equipment_turnover = EquipmentTurnover(
                    bed_turnover_id=turnover.id,
                    equipment_id=uuid.UUID(equipment_id),
                    status="needs_cleaning",
                    cleaning_required=True,
                    cleaning_type=cleaning_type,
                    release_time=datetime.now()
                )
                db.add(equipment_turnover)
                equipment_records.append(equipment_turnover)
            
            db.commit()
            
            result = {
                "success": True,
                "equipment_count": len(equipment_records),
                "cleaning_type": cleaning_type,
                "message": f"Marked {len(equipment_records)} pieces of equipment for {cleaning_type} cleaning"
            }
            
            db.close()
            return result
            
        except Exception as e:
            db.rollback()
            db.close()
            return {"success": False, "message": str(e)}

    def update_turnover_progress(self, turnover_id: str, progress_status: str) -> Dict[str, Any]:
        """Update bed turnover progress status."""
        if not DISCHARGE_DEPS:
            return {"success": False, "message": "Discharge dependencies not available"}
        
        try:
            from database import SessionLocal, BedTurnover
            db = SessionLocal()
            
            # Find the turnover record
            turnover = db.query(BedTurnover).filter(BedTurnover.turnover_id == turnover_id).first()
            
            if not turnover:
                db.close()
                return {"success": False, "message": f"Turnover {turnover_id} not found"}
            
            # Update progress status
            turnover.progress_status = progress_status
            db.commit()
            
            result = {
                "success": True,
                "message": f"Turnover progress updated to {progress_status}",
                "turnover_id": turnover_id,
                "new_status": progress_status,
                "updated_at": datetime.now().isoformat()
            }
            
            db.close()
            return result
            
        except Exception as e:
            return {"success": False, "message": f"Failed to update turnover progress: {str(e)}"}

    def get_bed_turnover_details(self, bed_id: str) -> Dict[str, Any]:
        """Get detailed information about bed turnover process."""
        if not DISCHARGE_DEPS:
            return {"success": False, "message": "Discharge dependencies not available"}
        
        try:
            from database import SessionLocal, BedTurnover, Bed
            db = SessionLocal()
            
            # Find the bed
            bed = db.query(Bed).filter(Bed.bed_id == bed_id).first()
            if not bed:
                db.close()
                return {"success": False, "message": f"Bed {bed_id} not found"}
            
            # Find active turnover
            active_turnover = db.query(BedTurnover).filter(
                BedTurnover.bed_id == bed_id,
                BedTurnover.status.in_(["in_progress", "cleaning", "inspection"])
            ).first()
            
            if not active_turnover:
                db.close()
                return {
                    "success": True,
                    "bed_id": bed_id,
                    "status": "no_active_turnover",
                    "message": "No active turnover process for this bed"
                }
            
            result = {
                "success": True,
                "bed_id": bed_id,
                "turnover_id": active_turnover.turnover_id,
                "status": active_turnover.status,
                "progress_status": getattr(active_turnover, 'progress_status', 'unknown'),
                "started_at": active_turnover.start_time.isoformat() if active_turnover.start_time else None,
                "estimated_completion": active_turnover.estimated_completion_time.isoformat() if hasattr(active_turnover, 'estimated_completion_time') and active_turnover.estimated_completion_time else None,
                "turnover_type": getattr(active_turnover, 'turnover_type', 'standard'),
                "priority": getattr(active_turnover, 'priority_level', 'normal')
            }
            
            db.close()
            return result
            
        except Exception as e:
            return {"success": False, "message": f"Failed to get turnover details: {str(e)}"}

    def complete_equipment_cleaning(self, equipment_id: str) -> Dict[str, Any]:
        """Complete equipment cleaning process."""
        if not DISCHARGE_DEPS:
            return {"success": False, "message": "Discharge dependencies not available"}
        
        try:
            from database import SessionLocal, EquipmentTurnover
            db = SessionLocal()
            
            # Find equipment turnover record
            equipment_turnover = db.query(EquipmentTurnover).filter(
                EquipmentTurnover.equipment_id == equipment_id,
                EquipmentTurnover.status == "cleaning"
            ).first()
            
            if not equipment_turnover:
                db.close()
                return {"success": False, "message": f"No active cleaning process found for equipment {equipment_id}"}
            
            # Update status to cleaned
            equipment_turnover.status = "cleaned"
            equipment_turnover.completion_time = datetime.now()
            db.commit()
            
            result = {
                "success": True,
                "message": f"Equipment {equipment_id} cleaning completed",
                "equipment_id": equipment_id,
                "completed_at": datetime.now().isoformat(),
                "status": "cleaned"
            }
            
            db.close()
            return result
            
        except Exception as e:
            return {"success": False, "message": f"Failed to complete equipment cleaning: {str(e)}"}

    def get_equipment_turnover_status(self, equipment_id: str) -> Dict[str, Any]:
        """Get equipment turnover status."""
        if not DISCHARGE_DEPS:
            return {"success": False, "message": "Discharge dependencies not available"}
        
        try:
            from database import SessionLocal, EquipmentTurnover, Equipment
            db = SessionLocal()
            
            # Find equipment
            equipment = db.query(Equipment).filter(Equipment.equipment_id == equipment_id).first()
            if not equipment:
                db.close()
                return {"success": False, "message": f"Equipment {equipment_id} not found"}
            
            # Find active turnover
            active_turnover = db.query(EquipmentTurnover).filter(
                EquipmentTurnover.equipment_id == equipment_id,
                EquipmentTurnover.status.in_(["cleaning", "maintenance", "inspection"])
            ).first()
            
            if not active_turnover:
                db.close()
                return {
                    "success": True,
                    "equipment_id": equipment_id,
                    "status": "available",
                    "message": "Equipment is available for use"
                }
            
            result = {
                "success": True,
                "equipment_id": equipment_id,
                "turnover_status": active_turnover.status,
                "started_at": active_turnover.start_time.isoformat() if active_turnover.start_time else None,
                "estimated_completion": active_turnover.estimated_completion_time.isoformat() if hasattr(active_turnover, 'estimated_completion_time') and active_turnover.estimated_completion_time else None,
                "cleaning_type": getattr(active_turnover, 'cleaning_type', 'standard')
            }
            
            db.close()
            return result
            
        except Exception as e:
            return {"success": False, "message": f"Failed to get equipment turnover status: {str(e)}"}
