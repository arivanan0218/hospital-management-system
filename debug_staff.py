#!/usr/bin/env python3
"""
Debug the staff list API call
"""

import asyncio
import aiohttp
import json

async def debug_staff_list():
    """Debug the staff list API call to see what's happening"""
    
    print("🔍 DEBUGGING STAFF LIST API CALL")
    print("=" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test 1: Direct list_staff call
            print("\n📞 Test 1: Direct list_staff call...")
            
            staff_call = {
                "method": "tools/call",
                "params": {
                    "name": "list_staff", 
                    "arguments": {}
                }
            }
            
            async with session.post(
                'http://localhost:8000/tools/call',
                json=staff_call,
                headers={'Content-Type': 'application/json'}
            ) as response:
                print(f"Response Status: {response.status}")
                result = await response.json()
                print(f"Raw Response: {json.dumps(result, indent=2)}")
                
                if 'content' in result:
                    content = result['content']
                    if content and len(content) > 0:
                        text_content = content[0].get('text', '')
                        print(f"\nText Content: {text_content}")
                        
                        try:
                            parsed_data = json.loads(text_content)
                            print(f"Parsed Data: {json.dumps(parsed_data, indent=2)}")
                        except json.JSONDecodeError as e:
                            print(f"JSON Parse Error: {e}")
            
            # Test 2: List available tools to make sure list_staff exists
            print(f"\n📋 Test 2: Checking available tools...")
            
            async with session.get('http://localhost:8000/tools/list') as response:
                if response.status == 200:
                    tools_result = await response.json()
                    print(f"Tools Response Status: {response.status}")
                    
                    # Look for staff-related tools
                    tools = tools_result.get('tools', [])
                    staff_tools = [tool for tool in tools if 'staff' in tool.get('name', '').lower()]
                    
                    print(f"\nFound {len(staff_tools)} staff-related tools:")
                    for tool in staff_tools:
                        print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                        
    except Exception as e:
        print(f"❌ Debug failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_staff_list())
