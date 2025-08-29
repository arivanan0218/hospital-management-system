import sys
import json
from database import SessionLocal, PatientSupplyUsage
import uuid

usage_id = sys.argv[1] if len(sys.argv) > 1 else None
if not usage_id:
    print(json.dumps({"error": "usage_id_required"}))
    sys.exit(1)

session = SessionLocal()
try:
    try:
        uid = uuid.UUID(usage_id)
    except Exception as e:
        print(json.dumps({"error": "invalid_uuid", "msg": str(e)}))
        sys.exit(1)

    usage = session.query(PatientSupplyUsage).filter(PatientSupplyUsage.id == uid).first()
    if not usage:
        print(json.dumps({"found": False, "id": usage_id}))
    else:
        out = {
            "found": True,
            "id": str(usage.id),
            "patient_id": str(usage.patient_id),
            "supply_id": str(usage.supply_id),
            "quantity_used": usage.quantity_used,
            "status": usage.status,
            "start_date": usage.start_date.isoformat() if usage.start_date else None,
            "created_at": usage.created_at.isoformat() if usage.created_at else None,
            "notes": usage.notes,
        }
        print(json.dumps(out, indent=2))
finally:
    session.close()
