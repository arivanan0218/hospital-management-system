"""
Enhanced Patient Admission Form Integration with LangGraph
Demo script to show the complete admission workflow integration
"""

import requests
import json

def test_enhanced_patient_admission_workflow():
    """Test the enhanced patient admission workflow with LangGraph integration"""
    
    print("🏥 ENHANCED PATIENT ADMISSION WORKFLOW DEMO")
    print("Frontend Form → Backend Processing → LangGraph Workflow")
    print("=" * 70)
    
    # Example of what your frontend form sends
    patient_form_data = {
        "first_name": "Sarah",
        "last_name": "Johnson", 
        "date_of_birth": "1985-07-15",
        "gender": "female",
        "phone": "555-0987",
        "email": "sarah.johnson@email.com",
        "address": "123 Main St, City, State 12345",
        "emergency_contact_name": "John Johnson",
        "emergency_contact_phone": "555-0988",
        "blood_type": "O+",
        "allergies": "Penicillin",
        "medical_history": "Previous appendectomy in 2020, mild hypertension"
    }
    
    base_url = "http://127.0.0.1:8000/tools/call"
    
    # Step 1: Standard Patient Creation (what your form currently does)
    print("\n📝 STEP 1: STANDARD PATIENT CREATION (Current Form)")
    print("-" * 50)
    
    create_patient_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "create_patient",
            "arguments": patient_form_data
        }
    }
    
    try:
        response = requests.post(base_url, json=create_patient_payload, timeout=15)
        if response.status_code == 200:
            result = response.json()
            content = result.get("result", {}).get("content", [])
            if content:
                data = json.loads(content[0].get("text", "{}"))
                if data.get("success"):
                    patient_data = data.get("data", {})
                    patient_id = patient_data.get("patient_number") or patient_data.get("id")
                    print(f"✅ Patient Created Successfully!")
                    print(f"   Patient ID: {patient_id}")
                    print(f"   Name: {patient_data.get('first_name')} {patient_data.get('last_name')}")
                    print(f"   Status: Patient record in database")
                else:
                    print(f"❌ Patient creation failed: {data.get('message')}")
                    return
            else:
                print("❌ No response content from patient creation")
                return
    except Exception as e:
        print(f"❌ Patient creation error: {e}")
        return
    
    # Step 2: Enhanced LangGraph Admission Workflow
    print("\n🧠 STEP 2: LANGRAPH ENHANCED ADMISSION WORKFLOW")
    print("-" * 50)
    print("This would be triggered automatically after form submission...")
    
    langraph_payload = {
        "jsonrpc": "2.0", 
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "execute_langraph_patient_admission",
            "arguments": {
                "patient_data": patient_form_data
            }
        }
    }
    
    try:
        response = requests.post(base_url, json=langraph_payload, timeout=20)
        if response.status_code == 200:
            result = response.json()
            content = result.get("result", {}).get("content", [])
            if content:
                data = json.loads(content[0].get("text", "{}"))
                if data.get("success"):
                    workflow_result = data.get("result", {})
                    print(f"✅ LangGraph Workflow Executed!")
                    print(f"   Workflow Status: {workflow_result.get('status', 'Unknown')}")
                    
                    if workflow_result.get("bed_id"):
                        print(f"   🛏️ Bed Assigned: {workflow_result.get('bed_id')}")
                    
                    if workflow_result.get("staff_assignments"):
                        print(f"   👥 Staff Assignments: {len(workflow_result.get('staff_assignments', []))}")
                    
                    if workflow_result.get("equipment_assignments"):
                        print(f"   ⚙️ Equipment Assigned: {len(workflow_result.get('equipment_assignments', []))}")
                    
                    steps = workflow_result.get("steps_completed", [])
                    print(f"   ✅ Completed Steps: {', '.join(steps)}")
                    
                    messages = workflow_result.get("messages", [])
                    if messages:
                        print("   📋 Workflow Messages:")
                        for msg in messages[-3:]:  # Show last 3 messages
                            print(f"      • {msg}")
                            
                else:
                    print(f"⚠️ LangGraph workflow completed with issues:")
                    print(f"   Message: {data.get('message', 'Unknown issue')}")
                    workflow_result = data.get("result", {})
                    if workflow_result:
                        print(f"   Status: {workflow_result.get('status', 'Unknown')}")
                        if workflow_result.get("error"):
                            print(f"   Error: {workflow_result.get('error')}")
    except Exception as e:
        print(f"ℹ️ LangGraph workflow: {str(e)[:100]}...")
    
    # Step 3: Show Enhanced Frontend Integration
    print("\n🌐 STEP 3: ENHANCED FRONTEND INTEGRATION SUGGESTIONS")
    print("-" * 50)
    
    print("To integrate LangGraph with your admission form, you could:")
    print()
    print("1️⃣ **Automatic LangGraph Trigger:**")
    print("   After successful patient creation, automatically trigger:")
    print("   `execute_langraph_patient_admission(patient_data)`")
    print()
    print("2️⃣ **Enhanced Success Response:**")
    print("   Instead of just showing patient details, show:")
    print("   • ✅ Patient created")
    print("   • 🛏️ Bed assignment in progress...")
    print("   • 👥 Staff assignment in progress...")
    print("   • ⚙️ Equipment assignment in progress...")
    print()
    print("3️⃣ **Real-time Workflow Updates:**")
    print("   Stream workflow progress to frontend:")
    print("   • Step 1: Patient validation ✅")
    print("   • Step 2: Bed assignment ✅")
    print("   • Step 3: Staff assignment ✅")
    print("   • Step 4: Equipment setup ✅")
    print()
    print("4️⃣ **Smart Post-Admission Actions:**")
    print("   After admission, suggest next actions:")
    print("   • 'Assign bed 101A to patient Sarah Johnson'")
    print("   • 'Assign Dr. Smith to patient Sarah Johnson'")
    
    # Step 4: Show Current Status
    print("\n📊 STEP 4: CURRENT SYSTEM STATUS")
    print("-" * 50)
    
    try:
        health_response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if health_response.status_code == 200:
            health = health_response.json()
            print("✅ Current System Status:")
            print(f"   • Backend: {health.get('status', 'Unknown')}")
            print(f"   • Agents: {health.get('agents_count', 0)} active")
            print(f"   • Tools: {health.get('tools_count', 0)} available")
            print(f"   • Database: {health.get('database', 'Unknown')}")
    except Exception as e:
        print(f"ℹ️ System status check: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 ENHANCEMENT RECOMMENDATIONS FOR YOUR FORM")
    print("=" * 70)
    
    print("Your PatientAdmissionForm.jsx is excellent! Here are suggestions:")
    print()
    print("✅ **Already Implemented:**")
    print("   • Comprehensive patient data collection")
    print("   • Clean form validation")
    print("   • Proper error handling")
    print("   • Success/failure feedback")
    print()
    print("🚀 **Potential Enhancements:**")
    print("   1. Add LangGraph workflow trigger after patient creation")
    print("   2. Show real-time admission progress")
    print("   3. Display suggested next steps (bed/staff assignment)")
    print("   4. Add workflow status indicator")
    print("   5. Stream LangGraph workflow updates")
    print()
    print("💡 **Implementation Approach:**")
    print("   In handleSubmit() after successful patient creation:")
    print("   ```javascript")
    print("   // Trigger LangGraph admission workflow")
    print("   const workflowResponse = await aiMcpServiceRef.current.callToolDirectly(")
    print("     'execute_langraph_patient_admission', { patient_data: formData }")
    print("   ```")
    
    print(f"\n🌐 **Your Form Access:**")
    print(f"   • Frontend: http://localhost:5173")
    print(f"   • Backend: http://127.0.0.1:8000")
    print(f"   • Form triggers when you say 'admit patient' in chat")

if __name__ == "__main__":
    test_enhanced_patient_admission_workflow()
