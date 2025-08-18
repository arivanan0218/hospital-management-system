# Test Cases for Intelligent AI Processing

## Popup Form Tests (Should show popup forms)

### create_user
- "Create a new user"
- "Add new user to the system"
- "Register new user"

### create_patient  
- "Register a new patient"
- "Admit new patient"
- "Add patient to the system"

### create_legacy_user
- "Create legacy user"
- "Add legacy user"

### create_department
- "Create new department"
- "Add cardiology department"
- "Create radiology department"

### create_room
- "Create new room"
- "Add room 101"
- "Register new room"

### create_bed
- "Create new bed"
- "Add bed to room"
- "Register new bed"

### create_staff
- "Add new staff member"
- "Hire new doctor"
- "Create staff record"

### create_equipment
- "Add new equipment" ✅ (Should show popup)
- "Create new equipment" ✅ (Should show popup)  
- "Register new equipment" ✅ (Should show popup)

### create_supply
- "Add new supply" ✅ (Should show popup)
- "Create new supply" ✅ (Should show popup)
- "Register new supply" ✅ (Should show popup)

### create_appointment
- "Book patient appointment"
- "Schedule appointment with doctor"
- "Create patient appointment"

## AI Processing Tests (Should use backend tools, NOT popup forms)

### Equipment/Supply Categories (Critical Fix)
- "Create equipment category" ❌ (Should use AI processing, NOT popup)
- "Add equipment category" ❌ (Should use AI processing, NOT popup)
- "Create supply category" ❌ (Should use AI processing, NOT popup) 
- "Add supply category" ❌ (Should use AI processing, NOT popup)

### All Other Tools
- "List all patients" (uses list_patients)
- "Show all departments" (uses list_departments)
- "Find patient John Smith" (uses search_patients)
- "Update bed status" (uses update_bed_status)
- "Schedule staff meeting" (uses schedule_meeting)
- "Generate discharge report" (uses generate_discharge_report)
- "Show equipment status" (uses list_equipment)
- "Check supply inventory" (uses list_supplies)
- "Update equipment status" (uses update_equipment_status)
- "Delete patient record" (uses delete_patient)

## Expected Behavior

1. **Popup Forms**: Only show for the exact 10 CREATE tools listed above
2. **AI Processing**: Everything else goes through intelligent backend agent processing
3. **Categories**: Equipment and supply categories should NEVER show popup forms
4. **Meetings**: Staff meetings use AI processing (schedule_meeting tool)
5. **Appointments**: Patient appointments show popup form (create_appointment)

## Key Fix

The main issue was that "create equipment category" was incorrectly triggering the equipment popup form. Now:

- ✅ "create equipment" → Equipment popup form
- ✅ "create equipment category" → AI processing (backend tool)
- ✅ "create supply" → Supply popup form  
- ✅ "create supply category" → AI processing (backend tool)
