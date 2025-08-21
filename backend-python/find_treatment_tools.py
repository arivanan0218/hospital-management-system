#!/usr/bin/env python3
"""
Find treatment-related tools
"""
import requests
import json

def main():
    # Get list of available tools
    response = requests.get('http://localhost:8000/tools/list')
    if response.status_code == 200:
        result = response.json()
        tools = result['result']['tools']
        
        print("🔍 SEARCHING FOR TREATMENT/MEDICAL TOOLS")
        print("=" * 50)
        
        treatment_tools = []
        medical_tools = []
        
        for tool in tools:
            name = tool['name'].lower()
            if 'treatment' in name:
                treatment_tools.append(tool)
            elif 'medical' in name:
                medical_tools.append(tool)
        
        print(f"\n📋 TREATMENT TOOLS ({len(treatment_tools)} found):")
        for tool in treatment_tools:
            print(f"   - {tool['name']}: {tool.get('description', 'N/A')}")
        
        print(f"\n🏥 MEDICAL TOOLS ({len(medical_tools)} found):")
        for tool in medical_tools:
            print(f"   - {tool['name']}: {tool.get('description', 'N/A')}")
        
        # Search for other relevant tools
        print(f"\n🔍 OTHER POTENTIALLY RELEVANT TOOLS:")
        keywords = ['record', 'add', 'create', 'log', 'history', 'diagnosis']
        for keyword in keywords:
            matching_tools = [t for t in tools if keyword in t['name'].lower()]
            if matching_tools:
                print(f"\n   {keyword.upper()} tools:")
                for tool in matching_tools[:5]:  # Show first 5
                    print(f"   - {tool['name']}")
    else:
        print(f"❌ Failed to get tools list: {response.status_code}")

if __name__ == "__main__":
    main()
