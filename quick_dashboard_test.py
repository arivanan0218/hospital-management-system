"""Quick test of one dashboard tool"""

import requests
import json

try:
    # Test get_dashboard_stats
    response = requests.post(
        "http://0.0.0.0:8000/tools/call",
        json={"name": "get_dashboard_stats", "arguments": {}},
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Dashboard tool test SUCCESS!")
        print(f"Result: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ HTTP {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {str(e)}")
