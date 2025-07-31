"""
Hospital Management System MCP Client (Python)
Clean CRUD client for interacting with the database-only server.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    import inquirer
    # Import server functions directly for testing
    from server import (
        create_user, create_random_user, get_user_by_id, 
        list_users, delete_user, update_user, load_users
    )
except ImportError as e:
    missing_deps = []
    if "google" in str(e):
        missing_deps.append("google-generativeai")
    if "inquirer" in str(e):
        missing_deps.append("inquirer")
    if "dotenv" in str(e):
        missing_deps.append("python-dotenv")
    
    print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
    print("\n📦 Please install dependencies:")
    print(f"pip install {' '.join(missing_deps)}")
    sys.exit(1)

# Load environment variables
load_dotenv()

class HospitalMCPClient:
    """Hospital Management System MCP Client - Clean CRUD Interface"""
    
    def __init__(self):
        # Configure Google Generative AI
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            print("ℹ️  Note: GEMINI_API_KEY not found. AI features will be disabled.")
            self.model = None
        
        # Define available CRUD tools
        self.tools = [
            {
                "name": "create-user",
                "description": "Create a new user in the database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "User's full name"},
                        "email": {"type": "string", "description": "User's email address"},
                        "address": {"type": "string", "description": "User's address"},
                        "phone": {"type": "string", "description": "User's phone number"}
                    },
                    "required": ["name", "email", "address", "phone"]
                },
                "function": create_user
            },
            {
                "name": "create-random-user",
                "description": "Create a random user with fake data",
                "inputSchema": {"type": "object", "properties": {}},
                "function": create_random_user
            },
            {
                "name": "get-user-by-id",
                "description": "Get a specific user by their ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "integer", "description": "User ID"}
                    },
                    "required": ["user_id"]
                },
                "function": get_user_by_id
            },
            {
                "name": "list-users",
                "description": "List all users in the system",
                "inputSchema": {"type": "object", "properties": {}},
                "function": list_users
            },
            {
                "name": "delete-user",
                "description": "Delete a user from the database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "integer", "description": "User ID to delete"}
                    },
                    "required": ["user_id"]
                },
                "function": delete_user
            },
            {
                "name": "update-user",
                "description": "Update an existing user's information",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "integer", "description": "User ID to update"},
                        "name": {"type": "string", "description": "New name"},
                        "email": {"type": "string", "description": "New email"},
                        "address": {"type": "string", "description": "New address"},
                        "phone": {"type": "string", "description": "New phone"}
                    },
                    "required": ["user_id"]
                },
                "function": update_user
            }
        ]
        
        # Define available resources (simplified to match CRUD-only server)
        self.resources = [
            {
                "uri": "users://all",
                "name": "All Users",
                "description": "Get all users data from the database",
                "function": list_users  # Using list_users instead of get_all_users
            },
            {
                "uri": "users://{user_id}/profile",
                "name": "User Profile", 
                "description": "Get a user's details from the database",
                "function": get_user_by_id  # Using get_user_by_id instead of get_user_profile
            }
        ]

    async def main(self):
        """Main client loop - focused on CRUD operations"""
        print("🏥 Hospital Management System - CRUD Client")
        print("You are connected to the database!")
        
        while True:
            try:
                # Main menu selection
                questions = [
                    inquirer.List('option',
                                message="What would you like to do?",
                                choices=[
                                    'Query (AI-powered)', 
                                    'CRUD Tools', 
                                    'View Data', 
                                    'Exit'
                                ],
                    ),
                ]
                answers = inquirer.prompt(questions)
                
                if not answers or answers['option'] == 'Exit':
                    break
                
                option = answers['option']
                
                if option == "CRUD Tools":
                    await self.handle_tools()
                elif option == "View Data":
                    await self.handle_resources()
                elif option == "Query (AI-powered)":
                    await self.handle_query()
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    async def handle_tools(self):
        """Handle CRUD tools selection and execution"""
        if not self.tools:
            print("No tools available.")
            return
        
        # Create more user-friendly tool choices
        tool_choices = []
        for tool in self.tools:
            if tool['name'] == 'create-user':
                tool_choices.append('Create New User')
            elif tool['name'] == 'create-random-user':
                tool_choices.append('Create Random User (Demo)')
            elif tool['name'] == 'get-user-by-id':
                tool_choices.append('Get User by ID')
            elif tool['name'] == 'list-users':
                tool_choices.append('List All Users')
            elif tool['name'] == 'update-user':
                tool_choices.append('Update User')
            elif tool['name'] == 'delete-user':
                tool_choices.append('Delete User')
            else:
                tool_choices.append(f"{tool['name']} - {tool['description']}")
        
        # Select a tool
        questions = [
            inquirer.List('tool_choice',
                        message="Select a CRUD operation:",
                        choices=tool_choices + ['Back to Main Menu'],
            ),
        ]
        answers = inquirer.prompt(questions)
        
        if not answers or answers['tool_choice'] == 'Back to Main Menu':
            return
        
        # Map choice back to tool
        choice_to_tool = {
            'Create New User': 'create-user',
            'Create Random User (Demo)': 'create-random-user',
            'Get User by ID': 'get-user-by-id',
            'List All Users': 'list-users',
            'Update User': 'update-user',
            'Delete User': 'delete-user'
        }
        
        selected_choice = answers['tool_choice']
        tool_name = choice_to_tool.get(selected_choice)
        
        if tool_name:
            tool = next((t for t in self.tools if t['name'] == tool_name), None)
            if tool:
                await self.handle_tool(tool)

    async def handle_tool(self, tool: Dict[str, Any]):
        """Execute a specific CRUD tool with improved UX"""
        print(f"\n🔧 {tool['name'].replace('-', ' ').title()}")
        print(f"Description: {tool['description']}")
        
        # Special handling for tools that don't need parameters
        if tool['name'] == 'create-random-user':
            try:
                print("\n⏳ Creating random user...")
                result = tool['function']()
                print("✅ Success!")
                print(json.dumps(result, indent=2))
            except Exception as e:
                print(f"❌ Error: {e}")
            return
        
        if tool['name'] == 'list-users':
            try:
                print("\n⏳ Fetching all users...")
                result = tool['function']()
                print("✅ Success!")
                print(json.dumps(result, indent=2))
            except Exception as e:
                print(f"❌ Error: {e}")
            return
        
        # Collect arguments for other tools
        args = {}
        properties = tool['inputSchema'].get('properties', {})
        required = tool['inputSchema'].get('required', [])
        
        for key, value in properties.items():
            param_type = value.get('type', 'string')
            param_desc = value.get('description', '')
            is_required = key in required
            
            # Skip optional parameters for update operations if user doesn't want to change them
            if tool['name'] == 'update-user' and key != 'user_id' and not is_required:
                questions = [
                    inquirer.Confirm(
                        'update_field', 
                        message=f"Do you want to update {key}?", 
                        default=False
                    )
                ]
                update_answers = inquirer.prompt(questions)
                if not update_answers or not update_answers['update_field']:
                    continue
            
            prompt_text = f"Enter {key}"
            if param_desc:
                prompt_text += f" ({param_desc})"
            if is_required:
                prompt_text += " [REQUIRED]"
            
            questions = [inquirer.Text('value', message=prompt_text)]
            answers = inquirer.prompt(questions)
            
            if answers and answers['value']:
                # Convert to appropriate type
                if param_type == 'integer':
                    try:
                        args[key] = int(answers['value'])
                    except ValueError:
                        print(f"❌ {key} must be an integer!")
                        return
                elif param_type == 'boolean':
                    args[key] = answers['value'].lower() in ['true', '1', 'yes', 'y']
                else:
                    args[key] = answers['value']
            elif is_required:
                print(f"❌ {key} is required!")
                return
        
        try:
            # Call the tool function
            print(f"\n⏳ Executing {tool['name']}...")
            result = tool['function'](**args)
            
            # Display result
            print("✅ Success!")
            if hasattr(result, 'model_dump'):
                # Pydantic model
                print(json.dumps(result.model_dump(), indent=2))
            else:
                # Regular dict/object
                print(json.dumps(result, indent=2))
                
        except Exception as e:
            print(f"❌ Error executing tool: {e}")

    async def handle_resources(self):
        """Handle data viewing options"""
        if not self.resources:
            print("No data views available.")
            return
        
        # Create user-friendly choices
        choices = [
            'View All Users',
            'View User Profile by ID',
            'Back to Main Menu'
        ]
        
        questions = [
            inquirer.List('view_choice',
                        message="What data would you like to view?",
                        choices=choices,
            ),
        ]
        answers = inquirer.prompt(questions)
        
        if not answers or answers['view_choice'] == 'Back to Main Menu':
            return
        
        choice = answers['view_choice']
        
        if choice == 'View All Users':
            resource = self.resources[0]  # users://all
            await self.handle_resource(resource)
        elif choice == 'View User Profile by ID':
            resource = self.resources[1]  # users://{user_id}/profile
            await self.handle_resource(resource)

    async def handle_resource(self, resource: Dict[str, Any]):
        """Access a specific resource - simplified for CRUD operations"""
        print(f"\n📂 Accessing resource: {resource['uri']}")
        
        try:
            if "user_id" in resource['uri']:
                # Resource with user ID parameter
                questions = [
                    inquirer.Text('user_id', message="Enter User ID"),
                ]
                answers = inquirer.prompt(questions)
                if answers and answers['user_id']:
                    try:
                        user_id = int(answers['user_id'])
                        result = resource['function'](user_id)
                    except ValueError:
                        print("❌ User ID must be an integer!")
                        return
                else:
                    print("❌ User ID is required!")
                    return
            else:
                # Resource without parameters (like all users)
                result = resource['function']()
            
            # Display result
            print(json.dumps(result, indent=2))
                
        except Exception as e:
            print(f"❌ Error accessing resource: {e}")

    async def handle_query(self):
        """Handle AI-powered queries for hospital management"""
        if not self.model:
            print("❌ AI features not available. Please set GEMINI_API_KEY in your .env file.")
            return
        
        # Get query from user
        questions = [
            inquirer.Text('query', message="🤖 Ask me anything about the hospital management system:"),
        ]
        answers = inquirer.prompt(questions)
        
        if not answers or not answers['query']:
            return
        
        query = answers['query']
        
        try:
            # Create tool descriptions for AI
            tool_descriptions = [
                "create-user: Create a new user with name, email, address, phone",
                "create-random-user: Generate a random user for testing",
                "get-user-by-id: Find a specific user by their ID number", 
                "list-users: Show all users in the system",
                "update-user: Modify an existing user's information",
                "delete-user: Remove a user from the system"
            ]
            
            # Enhanced prompt for hospital management context
            enhanced_prompt = f"""
You are an AI assistant for a Hospital Management System with a PostgreSQL database.

Available CRUD operations:
{chr(10).join(tool_descriptions)}

The system manages patient/user data with fields: id, name, email, address, phone.

User question: {query}

Please provide a helpful response. If the user needs to perform any database operations, 
suggest which tool would be appropriate and what information they would need to provide.
Be conversational and helpful.
"""
            
            # Generate AI response
            print("\n🤖 Thinking...")
            response = self.model.generate_content(enhanced_prompt)
            
            # Display result
            print(f"\n🤖 AI Assistant:\n{response.text}")
            
            # Check if AI suggests tool usage
            tool_names = [tool['name'] for tool in self.tools]
            if any(tool_name.replace('-', ' ') in response.text.lower() or 
                   tool_name in response.text.lower() for tool_name in tool_names):
                
                questions = [
                    inquirer.Confirm(
                        'use_tools', 
                        message="💡 Would you like to perform the suggested operation?", 
                        default=True
                    ),
                ]
                answers = inquirer.prompt(questions)
                
                if answers and answers['use_tools']:
                    await self.handle_tools()
                    
        except Exception as e:
            print(f"❌ Error processing query: {e}")


async def main():
    """Main entry point - equivalent of TypeScript main()"""
    client = HospitalMCPClient()
    
    try:
        # Run main client loop
        await client.main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    
    return 0


if __name__ == "__main__":
    # Check for required dependencies
    missing_deps = []
    try:
        import google.generativeai
    except ImportError:
        missing_deps.append("google-generativeai")
    
    try:
        import inquirer
    except ImportError:
        missing_deps.append("inquirer")
    
    try:
        import dotenv
    except ImportError:
        missing_deps.append("python-dotenv")
    
    if missing_deps:
        print(f"❌ Missing required dependencies: {', '.join(missing_deps)}")
        print("\n📦 Please install dependencies:")
        print(f"pip install {' '.join(missing_deps)}")
        sys.exit(1)
    
    # Run the client
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
