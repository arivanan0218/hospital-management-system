"""
Quick test script to verify MCP Bridge functionality
"""

import asyncio
import sys
import time
from client import MCPHttpClient


async def quick_test():
    """Quick test of the MCP bridge"""
    print("🚀 Starting MCP Bridge Quick Test...")
    print("=" * 50)
    
    client = MCPHttpClient()
    
    try:
        # Test 1: Health Check
        print("1️⃣  Testing health check...")
        health = await client.health_check()
        if health.get("status") == "healthy":
            print("✅ Bridge is healthy!")
        else:
            print("❌ Bridge health check failed")
            return False
        
        # Test 2: List Tools
        print("\n2️⃣  Testing tool listing...")
        tools_response = await client.list_tools()
        tools = tools_response.get("tools", [])
        if tools:
            print(f"✅ Found {len(tools)} tools available")
            print("📋 Sample tools:")
            for tool in tools[:5]:
                print(f"   - {tool.get('name', 'Unknown')}")
        else:
            print("❌ No tools found")
            return False
        
        # Test 3: Test a simple operation (list users)
        print("\n3️⃣  Testing list users operation...")
        try:
            users = await client.list_users()
            print(f"✅ Users list retrieved: {users.get('count', 0)} users")
        except Exception as e:
            print(f"⚠️  Users list failed (might be normal if no database): {e}")
        
        # Test 4: Test direct tool call
        print("\n4️⃣  Testing direct tool call...")
        try:
            result = await client.call_tool("list_departments", {})
            print("✅ Direct tool call successful")
        except Exception as e:
            print(f"⚠️  Direct tool call failed (might be normal if no database): {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Quick test completed successfully!")
        print("💡 The bridge is working and can communicate with the MCP server")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("💡 Make sure the bridge server is running: python mcp_bridge.py")
        return False
    
    finally:
        await client.close()


async def wait_for_bridge(max_wait=30):
    """Wait for the bridge to become available"""
    print(f"⏳ Waiting for bridge to become available (max {max_wait}s)...")
    
    client = MCPHttpClient()
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            health = await client.health_check()
            if health.get("status") == "healthy":
                await client.close()
                print("✅ Bridge is ready!")
                return True
        except Exception:
            pass
        
        await asyncio.sleep(1)
        print(".", end="", flush=True)
    
    await client.close()
    print(f"\n❌ Bridge did not become available within {max_wait}s")
    return False


if __name__ == "__main__":
    print("Hospital Management System MCP Bridge - Quick Test")
    print("=" * 60)
    
    # Check if we should wait for the bridge
    if len(sys.argv) > 1 and sys.argv[1] == "--wait":
        if not asyncio.run(wait_for_bridge()):
            sys.exit(1)
    
    # Run the test
    success = asyncio.run(quick_test())
    
    if not success:
        print("\n💡 To start the bridge server, run:")
        print("   python mcp_bridge.py")
        print("\n💡 Or use the convenience script:")
        print("   start_bridge.bat  (Windows)")
        print("   ./start_bridge.sh (Linux/macOS)")
        sys.exit(1)
    
    print("\n🚀 Bridge is ready for use!")
    print("📖 See README.md for usage examples")
