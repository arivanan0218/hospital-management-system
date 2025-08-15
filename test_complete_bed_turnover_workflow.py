#!/usr/bin/env python3
"""
Complete Hospital Bed Turnover Workflow Test
Tests the full workflow from patient admission to bed turnover and reassignment.
"""

import requests
import json
import time
import uuid
from datetime import datetime

class HospitalWorkflowTest:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_data = {}
        
    def call_tool(self, tool_name, arguments=None):
        """Call an MCP tool via the backend server."""
        if arguments is None:
            arguments = {}
            
        payload = {
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            print(f"\n🔧 Calling tool: {tool_name}")
            print(f"Arguments: {json.dumps(arguments, indent=2)}")
            
            response = self.session.post(
                f"{self.base_url}/mcp/tools/call", 
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('content'):
                    content = result['content'][0]['text']
                    parsed = json.loads(content)
                    print(f"✅ Success: {parsed.get('message', 'Tool executed successfully')}")
                    return parsed
                else:
                    print(f"❌ No content in response: {result}")
                    return {"success": False, "message": "No content returned"}
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                return {"success": False, "message": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Error calling tool {tool_name}: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def test_server_health(self):
        """Test if the server is running and responsive."""
        print("\n" + "="*60)
        print("🏥 HOSPITAL MANAGEMENT SYSTEM - WORKFLOW TEST")
        print("="*60)
        
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                print("✅ Server is running and healthy")
                return True
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to server: {str(e)}")
            return False
    
    def step_1_create_patient(self):
        """Step 1: Create a new patient."""
        print("\n" + "-"*50)
        print("STEP 1: CREATE NEW PATIENT")
        print("-"*50)
        
        patient_data = {
            "first_name": "John",
            "last_name": "Workflow",
            "date_of_birth": "1990-05-15",
            "gender": "Male",
            "phone_number": "555-0123",
            "email": "john.workflow@test.com",
            "emergency_contact_name": "Jane Workflow",
            "emergency_contact_phone": "555-0124",
            "medical_history": "Routine admission for workflow testing"
        }
        
        result = self.call_tool("register_patient", patient_data)
        if result.get("success"):
            self.test_data["patient_id"] = result.get("patient_id")
            self.test_data["patient_number"] = result.get("patient_number")
            print(f"📝 Patient created: {result.get('patient_number')}")
            return True
        else:
            print(f"❌ Failed to create patient: {result.get('message')}")
            return False
    
    def step_2_add_treatments(self):
        """Step 2: Add treatments for the patient."""
        print("\n" + "-"*50)
        print("STEP 2: ADD TREATMENTS")
        print("-"*50)
        
        treatments = [
            {
                "patient_id": self.test_data["patient_id"],
                "treatment_name": "Blood Pressure Monitoring",
                "treatment_type": "monitoring",
                "description": "Regular BP monitoring every 4 hours",
                "duration_hours": 24
            },
            {
                "patient_id": self.test_data["patient_id"],
                "treatment_name": "IV Therapy",
                "treatment_type": "medication",
                "description": "Saline IV drip",
                "duration_hours": 8
            }
        ]
        
        treatment_ids = []
        for treatment in treatments:
            result = self.call_tool("create_treatment_record", treatment)
            if result.get("success"):
                treatment_ids.append(result.get("treatment_id"))
                print(f"💊 Treatment added: {treatment['treatment_name']}")
            else:
                print(f"❌ Failed to add treatment: {result.get('message')}")
                return False
        
        self.test_data["treatment_ids"] = treatment_ids
        return True
    
    def step_3_assign_staff(self):
        """Step 3: Assign staff to the patient."""
        print("\n" + "-"*50)
        print("STEP 3: ASSIGN STAFF")
        print("-"*50)
        
        # First get available staff
        staff_result = self.call_tool("get_available_staff")
        if not staff_result.get("success"):
            print("❌ Could not get available staff")
            return False
        
        available_staff = staff_result.get("staff", [])
        if not available_staff:
            print("❌ No available staff found")
            return False
        
        # Assign first two available staff members
        assigned_staff = []
        for i, staff in enumerate(available_staff[:2]):
            assignment = {
                "patient_id": self.test_data["patient_id"],
                "staff_id": staff["user_id"],
                "role_in_treatment": "primary_care" if i == 0 else "support_care",
                "shift_start": "08:00",
                "shift_end": "16:00"
            }
            
            result = self.call_tool("create_staff_assignment", assignment)
            if result.get("success"):
                assigned_staff.append({
                    "staff_id": staff["user_id"],
                    "assignment_id": result.get("assignment_id"),
                    "name": staff["name"]
                })
                print(f"👨‍⚕️ Staff assigned: {staff['name']} as {assignment['role_in_treatment']}")
            else:
                print(f"❌ Failed to assign staff: {result.get('message')}")
        
        self.test_data["assigned_staff"] = assigned_staff
        return len(assigned_staff) > 0
    
    def step_4_assign_equipment(self):
        """Step 4: Assign equipment to the patient."""
        print("\n" + "-"*50)
        print("STEP 4: ASSIGN EQUIPMENT")
        print("-"*50)
        
        # Get available equipment
        equipment_result = self.call_tool("get_available_equipment")
        if not equipment_result.get("success"):
            print("❌ Could not get available equipment")
            return False
        
        available_equipment = equipment_result.get("equipment", [])
        if not available_equipment:
            print("❌ No available equipment found")
            return False
        
        # Assign first two pieces of equipment
        assigned_equipment = []
        for equipment in available_equipment[:2]:
            assignment = {
                "patient_id": self.test_data["patient_id"],
                "equipment_id": equipment["id"],
                "usage_purpose": "monitoring" if "monitor" in equipment["name"].lower() else "treatment",
                "start_time": datetime.now().isoformat()
            }
            
            result = self.call_tool("create_equipment_assignment", assignment)
            if result.get("success"):
                assigned_equipment.append({
                    "equipment_id": equipment["id"],
                    "assignment_id": result.get("assignment_id"),
                    "name": equipment["name"]
                })
                print(f"🏥 Equipment assigned: {equipment['name']}")
            else:
                print(f"❌ Failed to assign equipment: {result.get('message')}")
        
        self.test_data["assigned_equipment"] = assigned_equipment
        return len(assigned_equipment) > 0
    
    def step_5_assign_bed(self):
        """Step 5: Assign bed to patient."""
        print("\n" + "-"*50)
        print("STEP 5: ASSIGN BED")
        print("-"*50)
        
        # Get available beds
        beds_result = self.call_tool("get_available_beds")
        if not beds_result.get("success"):
            print("❌ Could not get available beds")
            return False
        
        available_beds = beds_result.get("beds", [])
        if not available_beds:
            print("❌ No available beds found")
            return False
        
        # Assign first available bed
        bed = available_beds[0]
        assignment = {
            "patient_id": self.test_data["patient_id"],
            "bed_id": bed["id"],
            "admission_date": datetime.now().isoformat()
        }
        
        result = self.call_tool("assign_bed_to_patient", assignment)
        if result.get("success"):
            self.test_data["bed_id"] = bed["id"]
            self.test_data["bed_number"] = bed["bed_number"]
            print(f"🛏️ Bed assigned: {bed['bed_number']} in room {bed.get('room_number', 'Unknown')}")
            return True
        else:
            print(f"❌ Failed to assign bed: {result.get('message')}")
            return False
    
    def step_6_discharge_patient(self):
        """Step 6: Discharge patient and generate report."""
        print("\n" + "-"*50)
        print("STEP 6: DISCHARGE PATIENT")
        print("-"*50)
        
        discharge_data = {
            "patient_id": self.test_data["patient_id"],
            "discharge_date": datetime.now().isoformat(),
            "discharge_summary": "Patient recovered well from treatment. Vital signs stable.",
            "follow_up_instructions": "Follow up with primary care physician in 1 week",
            "medications_prescribed": "Take prescribed medications as directed"
        }
        
        result = self.call_tool("generate_discharge_report", discharge_data)
        if result.get("success"):
            self.test_data["discharge_report_id"] = result.get("report_id")
            print(f"📋 Discharge report generated: {result.get('report_id')}")
            return True
        else:
            print(f"❌ Failed to discharge patient: {result.get('message')}")
            return False
    
    def step_7_start_bed_turnover(self):
        """Step 7: Start bed turnover process."""
        print("\n" + "-"*50)
        print("STEP 7: START BED TURNOVER PROCESS")
        print("-"*50)
        
        turnover_data = {
            "bed_id": self.test_data["bed_id"],
            "previous_patient_id": self.test_data["patient_id"],
            "turnover_type": "standard",
            "priority_level": "normal"
        }
        
        result = self.call_tool("start_bed_turnover_process", turnover_data)
        if result.get("success"):
            self.test_data["turnover_id"] = result.get("turnover_id")
            print(f"🔄 Bed turnover started: {result.get('turnover_id')}")
            print(f"⏱️ Estimated duration: {result.get('estimated_duration')} minutes")
            return True
        else:
            print(f"❌ Failed to start bed turnover: {result.get('message')}")
            return False
    
    def step_8_mark_equipment_for_cleaning(self):
        """Step 8: Mark equipment for cleaning."""
        print("\n" + "-"*50)
        print("STEP 8: MARK EQUIPMENT FOR CLEANING")
        print("-"*50)
        
        if not self.test_data.get("assigned_equipment"):
            print("⚠️ No equipment was assigned, skipping equipment cleaning")
            return True
        
        equipment_ids = [eq["equipment_id"] for eq in self.test_data["assigned_equipment"]]
        
        cleaning_data = {
            "bed_id": self.test_data["bed_id"],
            "equipment_ids": equipment_ids,
            "cleaning_type": "surface"
        }
        
        result = self.call_tool("mark_equipment_for_cleaning", cleaning_data)
        if result.get("success"):
            print(f"🧽 Equipment marked for cleaning: {result.get('equipment_count')} items")
            return True
        else:
            print(f"❌ Failed to mark equipment for cleaning: {result.get('message')}")
            return False
    
    def step_9_monitor_cleaning_progress(self):
        """Step 9: Monitor bed cleaning progress."""
        print("\n" + "-"*50)
        print("STEP 9: MONITOR CLEANING PROGRESS")
        print("-"*50)
        
        # Check bed status multiple times to simulate monitoring
        for i in range(3):
            result = self.call_tool("get_bed_status_with_time_remaining", {
                "bed_id": self.test_data["bed_id"]
            })
            
            if result.get("success"):
                status = result.get("current_status")
                process_status = result.get("process_status")
                time_remaining = result.get("time_remaining_minutes", 0)
                progress = result.get("progress_percentage", 0)
                
                print(f"🔍 Check {i+1}: Status={status}, Process={process_status}, "
                      f"Time Remaining={time_remaining}min, Progress={progress:.1f}%")
                
                if i < 2:  # Don't sleep on last iteration
                    time.sleep(2)
            else:
                print(f"❌ Failed to get bed status: {result.get('message')}")
                return False
        
        return True
    
    def step_10_complete_cleaning(self):
        """Step 10: Complete bed cleaning process."""
        print("\n" + "-"*50)
        print("STEP 10: COMPLETE BED CLEANING")
        print("-"*50)
        
        # Simulate inspector completing the cleaning
        completion_data = {
            "turnover_id": self.test_data["turnover_id"],
            "inspection_passed": True,
            "inspector_notes": "Bed cleaned thoroughly. All equipment sanitized. Ready for next patient."
        }
        
        result = self.call_tool("complete_bed_cleaning", completion_data)
        if result.get("success"):
            print(f"✅ Bed cleaning completed successfully")
            print(f"⏱️ Total cleaning duration: {result.get('cleaning_duration')} minutes")
            return True
        else:
            print(f"❌ Failed to complete cleaning: {result.get('message')}")
            return False
    
    def step_11_create_new_patient_and_queue(self):
        """Step 11: Create new patient and add to queue."""
        print("\n" + "-"*50)
        print("STEP 11: CREATE NEW PATIENT & ADD TO QUEUE")
        print("-"*50)
        
        # Create new patient
        new_patient_data = {
            "first_name": "Mary",
            "last_name": "NextPatient",
            "date_of_birth": "1985-08-22",
            "gender": "Female",
            "phone_number": "555-0125",
            "email": "mary.nextpatient@test.com",
            "emergency_contact_name": "Bob NextPatient",
            "emergency_contact_phone": "555-0126",
            "medical_history": "Scheduled surgery"
        }
        
        result = self.call_tool("register_patient", new_patient_data)
        if result.get("success"):
            new_patient_id = result.get("patient_id")
            print(f"📝 New patient created: {result.get('patient_number')}")
            
            # Get a department for queue assignment
            departments_result = self.call_tool("get_available_departments")
            if departments_result.get("success"):
                departments = departments_result.get("departments", [])
                if departments:
                    department_id = departments[0]["id"]
                    
                    # Add to patient queue
                    queue_data = {
                        "patient_id": new_patient_id,
                        "department_id": department_id,
                        "bed_type_required": "general",
                        "priority_level": "normal",
                        "medical_condition": "Scheduled procedure"
                    }
                    
                    queue_result = self.call_tool("add_patient_to_queue", queue_data)
                    if queue_result.get("success"):
                        self.test_data["new_patient_id"] = new_patient_id
                        self.test_data["queue_id"] = queue_result.get("queue_id")
                        print(f"📋 Patient added to queue at position {queue_result.get('queue_position')}")
                        return True
                    else:
                        print(f"❌ Failed to add patient to queue: {queue_result.get('message')}")
            
        print(f"❌ Failed to create new patient: {result.get('message')}")
        return False
    
    def step_12_assign_bed_to_next_patient(self):
        """Step 12: Assign the cleaned bed to next patient in queue."""
        print("\n" + "-"*50)
        print("STEP 12: ASSIGN BED TO NEXT PATIENT")
        print("-"*50)
        
        assignment_data = {
            "bed_id": self.test_data["bed_id"]
        }
        
        result = self.call_tool("assign_next_patient_to_bed", assignment_data)
        if result.get("success"):
            assignment = result.get("assignment", {})
            print(f"🛏️ Bed successfully assigned to next patient:")
            print(f"   Patient: {assignment.get('patient_name')}")
            print(f"   Bed: {assignment.get('bed_number')}")
            print(f"   Room: {assignment.get('room_number')}")
            return True
        else:
            print(f"❌ Failed to assign bed to next patient: {result.get('message')}")
            return False
    
    def step_13_verify_workflow_completion(self):
        """Step 13: Verify complete workflow."""
        print("\n" + "-"*50)
        print("STEP 13: VERIFY WORKFLOW COMPLETION")
        print("-"*50)
        
        # Check final bed status
        bed_status = self.call_tool("get_bed_status_with_time_remaining", {
            "bed_id": self.test_data["bed_id"]
        })
        
        if bed_status.get("success"):
            status = bed_status.get("current_status")
            process_status = bed_status.get("process_status")
            
            print(f"🔍 Final bed status: {status}")
            print(f"🔍 Process status: {process_status}")
            
            if status == "occupied" and process_status == "none":
                print("✅ Workflow completed successfully - bed is occupied by new patient")
                return True
            else:
                print(f"⚠️ Unexpected final status - Status: {status}, Process: {process_status}")
                return False
        else:
            print(f"❌ Failed to verify final status: {bed_status.get('message')}")
            return False
    
    def run_complete_workflow(self):
        """Run the complete hospital bed turnover workflow."""
        start_time = datetime.now()
        
        steps = [
            ("Server Health Check", self.test_server_health),
            ("Create Patient", self.step_1_create_patient),
            ("Add Treatments", self.step_2_add_treatments),
            ("Assign Staff", self.step_3_assign_staff),
            ("Assign Equipment", self.step_4_assign_equipment),
            ("Assign Bed", self.step_5_assign_bed),
            ("Discharge Patient", self.step_6_discharge_patient),
            ("Start Bed Turnover", self.step_7_start_bed_turnover),
            ("Mark Equipment for Cleaning", self.step_8_mark_equipment_for_cleaning),
            ("Monitor Cleaning Progress", self.step_9_monitor_cleaning_progress),
            ("Complete Cleaning", self.step_10_complete_cleaning),
            ("Create New Patient & Queue", self.step_11_create_new_patient_and_queue),
            ("Assign Bed to Next Patient", self.step_12_assign_bed_to_next_patient),
            ("Verify Workflow Completion", self.step_13_verify_workflow_completion)
        ]
        
        results = []
        
        for step_name, step_func in steps:
            print(f"\n{'='*20} {step_name} {'='*20}")
            try:
                success = step_func()
                results.append((step_name, success))
                
                if not success:
                    print(f"❌ Step failed: {step_name}")
                    break
                    
            except Exception as e:
                print(f"❌ Exception in {step_name}: {str(e)}")
                results.append((step_name, False))
                break
        
        # Final summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "="*60)
        print("🏥 WORKFLOW TEST SUMMARY")
        print("="*60)
        
        success_count = sum(1 for _, success in results if success)
        total_count = len(results)
        
        for step_name, success in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{status}: {step_name}")
        
        print(f"\nResults: {success_count}/{total_count} steps completed successfully")
        print(f"Total duration: {duration:.1f} seconds")
        
        if success_count == total_count:
            print("\n🎉 COMPLETE WORKFLOW TEST PASSED!")
            print("The hospital bed turnover system is working correctly.")
        else:
            print(f"\n❌ WORKFLOW TEST FAILED at step: {results[success_count][0]}")
        
        return success_count == total_count

if __name__ == "__main__":
    test = HospitalWorkflowTest()
    success = test.run_complete_workflow()
    exit(0 if success else 1)
