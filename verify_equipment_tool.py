#!/usr/bin/env python3
"""
Quick verification that the correct equipment usage tool is available
"""
import requests
import json

def check_equipment_tools():
    """Check available equipment usage tools"""
    
    print("🔍 Checking Available Equipment Usage Tools")
    print("=" * 50)
    
    # List available tools
    try:
        url = 'http://localhost:8000/tools/list'
        response = requests.get(url)
        result = response.json()
        
        tools = result.get('result', {}).get('tools', [])
        equipment_tools = [tool for tool in tools if 'equipment_usage' in tool['name']]
        
        print(f"Found {len(equipment_tools)} equipment usage tools:")
        for tool in equipment_tools:
            print(f"  ✅ {tool['name']}")
            
        # Check if our preferred tool is available
        preferred_tool = 'add_equipment_usage_with_codes'
        has_preferred = any(tool['name'] == preferred_tool for tool in equipment_tools)
        
        if has_preferred:
            print(f"\n✅ SUCCESS: '{preferred_tool}' is available!")
            print("   Frontend should use this tool to avoid UUID errors.")
        else:
            print(f"\n❌ ERROR: '{preferred_tool}' not found!")
            print("   Backend may need to be restarted.")
            
        # Test the preferred tool if available
        if has_preferred:
            print(f"\n🧪 Testing {preferred_tool}...")
            test_url = 'http://localhost:8000/tools/call'
            test_data = {
                'params': {
                    'name': preferred_tool,
                    'arguments': {
                        'patient_id': 'P002',
                        'equipment_id': 'EQ001',
                        'staff_id': 'EMP001',
                        'purpose': 'Test verification call'
                    }
                }
            }
            
            test_response = requests.post(test_url, json=test_data)
            if test_response.status_code == 200:
                test_result = test_response.json()
                if 'result' in test_result and 'content' in test_result['result']:
                    content = test_result['result']['content'][0]['text']
                    parsed = json.loads(content)
                    
                    if parsed.get('success'):
                        print("   ✅ Tool test PASSED - Ready for frontend use!")
                        return True
                    else:
                        print(f"   ⚠️  Tool test returned: {parsed.get('message')}")
                        return False
                        
        return False
        
    except Exception as e:
        print(f"❌ Error checking tools: {e}")
        return False

if __name__ == "__main__":
    success = check_equipment_tools()
    
    if success:
        print("\n🎉 VERIFICATION COMPLETE")
        print("✅ Equipment usage tool is ready!")
        print("✅ Frontend should use 'add_equipment_usage_with_codes'")
        print("✅ UUID formatting issues should be resolved!")
    else:
        print("\n💥 VERIFICATION FAILED")
        print("❌ Equipment usage tool may need troubleshooting")
