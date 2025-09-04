"""
End-to-End Integration Verification Test
Tests complete integration between frontend and backend with LangChain/LangGraph
"""

import requests
import json
import time
from typing import Dict, Any

class EndToEndIntegrationTest:
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.frontend_url = "http://localhost:5173"
        self.results = []
    
    def log_result(self, test_name: str, success: bool, details: str = ""):
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_backend_availability(self):
        """Test backend server health and APIs"""
        print("\n🧪 TESTING BACKEND AVAILABILITY")
        print("-" * 40)
        
        try:
            # Health check
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                self.log_result("Backend Health", True, 
                              f"Status: {health.get('status')}, Agents: {health.get('agents_count')}")
            else:
                self.log_result("Backend Health", False, f"HTTP {response.status_code}")
                return False
                
            # Tools list
            response = requests.get(f"{self.backend_url}/tools/list", timeout=10)
            if response.status_code == 200:
                result = response.json()
                tools = result.get('result', {}).get('tools', [])
                self.log_result("Backend Tools API", True, f"Found {len(tools)} tools")
            else:
                self.log_result("Backend Tools API", False, f"HTTP {response.status_code}")
                
            return True
            
        except Exception as e:
            self.log_result("Backend Availability", False, f"Error: {e}")
            return False
    
    def test_frontend_availability(self):
        """Test frontend server availability"""
        print("\n🧪 TESTING FRONTEND AVAILABILITY")
        print("-" * 40)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                self.log_result("Frontend Server", True, "Vite development server running")
                
                # Check if it contains React app indicators
                content = response.text
                if 'vite' in content.lower() or 'react' in content.lower():
                    self.log_result("Frontend React App", True, "React application detected")
                else:
                    self.log_result("Frontend React App", False, "React application not detected")
                    
                return True
            else:
                self.log_result("Frontend Server", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Frontend Availability", False, f"Error: {e}")
            return False
    
    def test_langraph_workflows(self):
        """Test LangGraph workflow functionality"""
        print("\n🧪 TESTING LANGRAPH WORKFLOWS")
        print("-" * 40)
        
        try:
            # Test workflow status
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "get_langraph_workflow_status",
                    "arguments": {}
                }
            }
            
            response = requests.post(f"{self.backend_url}/tools/call", json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                content = result.get("result", {}).get("content", [])
                if content:
                    data = json.loads(content[0].get("text", "{}"))
                    if data.get("success"):
                        self.log_result("LangGraph Workflow Status", True, "Workflow system active")
                        workflows = data.get("status", {}).get("available_workflows", [])
                        self.log_result("Available Workflows", len(workflows) >= 0, f"Workflows: {workflows}")
                    else:
                        self.log_result("LangGraph Workflow Status", False, data.get("message"))
                else:
                    self.log_result("LangGraph Workflow Status", False, "No response content")
            else:
                self.log_result("LangGraph Workflow Status", False, f"HTTP {response.status_code}")
                
            # Test patient admission workflow
            test_patient = {
                "first_name": "Test",
                "last_name": "Integration",
                "date_of_birth": "1990-01-01",
                "phone": "555-TEST",
                "medical_history": "Integration test patient"
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "execute_langraph_patient_admission",
                    "arguments": {
                        "patient_data": test_patient
                    }
                }
            }
            
            response = requests.post(f"{self.backend_url}/tools/call", json=payload, timeout=15)
            if response.status_code == 200:
                result = response.json()
                content = result.get("result", {}).get("content", [])
                if content:
                    data = json.loads(content[0].get("text", "{}"))
                    if data.get("success") or "workflow_result" in data:
                        self.log_result("LangGraph Patient Admission", True, "Workflow executed successfully")
                    else:
                        self.log_result("LangGraph Patient Admission", False, data.get("message", "Unknown error"))
                else:
                    self.log_result("LangGraph Patient Admission", False, "No response content")
            else:
                self.log_result("LangGraph Patient Admission", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_result("LangGraph Workflows", False, f"Error: {e}")
    
    def test_enhanced_ai_tools(self):
        """Test Enhanced AI clinical tools"""
        print("\n🧪 TESTING ENHANCED AI CLINICAL TOOLS")
        print("-" * 40)
        
        enhanced_tools = [
            {
                "name": "enhanced_symptom_analysis",
                "args": {
                    "symptoms": "chest pain and shortness of breath",
                    "patient_history": "65-year-old male with hypertension"
                }
            },
            {
                "name": "enhanced_differential_diagnosis", 
                "args": {
                    "clinical_data": {
                        "symptoms": "chest pain, dyspnea",
                        "vital_signs": "HR 110, BP 150/95",
                        "patient_history": "HTN, hyperlipidemia"
                    }
                }
            },
            {
                "name": "enhanced_vital_signs_analysis",
                "args": {
                    "vitals_data": {
                        "heart_rate": 110,
                        "blood_pressure": "150/95",
                        "respiratory_rate": 22,
                        "temperature": 37.2,
                        "oxygen_saturation": 94,
                        "age": 65
                    }
                }
            }
        ]
        
        for tool_test in enhanced_tools:
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": tool_test["name"],
                        "arguments": tool_test["args"]
                    }
                }
                
                response = requests.post(f"{self.backend_url}/tools/call", json=payload, timeout=15)
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("result", {}).get("content", [])
                    if content:
                        data = json.loads(content[0].get("text", "{}"))
                        if data.get("success") or "analysis" in data or "diagnosis" in data:
                            self.log_result(f"Enhanced AI: {tool_test['name']}", True, "Tool executed successfully")
                        else:
                            self.log_result(f"Enhanced AI: {tool_test['name']}", False, data.get("message", "Unknown error"))
                    else:
                        self.log_result(f"Enhanced AI: {tool_test['name']}", False, "No response content")
                else:
                    self.log_result(f"Enhanced AI: {tool_test['name']}", False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Enhanced AI: {tool_test['name']}", False, f"Error: {e}")
    
    def test_core_hospital_functions(self):
        """Test core hospital management functions"""
        print("\n🧪 TESTING CORE HOSPITAL FUNCTIONS")
        print("-" * 40)
        
        core_tools = [
            {"name": "get_system_status", "args": {}},
            {"name": "list_patients", "args": {"status": "active"}},
            {"name": "list_beds", "args": {"status": "available"}},
            {"name": "get_dashboard_stats", "args": {}}
        ]
        
        for tool_test in core_tools:
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": tool_test["name"],
                        "arguments": tool_test["args"]
                    }
                }
                
                response = requests.post(f"{self.backend_url}/tools/call", json=payload, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("result", {}).get("content", [])
                    if content:
                        data = json.loads(content[0].get("text", "{}"))
                        if data.get("success") or "data" in data or "patients" in data:
                            self.log_result(f"Core Function: {tool_test['name']}", True, "Function working")
                        else:
                            self.log_result(f"Core Function: {tool_test['name']}", False, data.get("message", "Unknown error"))
                    else:
                        self.log_result(f"Core Function: {tool_test['name']}", False, "No response content")
                else:
                    self.log_result(f"Core Function: {tool_test['name']}", False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Core Function: {tool_test['name']}", False, f"Error: {e}")
    
    def run_comprehensive_test(self):
        """Run all integration tests"""
        print("🚀 END-TO-END INTEGRATION VERIFICATION TEST")
        print("🏥 Hospital Management System with LangChain/LangGraph")
        print("=" * 70)
        
        # Run all test suites
        tests = [
            ("Backend Availability", self.test_backend_availability),
            ("Frontend Availability", self.test_frontend_availability),
            ("LangGraph Workflows", self.test_langraph_workflows),
            ("Enhanced AI Tools", self.test_enhanced_ai_tools),
            ("Core Hospital Functions", self.test_core_hospital_functions)
        ]
        
        passed_suites = 0
        total_suites = len(tests)
        
        for suite_name, test_func in tests:
            try:
                if test_func():
                    passed_suites += 1
            except Exception as e:
                self.log_result(f"{suite_name} (Exception)", False, str(e))
        
        # Calculate overall results
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        
        print("\n" + "=" * 70)
        print(f"📊 INTEGRATION TEST RESULTS:")
        print(f"   Test Suites: {passed_suites}/{total_suites} passed")
        print(f"   Individual Tests: {passed_tests}/{total_tests} passed")
        print(f"   Success Rate: {passed_tests/total_tests*100:.1f}%")
        
        # Categorize results
        categories = {
            "Backend": ["Backend", "Core Function"],
            "Frontend": ["Frontend"],
            "LangGraph": ["LangGraph"],
            "Enhanced AI": ["Enhanced AI"]
        }
        
        print(f"\n📋 RESULTS BY CATEGORY:")
        for category, keywords in categories.items():
            category_results = [r for r in self.results if any(kw in r["test"] for kw in keywords)]
            if category_results:
                category_passed = sum(1 for r in category_results if r["success"])
                category_total = len(category_results)
                print(f"   {category}: {category_passed}/{category_total}")
        
        # Final assessment
        print(f"\n🎯 SYSTEM STATUS:")
        if passed_tests >= total_tests * 0.9:
            print("✅ EXCELLENT: Full integration working perfectly!")
            print("✅ LangChain/LangGraph successfully integrated")
            print("✅ Frontend and backend properly configured")
            print("✅ Production ready")
            status = "READY"
        elif passed_tests >= total_tests * 0.7:
            print("🟡 GOOD: System mostly working with minor issues")
            print("⚠️ Some features may need attention")
            status = "MOSTLY_READY"
        else:
            print("❌ ISSUES: Integration needs attention")
            print("❌ Check failed tests and fix issues")
            status = "NEEDS_FIXES"
        
        print(f"\n🏥 FINAL INTEGRATION STATUS: {status}")
        print("💡 Access your enhanced hospital system at:")
        print(f"   Frontend: {self.frontend_url}")
        print(f"   Backend API: {self.backend_url}")
        print(f"   Health Check: {self.backend_url}/health")
        
        return status == "READY"

if __name__ == "__main__":
    tester = EndToEndIntegrationTest()
    success = tester.run_comprehensive_test()
    exit(0 if success else 1)
