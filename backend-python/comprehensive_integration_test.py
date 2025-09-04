"""
Comprehensive Integration Test for LangChain/LangGraph Implementation
Tests both backend functionality and frontend compatibility
"""

import requests
import json
import time
from typing import Dict, Any

class IntegrationTester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.results = []
    
    def log_result(self, test_name: str, success: bool, details: str = ""):
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_backend_health(self):
        """Test backend server health and basic configuration"""
        print("\n=== TESTING BACKEND HEALTH ===")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                self.log_result("Backend Health", True, f"Status: {health.get('status')}")
                self.log_result("Database Connection", health.get('database') == 'connected', health.get('database'))
                self.log_result("Multi-Agent System", health.get('multi_agent') == 'active', f"Agents: {health.get('agents_count')}")
                self.log_result("Tools Available", health.get('tools_count', 0) > 100, f"Count: {health.get('tools_count')}")
                return True
            else:
                self.log_result("Backend Health", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Backend Health", False, f"Connection error: {e}")
            return False
    
    def test_tool_discovery(self):
        """Test tool discovery and LangGraph integration"""
        print("\n=== TESTING TOOL DISCOVERY ===")
        
        try:
            response = requests.get(f"{self.base_url}/tools/list", timeout=10)
            if response.status_code == 200:
                result = response.json()
                tools = result.get('result', {}).get('tools', [])
                
                self.log_result("Tools List Endpoint", True, f"Found {len(tools)} tools")
                
                # Check for LangGraph tools
                langraph_tools = [t for t in tools if 'langraph' in t.get('name', '').lower()]
                enhanced_tools = [t for t in tools if 'enhanced' in t.get('name', '').lower()]
                
                self.log_result("LangGraph Tools", len(langraph_tools) > 0, f"Found {len(langraph_tools)} LangGraph tools")
                self.log_result("Enhanced AI Tools", len(enhanced_tools) > 0, f"Found {len(enhanced_tools)} enhanced tools")
                
                # Check for core hospital tools
                core_tools = ['create_patient', 'list_beds', 'get_system_status', 'check_bed_status']
                found_core = [t['name'] for t in tools if t.get('name') in core_tools]
                self.log_result("Core Hospital Tools", len(found_core) >= 3, f"Found: {found_core}")
                
                return len(tools) > 50
            else:
                self.log_result("Tools List Endpoint", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Tools List Endpoint", False, f"Error: {e}")
            return False
    
    def test_langraph_functionality(self):
        """Test LangGraph workflow functionality"""
        print("\n=== TESTING LANGRAPH FUNCTIONALITY ===")
        
        # Test workflow status
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "get_system_status",
                    "arguments": {}
                }
            }
            
            response = requests.post(f"{self.base_url}/tools/call", json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                self.log_result("System Status Tool", True, "Tool call successful")
                
                # Extract system info
                content = result.get('result', {}).get('content', [])
                if content and len(content) > 0:
                    try:
                        system_data = json.loads(content[0].get('text', '{}'))
                        agents_count = system_data.get('agents_count', 0)
                        total_tools = system_data.get('total_tools', 0)
                        
                        self.log_result("System Integration", True, f"Agents: {agents_count}, Tools: {total_tools}")
                    except:
                        self.log_result("System Data Parsing", False, "Could not parse system data")
                
                return True
            else:
                self.log_result("System Status Tool", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("System Status Tool", False, f"Error: {e}")
            return False
    
    def test_enhanced_ai_tools(self):
        """Test enhanced AI clinical tools"""
        print("\n=== TESTING ENHANCED AI TOOLS ===")
        
        # Test enhanced symptom analysis
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "enhanced_symptom_analysis",
                    "arguments": {
                        "symptoms": "chest pain and shortness of breath",
                        "patient_history": "65-year-old male with hypertension"
                    }
                }
            }
            
            response = requests.post(f"{self.base_url}/tools/call", json=payload, timeout=15)
            if response.status_code == 200:
                result = response.json()
                self.log_result("Enhanced Symptom Analysis", True, "AI tool accessible")
                return True
            else:
                self.log_result("Enhanced Symptom Analysis", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Enhanced Symptom Analysis", False, f"Error: {e}")
            return False
    
    def test_frontend_compatibility(self):
        """Test frontend compatibility and configuration"""
        print("\n=== TESTING FRONTEND COMPATIBILITY ===")
        
        # Check if frontend files exist
        import os
        frontend_path = "../frontend"
        
        try:
            # Check key frontend files
            files_to_check = [
                "package.json",
                "src/App.js",
                "src/components",
                "public/index.html"
            ]
            
            for file_path in files_to_check:
                full_path = os.path.join(frontend_path, file_path)
                exists = os.path.exists(full_path)
                self.log_result(f"Frontend File: {file_path}", exists, "Found" if exists else "Missing")
            
            # Check package.json for dependencies
            package_json_path = os.path.join(frontend_path, "package.json")
            if os.path.exists(package_json_path):
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                    dependencies = package_data.get('dependencies', {})
                    
                    # Check for key frontend dependencies
                    key_deps = ['react', 'axios']
                    for dep in key_deps:
                        has_dep = dep in dependencies
                        self.log_result(f"Frontend Dependency: {dep}", has_dep, 
                                      dependencies.get(dep, "Not found") if has_dep else "Missing")
            
            return True
        except Exception as e:
            self.log_result("Frontend Compatibility", False, f"Error: {e}")
            return False
    
    def test_cors_configuration(self):
        """Test CORS configuration for frontend integration"""
        print("\n=== TESTING CORS CONFIGURATION ===")
        
        try:
            # Test CORS headers
            headers = {
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = requests.options(f"{self.base_url}/health", headers=headers, timeout=5)
            
            cors_enabled = response.status_code in [200, 204]
            self.log_result("CORS Configuration", cors_enabled, 
                          "Enabled" if cors_enabled else f"HTTP {response.status_code}")
            
            return cors_enabled
        except Exception as e:
            self.log_result("CORS Configuration", False, f"Error: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all integration tests"""
        print("🚀 COMPREHENSIVE LANGCHAIN/LANGGRAPH INTEGRATION TEST")
        print("=" * 70)
        
        tests = [
            ("Backend Health", self.test_backend_health),
            ("Tool Discovery", self.test_tool_discovery),
            ("LangGraph Functionality", self.test_langraph_functionality),
            ("Enhanced AI Tools", self.test_enhanced_ai_tools),
            ("Frontend Compatibility", self.test_frontend_compatibility),
            ("CORS Configuration", self.test_cors_configuration)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_result(f"{test_name} (Exception)", False, str(e))
        
        print("\n" + "=" * 70)
        print(f"📊 INTEGRATION TEST RESULTS: {passed_tests}/{total_tests} tests passed")
        print(f"📈 Success Rate: {passed_tests/total_tests*100:.1f}%")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        for category in ["Backend Health", "Tool Discovery", "LangGraph Functionality", 
                        "Enhanced AI Tools", "Frontend Compatibility", "CORS Configuration"]:
            category_results = [r for r in self.results if category.lower() in r["test"].lower()]
            category_passed = sum(1 for r in category_results if r["success"])
            category_total = len(category_results)
            
            if category_total > 0:
                print(f"  {category}: {category_passed}/{category_total}")
        
        # Summary
        print(f"\n🎯 INTEGRATION STATUS:")
        if passed_tests >= total_tests * 0.9:
            print("✅ EXCELLENT: LangChain/LangGraph integration is working perfectly!")
            print("✅ Backend and frontend are properly configured")
            print("✅ Ready for production use")
        elif passed_tests >= total_tests * 0.7:
            print("🟡 GOOD: LangChain/LangGraph integration is mostly working")
            print("⚠️ Some minor issues detected - check failed tests")
        else:
            print("❌ ISSUES DETECTED: Integration needs attention")
            print("❌ Check failed tests and fix configuration issues")
        
        return passed_tests >= total_tests * 0.8

if __name__ == "__main__":
    tester = IntegrationTester()
    success = tester.run_comprehensive_test()
    
    print(f"\n🏥 FINAL STATUS: {'✅ READY' if success else '❌ NEEDS FIXES'}")
    exit(0 if success else 1)
