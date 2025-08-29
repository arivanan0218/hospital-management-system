import sys
import json
from datetime import date, datetime

# Use local imports from the project
from database import SessionLocal, Patient, Supply, PatientSupplyUsage

patient_number = sys.argv[1] if len(sys.argv) > 1 else None
supply_code = sys.argv[2] if len(sys.argv) > 2 else None

session = SessionLocal()
try:
    patient = None
    if patient_number:
        patient = session.query(Patient).filter(Patient.patient_number == patient_number).first()

    supply = None
    if supply_code:
        supply = session.query(Supply).filter(Supply.item_code == supply_code).first()

    if not patient and not supply:
        print(json.dumps({"error": "no_patient_no_supply", "patient": None, "supply": None}))
        sys.exit(0)

    query = session.query(PatientSupplyUsage)
    if patient:
        query = query.filter(PatientSupplyUsage.patient_id == patient.id)
    if supply:
        query = query.filter(PatientSupplyUsage.supply_id == supply.id)

    results = []
    for u in query.order_by(PatientSupplyUsage.created_at.desc()).limit(50).all():
        results.append({
            "id": str(u.id),
            "patient_id": str(u.patient_id),
            "supply_id": str(u.supply_id),
            "quantity_used": u.quantity_used,
            "unit_cost": float(u.unit_cost) if u.unit_cost is not None else None,
            "total_cost": float(u.total_cost) if u.total_cost is not None else None,
            "status": u.status,
            "start_date": u.start_date.isoformat() if u.start_date else None,
            "administration_date": u.administration_date.isoformat() if u.administration_date else None,
            "notes": u.notes,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "updated_at": u.updated_at.isoformat() if u.updated_at else None,
        })

    out = {"patient": patient_number, "supply_code": supply_code, "count": len(results), "results": results}
    print(json.dumps(out, indent=2))
finally:
    session.close()
