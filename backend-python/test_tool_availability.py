"""Test tool availability and schemas for debugging frontend issues."""

import json
import asyncio
from multi_agent_server import mcp

async def list_available_tools():
    """List all tools and their schemas."""
    print("🔧 Available Tools in Multi-Agent Server")
    print("=" * 60)
    
    # Get tools from MCP server
    tools_info = await mcp.list_tools()
    
    print(f"📋 Found {len(tools_info)} tools:")
    print(f"🔍 Tools type: {type(tools_info)}")
    
    meeting_tools = []
    email_tools = []
    all_tools = []
    
    if hasattr(tools_info, 'tools'):
        tools_list = tools_info.tools
    else:
        tools_list = tools_info
    
    for tool in tools_list:
        tool_name = tool.name if hasattr(tool, 'name') else str(tool)
        all_tools.append(tool_name)
        
        if 'meeting' in tool_name.lower() or 'schedule' in tool_name.lower():
            meeting_tools.append(tool_name)
        
        if 'email' in tool_name.lower() or 'send' in tool_name.lower():
            email_tools.append(tool_name)
    
    print(f"\n📧 Email-related tools: {email_tools}")
    print(f"🗓️ Meeting-related tools: {meeting_tools}")
    
    # Check specific tools that the frontend is trying to call
    test_tools = ['list_users', 'list_staff', 'schedule_meeting', 'send_email']
    
    print(f"\n🔍 Checking specific tools frontend is calling:")
    for tool_name in test_tools:
        if tool_name in all_tools:
            print(f"   ✅ {tool_name}: Available")
            
            # Get the tool info
            for tool in tools_list:
                if (hasattr(tool, 'name') and tool.name == tool_name) or str(tool) == tool_name:
                    if hasattr(tool, 'description'):
                        print(f"      Description: {tool.description}")
                    if hasattr(tool, 'inputSchema') and tool.inputSchema:
                        print(f"      Schema: {json.dumps(tool.inputSchema, indent=8)}")
                    break
        else:
            print(f"   ❌ {tool_name}: NOT FOUND")
    
    return all_tools

if __name__ == "__main__":
    asyncio.run(list_available_tools())
