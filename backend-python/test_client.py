#!/usr/bin/env python3
"""
Simple test for the Hospital Management System MCP Client
This test verifies that the client can import and connect properly.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_client_import():
    """Test that the client can be imported without errors."""
    try:
        from client import HospitalMCPClient
        print("✅ Client imported successfully")
        
        # Create client instance
        client = HospitalMCPClient()
        print("✅ Client instance created")
        
        # Test connection (will fail without server running, but that's expected)
        print("📡 Testing connection to server...")
        connected = await client.connect()
        
        if connected:
            print("✅ Connected to server successfully!")
            
            # Test loading capabilities
            if client.tools:
                print(f"✅ Loaded {len(client.tools)} tools")
            if client.resources:
                print(f"✅ Loaded {len(client.resources)} resources")
            
            await client.disconnect()
        else:
            print("⚠️  Could not connect to server (this is expected if server is not running)")
            print("   To test with server: run 'python server.py' in another terminal")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def main():
    """Main test function."""
    print("🧪 Testing Hospital MCP Client...")
    print("=" * 50)
    
    success = await test_client_import()
    
    if success:
        print("\n✅ Client test completed successfully!")
        print("\n📋 To use the client:")
        print("   1. Start the server: python server.py")
        print("   2. In another terminal, run: python client.py")
        print("   3. Optional: Set GEMINI_API_KEY for AI features")
    else:
        print("\n❌ Client test failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
