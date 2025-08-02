# How to Use Manual CRUD Operations

## 🎯 Option 1: Use the New Manual CRUD Client (Recommended)

### Run the Manual CRUD Client:
```bash
cd c:\Users\Arivanan\hospital-management-system\backend-python
python manual_crud_client.py
```

This gives you a **completely manual interface** where you can:
- ✅ **Create real users** with custom data
- ✅ **Create real patients** with custom data  
- ✅ **Create real departments** with custom data
- ✅ **Create real equipment** with custom data
- ✅ **Create real supplies** with custom data
- ✅ **Update existing records** with real data
- ✅ **List all data** to see what you've created

### Example Manual User Creation:
```
👤 === CREATE NEW USER ===
Username: dr_smith
Email: dr.smith@hospital.com
Password Hash: secure_hash_123
Role (admin/doctor/nurse/staff): doctor
First Name: John
Last Name: Smith
Phone: 555-1234-5678
✅ User created successfully!
```

### Example Manual Patient Creation:
```
🤒 === CREATE NEW PATIENT ===
Patient Number: P12345
First Name: Sarah
Last Name: Johnson
Date of Birth (YYYY-MM-DD): 1985-03-15
Gender (male/female/other): female
Phone: 555-9876-5432
Email: sarah.johnson@email.com
Address: 123 Main Street, Anytown, ST 12345
Blood Type: A+
Allergies: Penicillin
Medical History: None
Emergency Contact Name: Mike Johnson
Emergency Contact Phone: 555-1111-2222
✅ Patient created successfully!
```

## 🎯 Option 2: Modify Existing client.py Demos

If you want to keep using the original client.py but with real data, here's how:

### For Interactive Mode Real Data Entry:

1. **Run the client:**
   ```bash
   python client.py
   # Choose option 2 (Interactive Mode)
   ```

2. **Choose option 13 (Intelligent Patient Admission):**
   This will prompt you for real patient data:
   ```
   👤 Enter Patient Information:
   First Name: [Enter real name]
   Last Name: [Enter real name]
   Date of Birth (YYYY-MM-DD): [Enter real date]
   Gender (male/female/other): [Enter real gender]
   Phone: [Enter real phone]
   Email: [Enter real email]
   ```

## 🎯 Option 3: Direct Tool Calls with Real Data

You can also call the tools directly with your real data:

```bash
python -c "
import asyncio
from client import HospitalManagementClient

async def create_real_user():
    client = HospitalManagementClient()
    await client.connect()
    
    # Create a real user with your data
    result = await client._safe_call_tool('create_user', {
        'username': 'your_username',
        'email': 'your.email@hospital.com',
        'password_hash': 'your_secure_hash',
        'role': 'doctor',  # or nurse, admin, staff
        'first_name': 'Your',
        'last_name': 'Name',
        'phone': '555-YOUR-PHONE'
    })
    
    print('Create User Result:', result)
    await client.disconnect()

asyncio.run(create_real_user())
"
```

## 🚀 Quick Start with Manual CRUD Client

### Step 1: Run the Manual Client
```bash
cd c:\Users\Arivanan\hospital-management-system\backend-python
python manual_crud_client.py
```

### Step 2: Create Your Hospital Structure
1. **Start with option 3** - Create Department (create your real departments)
2. **Then option 1** - Create User (create your real staff)
3. **Then option 2** - Create Patient (create your real patients)
4. **Then option 4** - Create Equipment (create your real equipment)
5. **Then option 5** - Create Supply (create your real supplies)

### Step 3: Verify Your Data
- **Use option 7** - List All Data to see everything you've created

## 📊 Example Manual CRUD Session

```bash
PS C:\Users\Arivanan\hospital-management-system\backend-python> python manual_crud_client.py

🏥 HOSPITAL MANAGEMENT SYSTEM - MANUAL CRUD MODE
============================================================
✅ Connected to Hospital Management MCP Server

==================================================
📋 MANUAL CRUD OPERATIONS MENU
==================================================

=== CREATE OPERATIONS ===
1. Create User
2. Create Patient
3. Create Department
4. Create Equipment
5. Create Supply

=== UPDATE OPERATIONS ===
6. Update User

=== READ OPERATIONS ===
7. List All Data

=== OTHER ===
0. Exit

Enter your choice (0-7): 1

👤 === CREATE NEW USER ===
Username: dr_wilson
Email: dr.wilson@myrhospital.com
Password Hash: secure123
Role (admin/doctor/nurse/staff): doctor
First Name: Emily
Last Name: Wilson
Phone: 555-123-4567
✅ User created successfully!
   User ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
   Username: dr_wilson
```

## 🔧 Benefits of Manual CRUD Client

1. **Real Data Entry**: No more demo/sample data
2. **Interactive Forms**: Guided input for all fields
3. **Data Validation**: Ensures proper formats (dates, emails, etc.)
4. **Foreign Key Handling**: Shows available options for relationships
5. **Error Handling**: Clear error messages for failed operations
6. **Complete CRUD**: Create, Read, Update operations all supported
7. **Real-time Feedback**: Immediate success/failure confirmation

## 🎯 Which Option Should You Use?

### Use **manual_crud_client.py** if:
- ✅ You want complete control over data entry
- ✅ You want to create real hospital data
- ✅ You want guided forms for input
- ✅ You want a clean, focused CRUD interface

### Use **client.py Interactive Mode** if:
- ✅ You want to see the AI features
- ✅ You want to test the agentic capabilities
- ✅ You occasionally need real data entry

**Recommendation**: Start with `manual_crud_client.py` to build your real hospital data, then use `client.py` for AI features!
