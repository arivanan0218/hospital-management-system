#!/usr/bin/env python3

import requests
import json

def get_tools_list():
    """Get the list of available tools from the backend"""
    
    url = "http://localhost:8000/tools/list"
    
    try:
        print("🔧 Getting tools list...")
        response = requests.get(url, timeout=10)
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if "result" in result and "tools" in result["result"]:
                tools = result["result"]["tools"]
                print(f"📋 Found {len(tools)} tools:")
                
                # Look for bed-related tools
                bed_tools = [tool for tool in tools if 'bed' in tool['name'].lower()]
                if bed_tools:
                    print("\n🏥 Bed-related tools:")
                    for tool in bed_tools:
                        print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
                
                # Look for our specific tool
                target_tool = None
                for tool in tools:
                    if tool['name'] == 'get_bed_status_with_time_remaining':
                        target_tool = tool
                        break
                
                if target_tool:
                    print(f"\n✅ Found target tool: {target_tool['name']}")
                    print(f"📝 Description: {target_tool.get('description', 'No description')}")
                else:
                    print("\n❌ Target tool 'get_bed_status_with_time_remaining' not found!")
                    print("\n🔍 All tools:")
                    for tool in tools:
                        print(f"  - {tool['name']}")
                        
            else:
                print("❌ Invalid response format")
                print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    get_tools_list()
