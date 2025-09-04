"""
Simple test to check if server is working and has our LangGraph tools
"""

import requests
import json

def test_server():
    """Test if server is responding"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        print(f"✅ Server Health: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Server Health: {e}")
        return False

def test_tools_list():
    """Test listing available MCP tools"""
    try:
        # First try the direct tools endpoint
        response = requests.get("http://127.0.0.1:8000/tools", timeout=10)
        if response.status_code == 200:
            tools = response.json()
            print(f"✅ Found {len(tools)} tools")
            
            # Look for our LangGraph tools
            langraph_tools = [tool for tool in tools if 'langraph' in tool.get('name', '').lower()]
            enhanced_tools = [tool for tool in tools if 'enhanced' in tool.get('name', '').lower()]
            
            print(f"📊 LangGraph tools: {len(langraph_tools)}")
            print(f"📊 Enhanced AI tools: {len(enhanced_tools)}")
            
            # List some tool names
            for tool in tools[:10]:
                print(f"   - {tool.get('name', 'unknown')}")
            
            return True
        else:
            print(f"❌ Tools endpoint: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Tools endpoint error: {e}")
        return False

def test_orchestrator_query():
    """Test the orchestrator with a simple query"""
    try:
        # Try a simple orchestrator query
        payload = {
            "query": "What is the status of the hospital management system?",
            "context": {}
        }
        
        response = requests.post(
            "http://127.0.0.1:8000/orchestrator/query",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Orchestrator query successful")
            print(f"   Response: {result.get('response', 'no response')[:100]}...")
            return True
        else:
            print(f"❌ Orchestrator query: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Orchestrator query error: {e}")
        return False

def main():
    """Run all simple tests"""
    print("🚀 Simple LangChain/LangGraph Integration Test")
    print("=" * 50)
    
    tests = [
        ("Server Health", test_server),
        ("Tools List", test_tools_list),
        ("Orchestrator Query", test_orchestrator_query)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 Basic integration is working!")
    else:
        print("⚠️ Some issues detected")

if __name__ == "__main__":
    main()
