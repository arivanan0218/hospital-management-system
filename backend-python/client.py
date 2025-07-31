#!/usr/bin/env python3
"""
Hospital Management System MCP Client (Python)
Exact equivalent of client.ts functionality using direct server function calls.
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
        list_users, delete_user, update_user,
        get_all_users, get_user_profile
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
    """Hospital Management System MCP Client - Python equivalent of client.ts"""
    
    def __init__(self):
        # Configure Google Generative AI
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            print("Warning: GEMINI_API_KEY not found. AI features will be disabled.")
            self.model = None
        
        # Define available tools (equivalent to MCP server tools)
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
        
        # Define available resources (equivalent to MCP server resources)
        self.resources = [
            {
                "uri": "users://all",
                "name": "All Users",
                "description": "Get all users data from the database",
                "function": get_all_users
            },
            {
                "uri": "users://{user_id}/profile",
                "name": "User Profile", 
                "description": "Get a user's details from the database",
                "function": get_user_profile
            }
        ]
        
        # No prompts defined in the original server
        self.prompts = []

    async def main(self):
        """Main client loop - exact equivalent of TypeScript main()"""
        print("You are connected!")
        
        while True:
            try:
                # Main menu selection (equivalent to TypeScript select)
                questions = [
                    inquirer.List('option',
                                message="What would you like to do",
                                choices=['Query', 'Tools', 'Resources', 'Prompts', 'Exit'],
                    ),
                ]
                answers = inquirer.prompt(questions)
                
                if not answers or answers['option'] == 'Exit':
                    break
                
                option = answers['option']
                
                if option == "Tools":
                    await self.handle_tools()
                elif option == "Resources":
                    await self.handle_resources()
                elif option == "Prompts":
                    await self.handle_prompts()
                elif option == "Query":
                    await self.handle_query()
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    async def handle_tools(self):
        """Handle tools selection and execution - equivalent to TypeScript Tools case"""
        if not self.tools:
            print("No tools available.")
            return
        
        # Select a tool (equivalent to TypeScript select for tools)
        questions = [
            inquirer.List('tool_name',
                        message="Select a tool",
                        choices=[f"{tool['name']} - {tool['description']}" for tool in self.tools],
            ),
        ]
        answers = inquirer.prompt(questions)
        
        if not answers:
            return
        
        # Find selected tool
        selected_display = answers['tool_name']
        tool = None
        for t in self.tools:
            if selected_display.startswith(t['name']):
                tool = t
                break
        
        if tool is None:
            print("Tool not found.")
        else:
            await self.handle_tool(tool)

    async def handle_tool(self, tool: Dict[str, Any]):
        """Execute a specific tool - equivalent to TypeScript handleTool()"""
        print(f"\n🔧 Executing tool: {tool['name']}")
        print(f"Description: {tool['description']}")
        
        # Collect arguments (equivalent to TypeScript input collection)
        args = {}
        properties = tool['inputSchema'].get('properties', {})
        required = tool['inputSchema'].get('required', [])
        
        for key, value in properties.items():
            param_type = value.get('type', 'string')
            param_desc = value.get('description', '')
            is_required = key in required
            
            prompt_text = f"Enter value for {key} ({param_type})"
            if param_desc:
                prompt_text += f" - {param_desc}"
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
            result = tool['function'](**args)
            
            # Display result (equivalent to TypeScript console.log)
            if hasattr(result, 'model_dump'):
                # Pydantic model
                print(json.dumps(result.model_dump(), indent=2))
            else:
                # Regular dict/object
                print(json.dumps(result, indent=2))
                
        except Exception as e:
            print(f"❌ Error executing tool: {e}")

    async def handle_resources(self):
        """Handle resources selection and access - equivalent to TypeScript Resources case"""
        if not self.resources:
            print("No resources available.")
            return
        
        # Select a resource (equivalent to TypeScript select for resources)
        questions = [
            inquirer.List('resource_uri',
                        message="Select a resource",
                        choices=[f"{resource['name']} - {resource['description']}" for resource in self.resources],
            ),
        ]
        answers = inquirer.prompt(questions)
        
        if not answers:
            return
        
        # Find selected resource
        selected_display = answers['resource_uri']
        resource = None
        for r in self.resources:
            if selected_display.startswith(r['name']):
                resource = r
                break
        
        if resource is None:
            print("Resource not found.")
        else:
            await self.handle_resource(resource)

    async def handle_resource(self, resource: Dict[str, Any]):
        """Access a specific resource - equivalent to TypeScript handleResource()"""
        print(f"\n📂 Accessing resource: {resource['uri']}")
        
        # Handle parameterized URIs (equivalent to TypeScript param handling)
        uri = resource['uri']
        final_args = {}
        
        if "{" in uri and "}" in uri:
            import re
            params = re.findall(r'\{([^}]+)\}', uri)
            for param in params:
                questions = [
                    inquirer.Text('param_value', message=f"Enter value for {param}"),
                ]
                answers = inquirer.prompt(questions)
                if answers and answers['param_value']:
                    final_args[param] = answers['param_value']
        
        try:
            # Call the resource function
            if final_args:
                # Resource with parameters (like user profile)
                result = resource['function'](**final_args)
            else:
                # Resource without parameters (like all users)
                result = resource['function']()
            
            # Display result (equivalent to TypeScript JSON.stringify)
            print(json.dumps(result, indent=2))
                
        except Exception as e:
            print(f"❌ Error accessing resource: {e}")

    async def handle_prompts(self):
        """Handle prompts - equivalent to TypeScript Prompts case"""
        if not self.prompts:
            print("No prompts available.")
            return
        
        # Would handle prompts here if we had any defined
        print("No prompts are currently defined in the server.")

    async def handle_query(self):
        """Handle AI-powered queries - equivalent to TypeScript handleQuery()"""
        if not self.model:
            print("❌ AI features not available. Please set GEMINI_API_KEY.")
            return
        
        # Get query from user (equivalent to TypeScript input)
        questions = [
            inquirer.Text('query', message="Enter your query"),
        ]
        answers = inquirer.prompt(questions)
        
        if not answers or not answers['query']:
            return
        
        query = answers['query']
        
        try:
            # Create tool descriptions for AI (equivalent to TypeScript tools.reduce)
            tool_descriptions = []
            for tool in self.tools:
                tool_desc = f"Tool: {tool['name']} - {tool['description']}"
                params = list(tool['inputSchema'].get('properties', {}).keys())
                if params:
                    tool_desc += f" (Parameters: {', '.join(params)})"
                tool_descriptions.append(tool_desc)
            
            # Enhanced prompt (equivalent to TypeScript generateText prompt)
            enhanced_prompt = f"""
You are helping with a Hospital Management System. Available tools:
{chr(10).join(tool_descriptions)}

User query: {query}

Please provide a helpful response. If you think any tools should be used to answer the query, please suggest which tool(s) and what parameters would be needed.
"""
            
            # Generate AI response (equivalent to TypeScript generateText)
            response = self.model.generate_content(enhanced_prompt)
            
            # Display result (equivalent to TypeScript console.log)
            print(f"\n🤖 AI Response:\n{response.text}")
            
            # Check if AI suggests tool usage
            if any(tool['name'] in response.text.lower() for tool in self.tools):
                questions = [
                    inquirer.Confirm('use_tools', message="The AI suggested using tools. Would you like to go to the tools menu?", default=True),
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
