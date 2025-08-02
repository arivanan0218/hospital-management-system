# Manual CRUD Operations Client
# Interactive client for real data entry instead of demo data

import asyncio
import json
import traceback
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from datetime import datetime
import uuid


class ManualCRUDClient:
    def __init__(self):
        self.session = None

    async def connect(self):
        """Connect to the MCP server."""
        try:
            print("🔌 Connecting to server...")
            server_params = StdioServerParameters(
                command="python",
                args=["comprehensive_server.py"],
                env=None
            )
            
            self.stdio_context = stdio_client(server_params)
            read, write = await self.stdio_context.__aenter__()
            self.session = ClientSession(read, write)
            
            print("🔗 Initializing session...")
            await self.session.initialize()
            print("✅ Connected to Hospital Management MCP Server")
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            raise

    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.session:
            await self.session.close()
        if hasattr(self, 'stdio_context'):
            await self.stdio_context.__aexit__(None, None, None)
        print("📡 Disconnected from server")

    async def _safe_call_tool(self, tool_name, params):
        """Safely call MCP tool with error handling."""
        try:
            result = await self.session.call_tool(tool_name, params)
            return json.loads(result.content[0].text)
        except Exception as e:
            print(f"⚠️ Tool {tool_name} failed: {e}")
            return {"success": False, "message": str(e)}

    def get_user_input(self, prompt, required=True, default=None):
        """Get user input with validation."""
        while True:
            value = input(f"{prompt}: ").strip()
            if value:
                return value
            elif default:
                return default
            elif not required:
                return None
            else:
                print("This field is required. Please enter a value.")

    def get_date_input(self, prompt):
        """Get date input in YYYY-MM-DD format."""
        while True:
            date_str = input(f"{prompt} (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                return date_str
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD")

    def get_number_input(self, prompt, required=True):
        """Get numeric input."""
        while True:
            value = input(f"{prompt}: ").strip()
            if not value and not required:
                return None
            try:
                return float(value) if '.' in value else int(value)
            except ValueError:
                print("Please enter a valid number.")

    # === MANUAL CREATE OPERATIONS ===

    async def manual_create_user(self):
        """Create user with manual input."""
        print("\n👤 === CREATE NEW USER ===")
        
        username = self.get_user_input("Username")
        email = self.get_user_input("Email")
        password_hash = self.get_user_input("Password Hash")
        role = self.get_user_input("Role (admin/doctor/nurse/staff)")
        first_name = self.get_user_input("First Name")
        last_name = self.get_user_input("Last Name")
        phone = self.get_user_input("Phone", required=False)
        
        user_data = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone
        }
        
        result = await self._safe_call_tool("create_user", user_data)
        
        if result.get("success"):
            print(f"✅ User created successfully!")
            print(f"   User ID: {result['data']['id']}")
            print(f"   Username: {result['data']['username']}")
        else:
            print(f"❌ Failed to create user: {result.get('message', 'Unknown error')}")
        
        return result

    async def manual_create_patient(self):
        """Create patient with manual input."""
        print("\n🤒 === CREATE NEW PATIENT ===")
        
        patient_number = self.get_user_input("Patient Number", default=f"P{str(uuid.uuid4().hex[:8]).upper()}")
        first_name = self.get_user_input("First Name")
        last_name = self.get_user_input("Last Name")
        date_of_birth = self.get_date_input("Date of Birth")
        gender = self.get_user_input("Gender (male/female/other)")
        phone = self.get_user_input("Phone", required=False)
        email = self.get_user_input("Email", required=False)
        address = self.get_user_input("Address", required=False)
        blood_type = self.get_user_input("Blood Type", required=False)
        allergies = self.get_user_input("Allergies", required=False)
        medical_history = self.get_user_input("Medical History", required=False)
        emergency_contact_name = self.get_user_input("Emergency Contact Name", required=False)
        emergency_contact_phone = self.get_user_input("Emergency Contact Phone", required=False)
        
        patient_data = {
            "patient_number": patient_number,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "phone": phone,
            "email": email,
            "address": address,
            "blood_type": blood_type,
            "allergies": allergies,
            "medical_history": medical_history,
            "emergency_contact_name": emergency_contact_name,
            "emergency_contact_phone": emergency_contact_phone
        }
        
        result = await self._safe_call_tool("create_patient", patient_data)
        
        if result.get("success"):
            print(f"✅ Patient created successfully!")
            print(f"   Patient ID: {result['data']['id']}")
            print(f"   Patient Number: {result['data']['patient_number']}")
            print(f"   Name: {result['data']['first_name']} {result['data']['last_name']}")
        else:
            print(f"❌ Failed to create patient: {result.get('message', 'Unknown error')}")
        
        return result

    async def manual_create_department(self):
        """Create department with manual input."""
        print("\n🏢 === CREATE NEW DEPARTMENT ===")
        
        name = self.get_user_input("Department Name")
        description = self.get_user_input("Description", required=False)
        floor_number = self.get_number_input("Floor Number", required=False)
        phone = self.get_user_input("Phone", required=False)
        email = self.get_user_input("Email", required=False)
        
        # Show available users for head doctor selection
        users_result = await self._safe_call_tool("list_users", {})
        if users_result.get("users"):
            print("\nAvailable users for Head Doctor:")
            for i, user in enumerate(users_result["users"], 1):
                print(f"   {i}. {user['first_name']} {user['last_name']} ({user['role']}) - ID: {user['id']}")
            
            head_doctor_choice = input("Select head doctor number (or press Enter to skip): ").strip()
            head_doctor_id = None
            if head_doctor_choice.isdigit():
                choice_idx = int(head_doctor_choice) - 1
                if 0 <= choice_idx < len(users_result["users"]):
                    head_doctor_id = users_result["users"][choice_idx]["id"]
        else:
            head_doctor_id = None
        
        dept_data = {
            "name": name,
            "description": description,
            "floor_number": floor_number,
            "phone": phone,
            "email": email,
            "head_doctor_id": head_doctor_id
        }
        
        result = await self._safe_call_tool("create_department", dept_data)
        
        if result.get("success"):
            print(f"✅ Department created successfully!")
            print(f"   Department ID: {result['data']['id']}")
            print(f"   Name: {result['data']['name']}")
        else:
            print(f"❌ Failed to create department: {result.get('message', 'Unknown error')}")
        
        return result

    async def manual_create_equipment(self):
        """Create equipment with manual input."""
        print("\n🔧 === CREATE NEW EQUIPMENT ===")
        
        # First show available categories or create new one
        categories_result = await self._safe_call_tool("list_equipment_categories", {})
        category_id = None
        
        if categories_result.get("categories"):
            print("\nAvailable Equipment Categories:")
            for i, cat in enumerate(categories_result["categories"], 1):
                print(f"   {i}. {cat['name']} - {cat.get('description', 'No description')}")
            
            create_new = input("\nCreate new category? (y/n): ").strip().lower()
            if create_new == 'y':
                cat_name = self.get_user_input("Category Name")
                cat_desc = self.get_user_input("Category Description", required=False)
                cat_result = await self._safe_call_tool("create_equipment_category", {
                    "name": cat_name,
                    "description": cat_desc
                })
                if cat_result.get("success"):
                    category_id = cat_result["data"]["id"]
                    print(f"✅ Category created: {cat_name}")
            else:
                cat_choice = input("Select category number: ").strip()
                if cat_choice.isdigit():
                    choice_idx = int(cat_choice) - 1
                    if 0 <= choice_idx < len(categories_result["categories"]):
                        category_id = categories_result["categories"][choice_idx]["id"]
        else:
            # Create first category
            print("No categories found. Creating first category...")
            cat_name = self.get_user_input("Category Name")
            cat_desc = self.get_user_input("Category Description", required=False)
            cat_result = await self._safe_call_tool("create_equipment_category", {
                "name": cat_name,
                "description": cat_desc
            })
            if cat_result.get("success"):
                category_id = cat_result["data"]["id"]
        
        if not category_id:
            print("❌ No category selected. Cannot create equipment.")
            return
        
        # Get equipment details
        equipment_id = self.get_user_input("Equipment ID", default=f"EQ{str(uuid.uuid4().hex[:8]).upper()}")
        name = self.get_user_input("Equipment Name")
        model = self.get_user_input("Model", required=False)
        manufacturer = self.get_user_input("Manufacturer", required=False)
        serial_number = self.get_user_input("Serial Number", required=False)
        location = self.get_user_input("Location", required=False)
        cost = self.get_number_input("Cost", required=False)
        purchase_date = self.get_date_input("Purchase Date") if input("Enter purchase date? (y/n): ").strip().lower() == 'y' else None
        warranty_expiry = self.get_date_input("Warranty Expiry Date") if input("Enter warranty expiry? (y/n): ").strip().lower() == 'y' else None
        
        equipment_data = {
            "equipment_id": equipment_id,
            "name": name,
            "category_id": category_id,
            "model": model,
            "manufacturer": manufacturer,
            "serial_number": serial_number,
            "location": location,
            "cost": cost,
            "purchase_date": purchase_date,
            "warranty_expiry": warranty_expiry
        }
        
        result = await self._safe_call_tool("create_equipment", equipment_data)
        
        if result.get("success"):
            print(f"✅ Equipment created successfully!")
            print(f"   Equipment ID: {result['data']['id']}")
            print(f"   Name: {result['data']['name']}")
        else:
            print(f"❌ Failed to create equipment: {result.get('message', 'Unknown error')}")
        
        return result

    async def manual_create_supply(self):
        """Create supply with manual input."""
        print("\n📦 === CREATE NEW SUPPLY ===")
        
        # Handle supply categories similar to equipment
        categories_result = await self._safe_call_tool("list_supply_categories", {})
        category_id = None
        
        if categories_result.get("categories"):
            print("\nAvailable Supply Categories:")
            for i, cat in enumerate(categories_result["categories"], 1):
                print(f"   {i}. {cat['name']} - {cat.get('description', 'No description')}")
            
            create_new = input("\nCreate new category? (y/n): ").strip().lower()
            if create_new == 'y':
                cat_name = self.get_user_input("Category Name")
                cat_desc = self.get_user_input("Category Description", required=False)
                cat_result = await self._safe_call_tool("create_supply_category", {
                    "name": cat_name,
                    "description": cat_desc
                })
                if cat_result.get("success"):
                    category_id = cat_result["data"]["id"]
                    print(f"✅ Category created: {cat_name}")
            else:
                cat_choice = input("Select category number: ").strip()
                if cat_choice.isdigit():
                    choice_idx = int(cat_choice) - 1
                    if 0 <= choice_idx < len(categories_result["categories"]):
                        category_id = categories_result["categories"][choice_idx]["id"]
        else:
            print("No categories found. Creating first category...")
            cat_name = self.get_user_input("Category Name")
            cat_desc = self.get_user_input("Category Description", required=False)
            cat_result = await self._safe_call_tool("create_supply_category", {
                "name": cat_name,
                "description": cat_desc
            })
            if cat_result.get("success"):
                category_id = cat_result["data"]["id"]
        
        if not category_id:
            print("❌ No category selected. Cannot create supply.")
            return
        
        # Get supply details
        item_code = self.get_user_input("Item Code", default=f"SUP{str(uuid.uuid4().hex[:8]).upper()}")
        name = self.get_user_input("Supply Name")
        unit_of_measure = self.get_user_input("Unit of Measure (boxes, pieces, bottles, etc.)")
        description = self.get_user_input("Description", required=False)
        current_stock = self.get_number_input("Current Stock", required=False) or 0
        minimum_stock_level = self.get_number_input("Minimum Stock Level", required=False) or 0
        maximum_stock_level = self.get_number_input("Maximum Stock Level", required=False)
        unit_cost = self.get_number_input("Unit Cost", required=False)
        supplier = self.get_user_input("Supplier", required=False)
        location = self.get_user_input("Storage Location", required=False)
        expiry_date = self.get_date_input("Expiry Date") if input("Enter expiry date? (y/n): ").strip().lower() == 'y' else None
        
        supply_data = {
            "item_code": item_code,
            "name": name,
            "category_id": category_id,
            "unit_of_measure": unit_of_measure,
            "description": description,
            "current_stock": current_stock,
            "minimum_stock_level": minimum_stock_level,
            "maximum_stock_level": maximum_stock_level,
            "unit_cost": unit_cost,
            "supplier": supplier,
            "location": location,
            "expiry_date": expiry_date
        }
        
        result = await self._safe_call_tool("create_supply", supply_data)
        
        if result.get("success"):
            print(f"✅ Supply created successfully!")
            print(f"   Supply ID: {result['data']['id']}")
            print(f"   Name: {result['data']['name']}")
            print(f"   Current Stock: {result['data']['current_stock']} {result['data']['unit_of_measure']}")
        else:
            print(f"❌ Failed to create supply: {result.get('message', 'Unknown error')}")
        
        return result

    # === MANUAL UPDATE OPERATIONS ===

    async def manual_update_user(self):
        """Update user with manual input."""
        print("\n✏️ === UPDATE USER ===")
        
        # Show available users
        users_result = await self._safe_call_tool("list_users", {})
        if not users_result.get("users"):
            print("❌ No users found.")
            return
        
        print("\nAvailable Users:")
        for i, user in enumerate(users_result["users"], 1):
            print(f"   {i}. {user['first_name']} {user['last_name']} ({user['username']}) - {user['email']}")
        
        user_choice = input("Select user number to update: ").strip()
        if not user_choice.isdigit():
            print("❌ Invalid selection.")
            return
        
        choice_idx = int(user_choice) - 1
        if not (0 <= choice_idx < len(users_result["users"])):
            print("❌ Invalid selection.")
            return
        
        user = users_result["users"][choice_idx]
        user_id = user["id"]
        
        print(f"\nUpdating user: {user['first_name']} {user['last_name']}")
        print("(Press Enter to keep current value)")
        
        # Get new values
        new_username = input(f"Username (current: {user['username']}): ").strip()
        new_email = input(f"Email (current: {user['email']}): ").strip()
        new_first_name = input(f"First Name (current: {user['first_name']}): ").strip()
        new_last_name = input(f"Last Name (current: {user['last_name']}): ").strip()
        new_phone = input(f"Phone (current: {user.get('phone', 'None')}): ").strip()
        new_role = input(f"Role (current: {user['role']}): ").strip()
        
        # Build update data with only changed fields
        update_data = {"user_id": user_id}
        if new_username: update_data["username"] = new_username
        if new_email: update_data["email"] = new_email
        if new_first_name: update_data["first_name"] = new_first_name
        if new_last_name: update_data["last_name"] = new_last_name
        if new_phone: update_data["phone"] = new_phone
        if new_role: update_data["role"] = new_role
        
        result = await self._safe_call_tool("update_user", update_data)
        
        if result.get("success"):
            print(f"✅ User updated successfully!")
        else:
            print(f"❌ Failed to update user: {result.get('message', 'Unknown error')}")
        
        return result

    # === MANUAL READ OPERATIONS ===

    async def manual_list_all(self):
        """List all entities."""
        print("\n📖 === LIST ALL DATA ===")
        
        entities = [
            ("users", "Users"),
            ("departments", "Departments"),
            ("patients", "Patients"),
            ("beds", "Beds"),
            ("equipment", "Equipment"),
            ("supplies", "Supplies"),
            ("appointments", "Appointments")
        ]
        
        for entity_key, entity_name in entities:
            print(f"\n{entity_name}:")
            result = await self._safe_call_tool(f"list_{entity_key}", {})
            
            if result.get(entity_key):
                for item in result[entity_key]:
                    if entity_key == "users":
                        print(f"   • {item['first_name']} {item['last_name']} ({item['username']}) - {item['role']}")
                    elif entity_key == "patients":
                        print(f"   • {item['patient_number']}: {item['first_name']} {item['last_name']} - {item.get('phone', 'No phone')}")
                    elif entity_key == "departments":
                        print(f"   • {item['name']} - Floor {item.get('floor_number', 'N/A')}")
                    elif entity_key == "beds":
                        print(f"   • Bed {item['bed_number']} - Status: {item.get('status', 'Unknown')}")
                    elif entity_key == "equipment":
                        print(f"   • {item['name']} ({item.get('model', 'No model')}) - Status: {item.get('status', 'Unknown')}")
                    elif entity_key == "supplies":
                        print(f"   • {item['name']} - Stock: {item.get('current_stock', 0)} {item.get('unit_of_measure', 'units')}")
                    elif entity_key == "appointments":
                        print(f"   • {item.get('appointment_date', 'No date')} - {item.get('reason', 'No reason')}")
            else:
                print(f"   No {entity_name.lower()} found.")

    async def run_manual_crud_interface(self):
        """Run the manual CRUD interface."""
        print("🏥 HOSPITAL MANAGEMENT SYSTEM - MANUAL CRUD MODE")
        print("=" * 60)
        
        server_params = StdioServerParameters(
            command="python",
            args=["comprehensive_server.py"],
            env=None
        )
        
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.session = session
                    await session.initialize()
                    print("✅ Connected to Hospital Management MCP Server")
                    
                    while True:
                        print("\n" + "="*50)
                        print("📋 MANUAL CRUD OPERATIONS MENU")
                        print("="*50)
                        print("\n=== CREATE OPERATIONS ===")
                        print("1. Create User")
                        print("2. Create Patient")
                        print("3. Create Department")
                        print("4. Create Equipment")
                        print("5. Create Supply")
                        print("\n=== UPDATE OPERATIONS ===")
                        print("6. Update User")
                        print("\n=== READ OPERATIONS ===")
                        print("7. List All Data")
                        print("\n=== OTHER ===")
                        print("0. Exit")
                        
                        try:
                            choice = input("\nEnter your choice (0-7): ").strip()
                            
                            if choice == "0":
                                break
                            elif choice == "1":
                                await self.manual_create_user()
                            elif choice == "2":
                                await self.manual_create_patient()
                            elif choice == "3":
                                await self.manual_create_department()
                            elif choice == "4":
                                await self.manual_create_equipment()
                            elif choice == "5":
                                await self.manual_create_supply()
                            elif choice == "6":
                                await self.manual_update_user()
                            elif choice == "7":
                                await self.manual_list_all()
                            else:
                                print("Invalid choice. Please enter 0-7.")
                                
                        except KeyboardInterrupt:
                            print("\n\nExiting...")
                            break
                        except Exception as e:
                            print(f"Error: {e}")
                            traceback.print_exc()
                    
                    print("📡 Disconnecting from server...")
                    
        except Exception as e:
            print(f"❌ Manual CRUD mode failed: {e}")
            traceback.print_exc()


async def main():
    """Main function to run the manual CRUD client."""
    client = ManualCRUDClient()
    await client.run_manual_crud_interface()


if __name__ == "__main__":
    asyncio.run(main())
