# Patient Supply Usage Tracking System

## Overview

The Patient Supply Usage Tracking System provides comprehensive medication and supply inventory management with full integration into discharge reports. This system tracks what medications and supplies are used for each patient during their stay and includes this information in the discharge documentation.

## Features

### 🔧 Core Functionality
- **Supply Usage Recording**: Track medications and supplies used per patient
- **Cost Tracking**: Monitor costs for billing and reporting
- **Clinical Documentation**: Record dosage, frequency, administration details
- **Status Management**: Track prescription → administration → completion workflow
- **Discharge Integration**: Automatic inclusion in discharge reports

### 📊 Key Benefits
- **Comprehensive Tracking**: Every medication and supply used is recorded
- **Cost Transparency**: Clear breakdown of medication costs in discharge reports
- **Clinical Documentation**: Detailed administration records for medical history
- **Inventory Integration**: Automatic stock updates when supplies are used
- **Billing Support**: Accurate cost calculations for insurance and billing

## Database Schema

### PatientSupplyUsage Table
```sql
CREATE TABLE patient_supply_usage (
    id UUID PRIMARY KEY,
    patient_id UUID REFERENCES patients(id),
    supply_id UUID REFERENCES supplies(id),
    quantity_used INTEGER NOT NULL,
    unit_cost DECIMAL(8,2),
    total_cost DECIMAL(10,2),
    prescribed_by_id UUID REFERENCES users(id),
    administered_by_id UUID REFERENCES users(id), 
    bed_id UUID REFERENCES beds(id),
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    administration_route VARCHAR(50),
    indication VARCHAR(200),
    prescribed_date TIMESTAMP NOT NULL,
    administration_date TIMESTAMP,
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'prescribed',
    effectiveness VARCHAR(20),
    side_effects TEXT,
    notes TEXT,
    billed BOOLEAN DEFAULT FALSE,
    insurance_covered BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## API Tools

### 1. record_patient_supply_usage
Record medication or supply usage for a patient.

**Parameters:**
- `patient_id` (required): Patient UUID
- `supply_id` (required): Supply/medication UUID
- `quantity_used` (required): Amount used
- `dosage`: Medication dosage (e.g., "500mg")
- `frequency`: Administration frequency (e.g., "twice daily")
- `prescribed_by_id`: Doctor who prescribed
- `administered_by_id`: Staff who administered
- `bed_id`: Where administered
- `administration_route`: How administered (oral, IV, injection, topical)
- `indication`: Why prescribed/used
- `start_date`: Treatment start date
- `end_date`: Treatment end date

**Example:**
```json
{
  "patient_id": "550e8400-e29b-41d4-a716-446655440000",
  "supply_id": "660e8400-e29b-41d4-a716-446655440001", 
  "quantity_used": 30,
  "dosage": "500mg",
  "frequency": "twice daily",
  "indication": "pain management",
  "administration_route": "oral"
}
```

### 2. get_supply_usage_for_discharge_report
Get all supply usage for a patient's discharge report.

**Parameters:**
- `patient_id` (required): Patient UUID
- `admission_date` (optional): Filter from admission date
- `discharge_date` (optional): Filter to discharge date

**Returns:**
```json
{
  "success": true,
  "data": {
    "medications": [...],
    "medical_supplies": [...], 
    "total_cost": 125.50,
    "summary": {
      "medications_count": 5,
      "supplies_count": 8,
      "total_cost": 125.50
    }
  }
}
```

### 3. update_supply_usage_status
Update status of supply usage.

**Status Options:**
- `prescribed`: Initial state when prescribed
- `administered`: When actually given to patient
- `completed`: Treatment completed successfully
- `discontinued`: Treatment stopped early

### 4. list_patient_medications
List all medications/supplies used by a patient.

### 5. search_supply_usage_by_patient
Search usage records by patient name, number, or supply.

### 6. calculate_patient_medication_costs
Calculate total medication costs for a patient stay.

## Discharge Report Integration

### Enhanced MEDICATIONS Section
The discharge report now includes both:

1. **Traditional Medications** (from TreatmentRecord)
   - Doctor prescribed treatments
   - Clinical protocols

2. **Supply Usage & Inventory** (from PatientSupplyUsage)
   - Actual medications administered from inventory
   - Medical supplies used
   - Cost breakdown
   - Administration details

### Sample Discharge Report Output

```markdown
## MEDICATIONS

### Paracetamol 500mg
- **Dosage:** 500mg
- **Frequency:** twice daily
- **Duration:** 5 days
- **Prescribed by:** Dr. Smith
- **Status:** completed

---

## SUPPLY USAGE & INVENTORY

### 💊 Medications Used

**Paracetamol 500mg** (Medications)
- **Quantity:** 30 tablets
- **Dosage:** 500mg
- **Frequency:** twice daily
- **Route:** oral
- **Indication:** pain management
- **Prescribed by:** Dr. Smith
- **Status:** completed
- **Cost:** $7.50
- **Effectiveness:** effective

### 🏥 Medical Supplies Used

**Disposable Syringe 5ml** (Medical Supplies)
- **Quantity:** 5 pieces
- **Used for:** medication administration
- **Used by:** Nurse Johnson
- **Cost:** $2.50

### 💰 Supply Cost Summary
- **Total Medications:** 3 items
- **Total Supplies:** 5 items  
- **Total Cost:** $45.75
```

## Workflow Examples

### Example 1: Recording Medication Usage
```bash
# Patient admitted, doctor prescribes Paracetamol
record_patient_supply_usage(
  patient_id="patient-uuid",
  supply_id="paracetamol-uuid", 
  quantity_used=30,
  dosage="500mg",
  frequency="twice daily",
  prescribed_by_id="doctor-uuid",
  indication="post-surgical pain management"
)

# Nurse administers first dose
update_supply_usage_status(
  usage_id="usage-uuid",
  status="administered", 
  administration_date="2025-01-15T08:00:00"
)

# Treatment completed
update_supply_usage_status(
  usage_id="usage-uuid",
  status="completed",
  effectiveness="effective"
)
```

### Example 2: Discharge Report Generation
```bash
# Generate discharge report with supply usage
get_supply_usage_for_discharge_report(
  patient_id="patient-uuid",
  admission_date="2025-01-10T00:00:00",
  discharge_date="2025-01-15T12:00:00"
)

# This data is automatically included in discharge reports
generate_discharge_report(
  bed_id="bed-uuid",
  discharge_condition="stable"
)
```

## Testing & Validation

### Run Migration
```bash
cd backend-python
python migrate_supply_usage.py
```

### Test Tools
```bash
# Test recording usage
python -c "
from multi_agent_server import record_patient_supply_usage
result = record_patient_supply_usage(
  patient_id='test-patient-id',
  supply_id='test-supply-id', 
  quantity_used=10
)
print(result)
"

# Test discharge report integration
python -c "
from multi_agent_server import get_supply_usage_for_discharge_report
result = get_supply_usage_for_discharge_report(patient_id='test-patient-id')
print(result)
"
```

## Benefits for Hospital Operations

### 📊 Improved Reporting
- Complete medication history in discharge reports
- Accurate cost tracking for billing
- Detailed supply usage analytics

### 💰 Cost Management  
- Track medication costs per patient
- Identify cost optimization opportunities
- Support insurance billing with detailed records

### 🏥 Clinical Documentation
- Complete medication administration records
- Track effectiveness and side effects
- Support clinical decision making

### 📦 Inventory Integration
- Automatic stock updates when supplies used
- Track usage patterns for reorder planning
- Prevent stockouts of critical medications

## Architecture

```
Frontend Request
     ↓
Multi-Agent Server
     ↓
PatientSupplyUsageAgent
     ↓
PatientSupplyUsage Database Table
     ↓
DischargeReportService (integration)
     ↓
Enhanced Discharge Report
```

The system provides a complete end-to-end solution for tracking medication and supply usage with full integration into the hospital's discharge documentation workflow.
