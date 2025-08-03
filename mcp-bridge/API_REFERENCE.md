# Hospital Management System MCP Bridge - API Reference

## Base URL
```
http://localhost:8080
```

## Authentication
Currently no authentication is required (development mode).

## Response Format
All responses follow this structure:
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... }
}
```

Error responses:
```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error information"
}
```

## Core Endpoints

### Health Check
```http
GET /health
```
Response:
```json
{
  "status": "healthy",
  "bridge_active": true
}
```

### List Tools
```http
GET /tools
```
Response:
```json
{
  "tools": [
    {
      "name": "create_user",
      "description": "Create a new user in the database",
      "inputSchema": { ... }
    }
  ],
  "count": 25
}
```

### Call Any Tool
```http
POST /tools/{tool_name}
Content-Type: application/json

{
  "param1": "value1",
  "param2": "value2"
}
```

## User Management

### Create User
```http
POST /users
Content-Type: application/json

{
  "username": "doctor1",
  "email": "doctor1@hospital.com",
  "password_hash": "hashed_password",
  "role": "doctor",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "555-0123"
}
```

### List Users
```http
GET /users
```

### Get User
```http
GET /users/{user_id}
```

### Update User
```http
POST /tools/update_user

{
  "user_id": "uuid-here",
  "first_name": "Updated Name",
  "is_active": true
}
```

### Delete User
```http
POST /tools/delete_user

{
  "user_id": "uuid-here"
}
```

## Patient Management

### Create Patient
```http
POST /patients
Content-Type: application/json

{
  "patient_number": "P001",
  "first_name": "Jane",
  "last_name": "Smith",
  "date_of_birth": "1990-01-15",
  "gender": "Female",
  "phone": "555-0124",
  "email": "jane.smith@email.com",
  "address": "123 Main St",
  "blood_type": "O+",
  "allergies": "Penicillin",
  "emergency_contact_name": "John Smith",
  "emergency_contact_phone": "555-0125"
}
```

### List Patients
```http
GET /patients
```

### Get Patient
```http
GET /patients/{patient_id}
```

## Department Management

### Create Department
```http
POST /departments
Content-Type: application/json

{
  "name": "Cardiology",
  "description": "Heart specialists",
  "floor_number": 3,
  "phone": "555-0200",
  "email": "cardiology@hospital.com"
}
```

### List Departments
```http
GET /departments
```

### Get Department
```http
GET /departments/{department_id}
```

## Bed Management

### Create Bed
```http
POST /beds
Content-Type: application/json

{
  "bed_number": "101A",
  "room_id": "uuid-here",
  "bed_type": "Standard",
  "status": "available"
}
```

### List Beds
```http
GET /beds
GET /beds?status=available
GET /beds?status=occupied
```

### Assign Bed to Patient
```http
POST /beds/{bed_id}/assign
Content-Type: application/json

{
  "patient_id": "uuid-here",
  "admission_date": "2025-08-02T10:00:00"
}
```

### Discharge Patient from Bed
```http
POST /beds/{bed_id}/discharge
Content-Type: application/json

{
  "discharge_date": "2025-08-05T15:30:00"
}
```

## Staff Management

### Create Staff
```http
POST /tools/create_staff
Content-Type: application/json

{
  "user_id": "uuid-here",
  "employee_id": "EMP001",
  "department_id": "uuid-here",
  "position": "Nurse",
  "specialization": "ICU",
  "license_number": "RN123456",
  "hire_date": "2025-01-01",
  "salary": 65000.00,
  "shift_pattern": "Day",
  "status": "active"
}
```

### List Staff
```http
GET /staff
GET /staff?department_id=uuid-here
GET /staff?status=active
GET /staff?department_id=uuid-here&status=active
```

## Equipment Management

### Create Equipment Category
```http
POST /tools/create_equipment_category
Content-Type: application/json

{
  "name": "Medical Devices",
  "description": "Various medical equipment"
}
```

### Create Equipment
```http
POST /tools/create_equipment
Content-Type: application/json

{
  "equipment_id": "EQ001",
  "name": "X-Ray Machine",
  "category_id": "uuid-here",
  "model": "XR-2000",
  "manufacturer": "MedTech Inc",
  "serial_number": "MT2000-001",
  "purchase_date": "2025-01-15",
  "warranty_expiry": "2030-01-15",
  "location": "Radiology Room 1",
  "department_id": "uuid-here",
  "cost": 150000.00
}
```

### List Equipment
```http
GET /equipment
GET /equipment?status=operational
GET /equipment?department_id=uuid-here
```

### Update Equipment Status
```http
POST /tools/update_equipment_status
Content-Type: application/json

{
  "equipment_id": "uuid-here",
  "status": "maintenance",
  "notes": "Scheduled maintenance"
}
```

## Supply Management

### Create Supply Category
```http
POST /tools/create_supply_category
Content-Type: application/json

{
  "name": "Medications",
  "description": "Various pharmaceutical supplies"
}
```

### Create Supply
```http
POST /tools/create_supply
Content-Type: application/json

{
  "item_code": "MED001",
  "name": "Aspirin 100mg",
  "category_id": "uuid-here",
  "description": "Pain relief medication",
  "unit_of_measure": "tablets",
  "minimum_stock_level": 50,
  "maximum_stock_level": 500,
  "current_stock": 200,
  "unit_cost": 0.25,
  "supplier": "PharmaCorp",
  "expiry_date": "2026-12-31",
  "location": "Pharmacy Storage A"
}
```

### List Supplies
```http
GET /supplies
GET /supplies?low_stock_only=true
```

### Update Supply Stock
```http
POST /tools/update_supply_stock
Content-Type: application/json

{
  "supply_id": "uuid-here",
  "quantity_change": 100,
  "transaction_type": "in",
  "performed_by": "user-uuid-here",
  "unit_cost": 0.25,
  "reference_number": "PO-2025-001",
  "notes": "Weekly delivery"
}
```

## Appointment Management

### Create Appointment
```http
POST /tools/create_appointment
Content-Type: application/json

{
  "patient_id": "uuid-here",
  "doctor_id": "uuid-here",
  "department_id": "uuid-here",
  "appointment_date": "2025-08-03T14:30:00",
  "duration_minutes": 30,
  "reason": "Regular checkup",
  "notes": "Patient has history of hypertension"
}
```

### List Appointments
```http
GET /appointments
GET /appointments?doctor_id=uuid-here
GET /appointments?patient_id=uuid-here
GET /appointments?date=2025-08-03
```

## Logging

### Log Agent Interaction
```http
POST /tools/log_agent_interaction
Content-Type: application/json

{
  "agent_type": "bed_management",
  "user_id": "uuid-here",
  "query": "Find available beds in ICU",
  "response": "Found 3 available beds",
  "action_taken": "list_beds",
  "confidence_score": 0.95,
  "execution_time_ms": 150
}
```

## Room Management

### Create Room
```http
POST /tools/create_room
Content-Type: application/json

{
  "room_number": "101",
  "department_id": "uuid-here",
  "room_type": "Standard",
  "floor_number": 1,
  "capacity": 2
}
```

### List Rooms
```http
GET /rooms
```

## Legacy Support

### Create Legacy User
```http
POST /tools/create_legacy_user
Content-Type: application/json

{
  "name": "Old System User",
  "email": "legacy@hospital.com",
  "address": "123 Legacy Lane",
  "phone": "555-9999"
}
```

### List Legacy Users
```http
GET /tools/list_legacy_users
```

## Error Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error (server/database error)
- `503` - Service Unavailable (bridge not initialized)

## Data Types

### UUIDs
All IDs are UUIDs in string format: `"123e4567-e89b-12d3-a456-426614174000"`

### Dates
- Date: `"2025-08-02"` (ISO format)
- DateTime: `"2025-08-02T14:30:00"` (ISO format)

### Status Values
- Bed Status: `"available"`, `"occupied"`, `"maintenance"`, `"out_of_order"`
- Staff Status: `"active"`, `"inactive"`, `"on_leave"`
- Equipment Status: `"operational"`, `"maintenance"`, `"out_of_order"`, `"retired"`

### Roles
- User Roles: `"admin"`, `"doctor"`, `"nurse"`, `"receptionist"`, `"technician"`

## Rate Limiting
Currently no rate limiting (development mode).

## CORS
Currently allows all origins (development mode).

For production deployment, configure appropriate CORS settings and add authentication.
