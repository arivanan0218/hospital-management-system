"""
Test script to verify interactive mode works
"""

import asyncio
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from client import HospitalManagementClient


async def test_interactive_connection():
    """Test that interactive mode can connect properly."""
    print("🧪 Testing Interactive Mode Connection...")
    
    client = HospitalManagementClient()
    
    try:
        # Simulate just the connection part of interactive mode
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        server_params = StdioServerParameters(
            command="python",
            args=["comprehensive_server.py"],
            env=None
        )
        
        print("1. Creating connection...")
        async with stdio_client(server_params) as (read, write):
            print("2. Creating session...")
            async with ClientSession(read, write) as session:
                print("3. Initializing session...")
                await session.initialize()
                print("✅ Session initialized!")
                
                print("4. Getting tools...")
                tools = await session.list_tools()
                print(f"✅ Found {len(tools.tools)} tools")
                
                print("5. Testing analyze hospital state...")
                client.session = session
                client.available_tools = [tool.name for tool in tools.tools]
                
                # Test just one simple operation
                analysis = await client.analyze_hospital_state()
                print(f"✅ Analysis completed! Found {analysis['total_patients']} patients")
                
                print("🎉 Interactive mode connection test PASSED!")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_interactive_connection())
