"""
MCP Client - HTTP Client for testing the MCP Bridge

This module provides a simple HTTP client to test the MCP bridge functionality.
It can be used to verify that the bridge is working correctly by making HTTP
requests to the bridge server.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional

import httpx


class MCPHttpClient:
    """HTTP client for the MCP Bridge"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the bridge is healthy"""
        response = await self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        response = await self.client.get(f"{self.base_url}/tools")
        response.raise_for_status()
        return response.json()
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool"""
        response = await self.client.post(
            f"{self.base_url}/tools/{tool_name}",
            json=arguments
        )
        response.raise_for_status()
        return response.json()
    
    # User operations
    async def create_user(self, username: str, email: str, password_hash: str, 
                         role: str, first_name: str, last_name: str, 
                         phone: str = None) -> Dict[str, Any]:
        """Create a new user"""
        data = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone
        }
        response = await self.client.post(f"{self.base_url}/users", json=data)
        response.raise_for_status()
        return response.json()
    
    async def list_users(self) -> Dict[str, Any]:
        """List all users"""
        response = await self.client.get(f"{self.base_url}/users")
        response.raise_for_status()
        return response.json()
    
    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user by ID"""
        response = await self.client.get(f"{self.base_url}/users/{user_id}")
        response.raise_for_status()
        return response.json()
    
    # Patient operations
    async def create_patient(self, patient_number: str, first_name: str, 
                           last_name: str, date_of_birth: str, **kwargs) -> Dict[str, Any]:
        """Create a new patient"""
        data = {
            "patient_number": patient_number,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": date_of_birth,
            **kwargs
        }
        response = await self.client.post(f"{self.base_url}/patients", json=data)
        response.raise_for_status()
        return response.json()
    
    async def list_patients(self) -> Dict[str, Any]:
        """List all patients"""
        response = await self.client.get(f"{self.base_url}/patients")
        response.raise_for_status()
        return response.json()
    
    async def get_patient(self, patient_id: str) -> Dict[str, Any]:
        """Get patient by ID"""
        response = await self.client.get(f"{self.base_url}/patients/{patient_id}")
        response.raise_for_status()
        return response.json()
    
    # Department operations
    async def create_department(self, name: str, **kwargs) -> Dict[str, Any]:
        """Create a new department"""
        data = {"name": name, **kwargs}
        response = await self.client.post(f"{self.base_url}/departments", json=data)
        response.raise_for_status()
        return response.json()
    
    async def list_departments(self) -> Dict[str, Any]:
        """List all departments"""
        response = await self.client.get(f"{self.base_url}/departments")
        response.raise_for_status()
        return response.json()
    
    async def get_department(self, department_id: str) -> Dict[str, Any]:
        """Get department by ID"""
        response = await self.client.get(f"{self.base_url}/departments/{department_id}")
        response.raise_for_status()
        return response.json()
    
    # Bed operations
    async def create_bed(self, bed_number: str, room_id: str, **kwargs) -> Dict[str, Any]:
        """Create a new bed"""
        data = {"bed_number": bed_number, "room_id": room_id, **kwargs}
        response = await self.client.post(f"{self.base_url}/beds", json=data)
        response.raise_for_status()
        return response.json()
    
    async def list_beds(self, status: str = None) -> Dict[str, Any]:
        """List all beds"""
        params = {"status": status} if status else {}
        response = await self.client.get(f"{self.base_url}/beds", params=params)
        response.raise_for_status()
        return response.json()
    
    async def assign_bed(self, bed_id: str, patient_id: str, **kwargs) -> Dict[str, Any]:
        """Assign a bed to a patient"""
        data = {"patient_id": patient_id, **kwargs}
        response = await self.client.post(f"{self.base_url}/beds/{bed_id}/assign", json=data)
        response.raise_for_status()
        return response.json()
    
    async def discharge_bed(self, bed_id: str, **kwargs) -> Dict[str, Any]:
        """Discharge a patient from a bed"""
        response = await self.client.post(f"{self.base_url}/beds/{bed_id}/discharge", json=kwargs)
        response.raise_for_status()
        return response.json()


async def main():
    """Example usage of the MCP HTTP client"""
    client = MCPHttpClient()
    
    try:
        # Health check
        print("Checking bridge health...")
        health = await client.health_check()
        print(f"Bridge health: {health}")
        
        # List tools
        print("\nListing available tools...")
        tools = await client.list_tools()
        print(f"Available tools: {len(tools['tools'])}")
        for tool in tools['tools'][:5]:  # Show first 5 tools
            print(f"  - {tool.get('name', 'Unknown')}")
        
        # Test user operations
        print("\nTesting user operations...")
        
        # List existing users
        users = await client.list_users()
        print(f"Current users count: {users.get('count', 0)}")
        
        # Create a test user
        try:
            user_result = await client.create_user(
                username="test_user_bridge",
                email="test@bridge.com",
                password_hash="hashed_password",
                role="nurse",
                first_name="Test",
                last_name="User",
                phone="555-0123"
            )
            print(f"Created user: {user_result}")
        except Exception as e:
            print(f"User creation failed (might already exist): {e}")
        
        # List departments
        print("\nListing departments...")
        departments = await client.list_departments()
        print(f"Departments count: {departments.get('count', 0)}")
        
        # List patients
        print("\nListing patients...")
        patients = await client.list_patients()
        print(f"Patients count: {patients.get('count', 0)}")
        
        # List beds
        print("\nListing beds...")
        beds = await client.list_beds()
        print(f"Beds count: {beds.get('count', 0)}")
        
        print("\nBridge test completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        sys.exit(1)
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
