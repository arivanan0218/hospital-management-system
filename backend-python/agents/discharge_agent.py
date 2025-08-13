"""Discharge Report Agent - manages discharge workflow and related clinical records."""
import uuid
from datetime import datetime
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
            "generate_discharge_report",
            "add_treatment_record_simple",
            "add_equipment_usage_simple",
            "assign_staff_to_patient_simple",
            "complete_equipment_usage_simple",
            "list_discharge_reports"
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
