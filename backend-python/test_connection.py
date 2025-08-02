"""
Simple test to verify MCP connection works
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_connection():
    """Test basic MCP connection."""
    print("🧪 Testing MCP Connection...")
    
    try:
        server_params = StdioServerParameters(
            command="python",
            args=["comprehensive_server.py"],
            env=None
        )
        
        print("1. Creating stdio client...")
        async with stdio_client(server_params) as (read, write):
            print("2. Creating session...")
            async with ClientSession(read, write) as session:
                print("3. Initializing session...")
                await session.initialize()
                print("✅ Session initialized successfully!")
                
                print("4. Testing list_tools...")
                tools = await session.list_tools()
                print(f"✅ Found {len(tools.tools)} tools")
                
                print("5. Testing list_users...")
                result = await session.call_tool("list_users", {})
                print(f"✅ list_users result: {result.content[0].text[:100]}...")
                
                print("🎉 All tests passed! MCP connection is working.")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_connection())
