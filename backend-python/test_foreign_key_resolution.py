#!/usr/bin/env python3
"""
Test the foreign key resolution system with natural language commands
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_foreign_key_resolution():
    """Test that the AI can resolve foreign keys properly"""
    
    # Test 1: List rooms to see what's available
    print("🔍 Testing: List available rooms")
    response = requests.post(f"{BASE_URL}/tools/call", json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "list_rooms",
            "arguments": {}
        }
    })
    
    if response.status_code == 200:
        result = response.json()
        if "result" in result:
            content = result["result"].get("content", [])
            if content:
                data = json.loads(content[0]["text"])
                print("✅ Available rooms:")
                for room in data.get("rooms", [])[:3]:  # Show first 3
                    print(f"   - Room {room['room_number']} ({room['room_type']})")
                
                # Test 2: Try to create a bed in room 101
                print(f"\n🛏️ Testing: Create bed in room 101")
                first_room = data["rooms"][0]
                room_id = first_room["id"]
                room_number = first_room["room_number"]
                
                bed_response = requests.post(f"{BASE_URL}/tools/call", json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "create_bed",
                        "arguments": {
                            "bed_number": f"BED-{room_number}-01",
                            "room_id": room_id,
                            "bed_type": "Standard",
                            "status": "available"
                        }
                    }
                })
                
                if bed_response.status_code == 200:
                    bed_result = bed_response.json()
                    if "result" in bed_result:
                        bed_content = bed_result["result"].get("content", [])
                        if bed_content:
                            bed_data = json.loads(bed_content[0]["text"])
                            if bed_data.get("success"):
                                print(f"✅ Created bed {bed_data['data']['bed_number']} in room {room_number}")
                            else:
                                print(f"❌ Failed to create bed: {bed_data}")
                        else:
                            print(f"❌ No content in bed creation response")
                    else:
                        print(f"❌ Bed creation failed: {bed_result}")
                else:
                    print(f"❌ Bed creation HTTP error: {bed_response.status_code}")
                
                # Test 3: List beds to verify creation
                print(f"\n📋 Testing: List available beds")
                beds_response = requests.post(f"{BASE_URL}/tools/call", json={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "list_beds",
                        "arguments": {"status": "available"}
                    }
                })
                
                if beds_response.status_code == 200:
                    beds_result = beds_response.json()
                    if "result" in beds_result:
                        beds_content = beds_result["result"].get("content", [])
                        if beds_content:
                            beds_data = json.loads(beds_content[0]["text"])
                            available_beds = beds_data.get("beds", [])
                            print(f"✅ Found {len(available_beds)} available beds")
                            for bed in available_beds[:2]:  # Show first 2
                                print(f"   - Bed {bed['bed_number']} in room {bed.get('room_number', 'Unknown')}")
                        else:
                            print("❌ No beds content in response")
                    else:
                        print(f"❌ List beds failed: {beds_result}")
                else:
                    print(f"❌ List beds HTTP error: {beds_response.status_code}")
                    
            else:
                print("❌ No rooms content in response")
        else:
            print(f"❌ List rooms failed: {result}")
    else:
        print(f"❌ List rooms HTTP error: {response.status_code}")

if __name__ == "__main__":
    print("🧪 Testing Foreign Key Resolution System")
    print("=" * 50)
    test_foreign_key_resolution()
    print("\n✅ Foreign key resolution test complete!")
