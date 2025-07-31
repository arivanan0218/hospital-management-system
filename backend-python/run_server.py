#!/usr/bin/env python3
"""
Hospital Management System MCP Server Runner
Usage: python run_server.py [--help]
"""

import sys
import argparse
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    parser = argparse.ArgumentParser(
        description="Hospital Management System MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_server.py              # Start the MCP server
  python run_server.py --test       # Run functionality tests
  python run_server.py --help       # Show this help
        """
    )
    
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Run tests instead of starting the server"
    )
    
    args = parser.parse_args()
    
    if args.test:
        print("Running Hospital Management System tests...")
        try:
            import test_server
            test_server.test_basic_functionality()
        except ImportError as e:
            print(f"Error importing test module: {e}")
            sys.exit(1)
    else:
        print("Starting Hospital Management System MCP Server...")
        print("Server is running in stdio mode for MCP clients...")
        print("Press Ctrl+C to stop the server.")
        try:
            import server
            server.mcp.run()
        except KeyboardInterrupt:
            print("\nServer stopped by user.")
        except ImportError as e:
            print(f"Error importing server module: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Server error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
