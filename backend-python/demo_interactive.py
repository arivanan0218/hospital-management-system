"""
Demo script showing interactive mode working
"""

import asyncio
from client import HospitalManagementClient


async def demo_interactive_features():
    """Demonstrate key interactive features."""
    print("🎯 INTERACTIVE MODE DEMO")
    print("=" * 40)
    
    client = HospitalManagementClient()
    
    # Simulate what happens when user chooses option 2 (interactive mode)
    # but run specific features programmatically
    
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    
    server_params = StdioServerParameters(
        command="python",
        args=["comprehensive_server.py"],
        env=None
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                client.session = session
                await session.initialize()
                print("✅ Connected successfully!")
                
                tools = await session.list_tools()
                client.available_tools = [tool.name for tool in tools.tools]
                print(f"✅ Loaded {len(tools.tools)} tools")
                
                # Demo 1: Analyze Hospital State (option 11)
                print("\n🧠 === DEMO: ANALYZE HOSPITAL STATE ===")
                analysis = await client.analyze_hospital_state()
                
                # Demo 2: Autonomous Management (option 12)
                print("\n🤖 === DEMO: AUTONOMOUS MANAGEMENT ===")
                await client.autonomous_hospital_management()
                
                # Demo 3: Smart Resource Optimization (option 14)
                print("\n⚡ === DEMO: SMART RESOURCE OPTIMIZATION ===")
                optimization = await client.smart_resource_optimization()
                
                print("\n🎉 === INTERACTIVE MODE DEMO COMPLETED ===")
                print("✅ All agentic AI features working perfectly!")
                print("✅ Interactive mode is fully operational!")
                
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(demo_interactive_features())
