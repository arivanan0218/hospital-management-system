"""Hospital Management System MCP Server using FastMCP with PostgreSQL."""

import random
from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from mcp.server.fastmcp import FastMCP

# Import database modules
try:
    from database import User as DBUser, SessionLocal, create_tables, migrate_json_to_db, test_connection
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("⚠️  Database modules not available. Install dependencies: pip install sqlalchemy psycopg2-binary")

# Initialize FastMCP server
mcp = FastMCP("hospital-management-system")

# Data models using Pydantic for structured output
class User(BaseModel):
    """User information structure."""
    id: int
    name: str = Field(description="User's full name")
    email: str = Field(description="User's email address")
    address: str = Field(description="User's address")
    phone: str = Field(description="User's phone number")


class UserCreateInput(BaseModel):
    """Input structure for creating a new user."""
    name: str = Field(description="User's full name")
    email: str = Field(description="User's email address")
    address: str = Field(description="User's address")
    phone: str = Field(description="User's phone number")


class UserCreationResult(BaseModel):
    """Result of user creation."""
    success: bool
    message: str
    user_id: int | None = None


# Database helper functions
def get_db_session() -> Session:
    """Get database session."""
    return SessionLocal()


def load_users_from_db() -> List[Dict[str, Any]]:
    """Load users from PostgreSQL database."""
    if not DATABASE_AVAILABLE:
        print("Database not available. Please install dependencies: pip install sqlalchemy psycopg2-binary")
        return []
    
    try:
        db = get_db_session()
        users = db.query(DBUser).all()
        db.close()
        
        return [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "address": user.address,
                "phone": user.phone
            }
            for user in users
        ]
    except Exception as e:
        print(f"Database error: {e}")
        return []


# Main data access function
def load_users() -> List[Dict[str, Any]]:
    """Load users from PostgreSQL database."""
    return load_users_from_db()


@mcp.resource("users://all")
def get_all_users() -> Dict[str, Any]:
    """Get all users data from the database."""
    if not DATABASE_AVAILABLE:
        return {
            "error": "Database not available. Please install dependencies: pip install sqlalchemy psycopg2-binary",
            "data": [],
            "count": 0
        }
    
    users = load_users()
    return {
        "description": "All users in the hospital management system",
        "data": users,
        "count": len(users)
    }


@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Get a user's details from the database."""
    if not DATABASE_AVAILABLE:
        return {
            "error": "Database not available. Please install dependencies: pip install sqlalchemy psycopg2-binary"
        }
    
    try:
        user_id_int = int(user_id)
        users = load_users()
        
        user = next((u for u in users if u.get("id") == user_id_int), None)
        
        if user is None:
            return {
                "error": "User not found",
                "user_id": user_id_int
            }
        
        return {
            "description": f"Profile for user {user_id}",
            "data": user
        }
    
    except ValueError:
        return {
            "error": "Invalid user ID format",
            "user_id": user_id
        }


@mcp.tool()
def save_user_to_db(user_data: Dict[str, Any]) -> bool:
    """Save a single user to PostgreSQL database."""
    if not DATABASE_AVAILABLE:
        print("Database not available. Please install dependencies: pip install sqlalchemy psycopg2-binary")
        return False
    
    try:
        db = get_db_session()
        db_user = DBUser(
            name=user_data["name"],
            email=user_data["email"],
            address=user_data["address"],
            phone=user_data["phone"]
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db.close()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False


def update_user_in_db(user_id: int, user_data: Dict[str, Any]) -> bool:
    """Update user in PostgreSQL database."""
    if not DATABASE_AVAILABLE:
        print("Database not available. Please install dependencies: pip install sqlalchemy psycopg2-binary")
        return False
    
    try:
        db = get_db_session()
        db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if db_user:
            if "name" in user_data:
                db_user.name = user_data["name"]
            if "email" in user_data:
                db_user.email = user_data["email"]
            if "address" in user_data:
                db_user.address = user_data["address"]
            if "phone" in user_data:
                db_user.phone = user_data["phone"]
            db.commit()
        db.close()
        return db_user is not None
    except Exception as e:
        print(f"Database error: {e}")
        return False


def delete_user_from_db(user_id: int) -> bool:
    """Delete user from PostgreSQL database."""
    if not DATABASE_AVAILABLE:
        print("Database not available. Please install dependencies: pip install sqlalchemy psycopg2-binary")
        return False
    
    try:
        db = get_db_session()
        db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if db_user:
            db.delete(db_user)
            db.commit()
        db.close()
        return db_user is not None
    except Exception as e:
        print(f"Database error: {e}")
        return False


def create_user(name: str, email: str, address: str, phone: str) -> UserCreationResult:
    """Create a new user in the database."""
    if not DATABASE_AVAILABLE:
        return UserCreationResult(
            success=False,
            message="Database not available. Please install dependencies: pip install sqlalchemy psycopg2-binary",
            user_id=None
        )
    
    try:
        user_data = {
            "name": name,
            "email": email,
            "address": address,
            "phone": phone
        }
        
        # Save to PostgreSQL
        db = get_db_session()
        db_user = DBUser(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        user_id = db_user.id
        db.close()
        
        return UserCreationResult(
            success=True,
            message=f"User {user_id} created successfully",
            user_id=user_id
        )
        
    except Exception as e:
        return UserCreationResult(
            success=False,
            message=f"Failed to create user: {str(e)}",
            user_id=None
        )


@mcp.tool()
def create_random_user() -> UserCreationResult:
    """Create a random user with fake data."""
    import random
    
    # Sample data for generating random users
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Edward", "Fiona", "George", "Hannah"]
    last_names = ["Johnson", "Smith", "Brown", "Davis", "Wilson", "Miller", "Moore", "Taylor"]
    domains = ["gmail.com", "yahoo.com", "outlook.com", "example.com"]
    streets = ["Main St", "Oak St", "Maple St", "Pine St", "Elm St", "Cedar St"]
    cities = ["Springfield", "Franklin", "Georgetown", "Madison", "Clinton"]
    states = ["IL", "OH", "TX", "CA", "NY", "FL"]
    
    # Generate random user data
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    name = f"{first_name} {last_name}"
    
    email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}"
    
    street_num = random.randint(100, 9999)
    street = random.choice(streets)
    city = random.choice(cities)
    state = random.choice(states)
    zip_code = random.randint(10000, 99999)
    address = f"{street_num} {street}, {city}, {state} {zip_code}"
    
    area_code = random.randint(200, 999)
    exchange = random.randint(200, 999)
    number = random.randint(1000, 9999)
    phone = f"({area_code}) {exchange}-{number}"
    
    return create_user(name, email, address, phone)


@mcp.tool()
def get_user_by_id(user_id: int) -> Dict[str, Any]:
    """Get a specific user by their ID."""
    if not DATABASE_AVAILABLE:
        return {
            "error": "Database not available. Please install dependencies: pip install sqlalchemy psycopg2-binary"
        }
    
    users = load_users()
    user = next((u for u in users if u.get("id") == user_id), None)
    
    if user is None:
        return {"error": "User not found", "user_id": user_id}
    
    return {"data": user}


@mcp.tool()
def list_users() -> Dict[str, Any]:
    """List all users in the system."""
    if not DATABASE_AVAILABLE:
        return {
            "error": "Database not available. Please install dependencies: pip install sqlalchemy psycopg2-binary",
            "users": [],
            "count": 0
        }
    
    users = load_users()
    return {
        "users": users,
        "count": len(users),
        "message": f"Found {len(users)} users in the system"
    }


@mcp.tool()
def delete_user(user_id: int) -> Dict[str, Any]:
    """Delete a user from the database."""
    if not DATABASE_AVAILABLE:
        return {
            "success": False,
            "message": "Database not available. Please install dependencies: pip install sqlalchemy psycopg2-binary"
        }
    
    try:
        success = delete_user_from_db(user_id)
        
        if not success:
            return {
                "success": False,
                "message": f"User with ID {user_id} not found"
            }
        
        return {
            "success": True,
            "message": f"User {user_id} deleted successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to delete user: {str(e)}"
        }


@mcp.tool()
def update_user(user_id: int, name: str = None, email: str = None, 
                address: str = None, phone: str = None) -> Dict[str, Any]:
    """Update an existing user's information."""
    if not DATABASE_AVAILABLE:
        return {
            "success": False,
            "message": "Database not available. Please install dependencies: pip install sqlalchemy psycopg2-binary"
        }
    
    try:
        # Prepare update data
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if email is not None:
            update_data["email"] = email
        if address is not None:
            update_data["address"] = address
        if phone is not None:
            update_data["phone"] = phone
        
        if not update_data:
            return {
                "success": False,
                "message": "No fields provided for update"
            }
        
        success = update_user_in_db(user_id, update_data)
        
        if not success:
            return {
                "success": False,
                "message": f"User with ID {user_id} not found"
            }
        
        # Get updated user data
        users = load_users()
        updated_user = next((u for u in users if u.get("id") == user_id), None)
        
        return {
            "success": True,
            "message": f"User {user_id} updated successfully",
            "user": updated_user
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to update user: {str(e)}"
        }


# Resource functions for client access (not MCP tools, but helper functions)
def get_all_users() -> dict:
    """Get all users data from the database (resource function)."""
    if not DATABASE_AVAILABLE:
        return {
            "error": "Database not available. Please install dependencies: pip install sqlalchemy psycopg2-binary"
        }
    
    try:
        users = load_users()
        return {
            "users": users,
            "total_count": len(users),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


def get_user_profile(user_id: int) -> dict:
    """Get a user's details from the database (resource function)."""
    if not DATABASE_AVAILABLE:
        return {
            "error": "Database not available. Please install dependencies: pip install sqlalchemy psycopg2-binary"
        }
    
    try:
        users = load_users()
        
        for user in users:
            if user['id'] == int(user_id):
                return {
                    "profile": user,
                    "timestamp": datetime.now().isoformat()
                }
        
        return {"error": f"User with ID {user_id} not found"}
        
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
