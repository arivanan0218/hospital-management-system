#!/usr/bin/env python3
"""Check available tools in the backend"""

import requests
import json

def check_tools():
    """Check what tools are available"""
    try:
        response = requests.get("http://localhost:8000/tools/list")
        if response.status_code == 200:
            result = response.json()
            tools = result.get("result", {}).get("tools", [])
            
            print(f"Found {len(tools)} tools:")
            print("=" * 50)
            
            # Group tools by category
            categories = {}
            for tool in tools:
                name = tool["name"]
                desc = tool.get("description", "")
                
                if "create" in name:
                    category = "CREATE"
                elif "list" in name or "get" in name or "search" in name:
                    category = "READ"
                elif "update" in name or "assign" in name:
                    category = "UPDATE"
                elif "delete" in name or "discharge" in name:
                    category = "DELETE"
                else:
                    category = "OTHER"
                
                if category not in categories:
                    categories[category] = []
                categories[category].append((name, desc))
            
            # Print by category
            for category in ["CREATE", "READ", "UPDATE", "DELETE", "OTHER"]:
                if category in categories:
                    print(f"\n{category} TOOLS:")
                    print("-" * 30)
                    for name, desc in categories[category]:
                        print(f"• {name}: {desc}")
            
            # Check for specific workflow tools
            print(f"\nWORKFLOW TOOLS CHECK:")
            print("-" * 30)
            workflow_tools = [
                "create_patient",
                "assign_bed_to_patient",
                "create_treatment_record", 
                "discharge_patient_complete",
                "get_patient_discharge_status",
                "get_bed_status_with_time_remaining"
            ]
            
            tool_names = [tool["name"] for tool in tools]
            for tool in workflow_tools:
                if tool in tool_names:
                    print(f"✅ {tool}")
                else:
                    print(f"❌ {tool} - MISSING")
                    
        else:
            print(f"Failed to get tools: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_tools()
