# 🏥 Hospital Management System - Comprehensive Test Cases

## 📋 Overview
This document contains comprehensive test cases for the Hospital Management System frontend chatbot. Each test case includes the exact query to type, expected behavior, and validation steps.

**System Components Tested:**
- Patient Management
- Bed Management & Room Assignments
- Staff Management
- Equipment Management
- Supply Management & Usage Tracking
- Discharge Workflow
- Inventory Management
- Medical Documentation
- AI Processing & Intelligent Responses

---

## 🧪 TEST CATEGORIES

### 1. PATIENT MANAGEMENT

#### 1.1 Patient Registration
**Test Case**: Create New Patient
```
Query: "Register new patient"
Expected: Patient registration popup form appears
Form Fields: First Name, Last Name, Date of Birth, Phone, Email, Address, Emergency Contact
Validation: All required fields must be filled
Success: Patient gets unique patient number (P001, P002, etc.)
```

**Test Case**: List Active Patients
```
Query: "List patients"
Expected: Shows only active patients (excludes discharged)
Validation: Check patient count and status
```

**Test Case**: List All Patients
```
Query: "Show all patients"
Expected: Shows both active and discharged patients
Validation: Verify discharged patients appear with correct status
```

**Test Case**: Search Patient by Name
```
Query: "Find patient John Smith"
Expected: Returns matching patient information
Validation: Patient details displayed correctly
```

**Test Case**: Search Patient by Number
```
Query: "Get patient P002"
Expected: Returns specific patient by patient number
Validation: Correct patient information displayed
```

#### 1.2 Patient Updates
**Test Case**: Update Patient Information
```
Query: "Update patient P001"
Expected: Patient update popup form appears
Validation: Form pre-populated with current data
Success: Changes saved and confirmed
```

---

### 2. BED AND ROOM MANAGEMENT

#### 2.1 Bed Status Queries
**Test Case**: Check Bed Status
```
Query: "Bed 302A status"
Expected: Shows current bed status (available, occupied, cleaning, maintenance)
Validation: Status, patient assignment, and room details
```

**Test Case**: List Available Beds
```
Query: "Show available beds"
Expected: Lists all beds with status "available"
Validation: Bed numbers, room assignments, and capacity
```

**Test Case**: List All Beds
```
Query: "List all beds"
Expected: Shows beds with all statuses
Validation: Complete bed inventory with statuses
```

#### 2.2 Bed Assignments
**Test Case**: Assign Patient to Bed
```
Query: "Assign patient P002 to bed 302A"
Expected: Assignment confirmation
Validation: 
- Bed status changes to "occupied"
- Patient linked to bed
- Room assignment updated
```

**Test Case**: Check Room Occupancy
```
Query: "Room 302 occupancy"
Expected: Shows all beds in room with patient assignments
Validation: Room layout and current occupants
```

#### 2.3 Bed Turnover Process
**Test Case**: Check Bed Cleaning Status
```
Query: "Bed 302A cleaning status"
Expected: Shows cleaning progress and estimated completion
Validation: Cleaning start time, progress, estimated completion
```

---

### 3. STAFF MANAGEMENT

#### 3.1 Staff Registration
**Test Case**: Register New Staff
```
Query: "Register new staff member"
Expected: Staff registration popup form appears
Form Fields: Name, Position, Department, Employee ID, Contact Info
Validation: Employee ID uniqueness (EMP001, EMP002, etc.)
```

#### 3.2 Staff Queries
**Test Case**: List All Staff
```
Query: "List staff members"
Expected: Shows all registered staff
Validation: Names, positions, departments, employee IDs
```

**Test Case**: Find Staff by Department
```
Query: "Show nursing staff"
Expected: Filters staff by department/position
Validation: Correct department filtering
```

**Test Case**: Find Specific Staff Member
```
Query: "Find staff EMP001"
Expected: Shows specific staff member details
Validation: Complete staff profile information
```

---

### 4. EQUIPMENT MANAGEMENT

#### 4.1 Equipment Registration
**Test Case**: Register New Equipment
```
Query: "Register new equipment"
Expected: Equipment registration popup form appears
Form Fields: Name, Category, Model, Serial Number, Location
Validation: Equipment gets unique equipment ID
```

#### 4.2 Equipment Queries
**Test Case**: List Available Equipment
```
Query: "Show available equipment"
Expected: Lists equipment with status "available"
Validation: Equipment names, categories, locations
```

**Test Case**: Equipment Usage Tracking
```
Query: "Add equipment usage for patient P002"
Expected: Equipment usage form appears
Form Fields: Equipment selection, usage start/end times, notes
Validation: Usage recorded and equipment status updated
```

**Test Case**: Check Equipment Status
```
Query: "Equipment EQ001 status"
Expected: Shows current equipment status and location
Validation: Status, current assignment, maintenance schedule
```

---

### 5. SUPPLY MANAGEMENT & USAGE TRACKING

#### 5.1 Supply Registration
**Test Case**: Register New Supply
```
Query: "Register new supply item"
Expected: Supply registration popup form appears
Form Fields: Name, Category, Item Code, Unit Cost, Stock Level
Validation: Supply gets unique item code (MED001, SUP002, etc.)
```

#### 5.2 Supply Inventory
**Test Case**: Check Supply Inventory
```
Query: "Show supply inventory"
Expected: Lists all supplies with current stock levels
Validation: Stock levels, unit costs, low stock alerts
```

**Test Case**: Low Stock Alerts
```
Query: "Show low stock items"
Expected: Lists supplies below minimum threshold
Validation: Critical stock levels highlighted
```

#### 5.3 Patient Supply Usage (Enhanced Feature)
**Test Case**: Record Supply Usage with User-Friendly Codes
```
Query: "Record patient supply usage"
Input Format:
- Patient ID: P002
- Supply Item Code: MED001
- Quantity Used: 2
- Date of Usage: 2025-08-26
- Staff ID: EMP001
- Additional Notes: Administered Aspirin 81mg

Expected: Success confirmation with usage details
Validation:
- Patient P002 → Resolves to patient UUID
- Supply MED001 → Resolves to supply UUID  
- Staff EMP001 → Resolves to staff user UUID
- Cost calculation: Quantity × Unit Cost
- Record stored in patient_supply_usage table
```

**Test Case**: View Patient Supply History
```
Query: "Show supply usage for patient P002"
Expected: Complete medication/supply history for patient
Validation: All usage records with dates, quantities, costs
```

**Test Case**: Calculate Patient Medication Costs
```
Query: "Calculate medication costs for patient P002"
Expected: Total cost breakdown for patient stay
Validation: Individual item costs and total amount
```

---

### 6. DISCHARGE WORKFLOW

#### 6.1 Patient Discharge Process
**Test Case**: Complete Patient Discharge
```
Query: "Discharge patient P001"
Expected: Discharge process initiated
Process Steps:
1. Discharge report generation
2. Patient status → "discharged"
3. Bed status → "cleaning"
4. Bed assignment cleared
5. Cleaning timer started (30 minutes)

Validation:
- Patient no longer in active patient list
- Bed shows "cleaning" status
- Discharge report generated
- PDF download link provided
```

**Test Case**: Discharge by Bed Number
```
Query: "Discharge bed 302A"
Expected: Discharges patient currently in bed 302A
Validation: Same discharge process as above
```

#### 6.2 Post-Discharge Verification
**Test Case**: Check Patient Status After Discharge
```
Query: "Patient P001 status"
Expected: Shows "discharged" status with discharge details
Validation: Discharge date, condition, destination
```

**Test Case**: Verify Bed Cleaning Process
```
Query: "Bed 302A status"
Expected: Shows "cleaning" status with timer
Validation: Cleaning start time, estimated completion
```

**Test Case**: List Discharged Patients
```
Query: "Show discharged patients"
Expected: Lists all patients with "discharged" status
Validation: Discharge dates and destinations
```

#### 6.3 Automatic Bed Availability
**Test Case**: Bed Becomes Available After Cleaning
```
Setup: Wait 30 minutes after discharge (or manually complete)
Query: "Bed 302A status"
Expected: Status changes to "available"
Validation: Bed ready for new patient assignment
```

---

### 7. INVENTORY MANAGEMENT

#### 7.1 Stock Updates
**Test Case**: Update Supply Stock
```
Query: "Update stock for MED001"
Expected: Stock update form appears
Validation: Current stock shown, new quantity updated
```

**Test Case**: Add Supply Category
```
Query: "Add new supply category"
Expected: Category creation form appears
Validation: Category added to system
```

---

### 8. MEDICAL DOCUMENTATION

#### 8.1 Treatment Records
**Test Case**: Add Treatment Record
```
Query: "Add treatment for patient P002"
Expected: Treatment form appears
Form Fields: Treatment type, medication, dosage, notes
Validation: Treatment linked to patient record
```

#### 8.2 Document Management
**Test Case**: View Patient Documents
```
Query: "Show documents for patient P002"
Expected: Lists all medical documents for patient
Validation: Document types, dates, processing status
```

---

### 9. SYSTEM INTEGRATION TESTS

#### 9.1 Complete Patient Journey
**Test Case**: Full Patient Workflow
```
1. "Register new patient" → Create patient P005
2. "Assign patient P005 to bed 302B" → Bed assignment
3. "Record patient supply usage" → Add medication usage
4. "Add treatment for patient P005" → Medical treatment
5. "Discharge patient P005" → Complete discharge
6. "List discharged patients" → Verify in discharge list
7. "Bed 302B status" → Verify bed cleaning
```

#### 9.2 Supply Chain Workflow
**Test Case**: Supply Usage Impact
```
1. "Show supply inventory" → Check MED001 stock level
2. "Record patient supply usage" → Use 5 units of MED001
3. "Show supply inventory" → Verify stock decreased by 5
4. "Show supply usage for patient" → Verify usage recorded
```

---

### 10. AI PROCESSING & INTELLIGENT RESPONSES

#### 10.1 Natural Language Understanding
**Test Case**: Conversational Queries
```
Query: "Who is in room 302?"
Expected: AI processes and shows room occupancy
```

**Test Case**: Complex Information Requests
```
Query: "Show me all patients who need medication today"
Expected: AI processes and filters relevant patients
```

#### 10.2 Context Awareness
**Test Case**: Follow-up Questions
```
Query 1: "Show patient P002"
Query 2: "What medications has this patient received?"
Expected: AI understands "this patient" refers to P002
```

---

## 🔧 TECHNICAL VALIDATION

### Database Verification Commands
After each test, you can verify results using these commands:

```bash
# Check patient supply usage records
cd "backend-python" ; python ..\verify_database.py

# Check patient statuses
cd "backend-python" ; python ..\debug_patient_listing.py

# Check bed statuses and assignments
# (Run through frontend or create specific test script)
```

### API Response Validation
- All successful operations return `"success": true`
- Error messages are clear and helpful
- Data format is consistent across endpoints
- User-friendly codes (P002, MED001, EMP001) work correctly

---

## 🎯 SUCCESS CRITERIA

### ✅ Passing Tests Should Show:
1. **Patient Management**: Registration, updates, and status tracking work
2. **Bed Management**: Assignment, status updates, and cleaning workflow
3. **Supply Tracking**: User-friendly codes resolve to UUIDs correctly
4. **Discharge Process**: Complete workflow with status updates
5. **Database Integration**: All changes persist correctly
6. **Frontend Integration**: Popup forms appear and submit correctly
7. **AI Processing**: Natural language queries processed intelligently

### ❌ Failing Tests Indicate:
- Database connection issues
- Frontend-backend communication problems
- User-friendly code resolution failures
- Status update problems
- Popup form display issues

---

## 📈 TESTING BEST PRACTICES

1. **Test Environment**: Use consistent test data
2. **Sequential Testing**: Follow logical workflow order
3. **Data Cleanup**: Reset test data between major test runs
4. **Error Handling**: Test invalid inputs and edge cases
5. **Performance**: Monitor response times for complex queries
6. **Cross-Feature Testing**: Verify features work together correctly

---

## 🚀 GETTING STARTED

1. **Start Backend**: Ensure multi_agent_server.py is running
2. **Start Frontend**: Launch the React frontend application
3. **Open Chatbot**: Access the DirectMCPChatbot interface
4. **Begin Testing**: Start with basic patient registration
5. **Progress Through**: Follow the test categories in order
6. **Validate Results**: Check both frontend responses and database state

---

*This test suite covers the complete functionality of your Hospital Management System. Each test case has been validated and represents real-world usage scenarios.*
