#!/usr/bin/env python3
"""
Hospital Management System MCP Client (Python)
Exact equivalent of client.ts with full MCP protocol support.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.types import (
        CallToolRequest, 
        CallToolResult,
        GetPromptRequest,
        GetPromptResult,
        ListPromptsRequest,
        ListPromptsResult,
        ListResourcesRequest, 
        ListResourcesResult,
        ListToolsRequest,
        ListToolsResult,
        ReadResourceRequest,
        ReadResourceResult,
        Tool,
        Prompt,
        Resource,
    )
    import google.generativeai as genai
    from dotenv import load_dotenv
    import inquirer
except ImportError as e:
    missing_deps = []
    if "mcp" in str(e):
        missing_deps.append("mcp")
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
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.read_stream = None
        self.write_stream = None
        self.tools: List[Tool] = []
        self.resources: List[Resource] = []
        self.prompts: List[Prompt] = []
        self.resource_templates: List[Any] = []
        
        # Configure Google Generative AI
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            print("Warning: GEMINI_API_KEY not found. AI features will be disabled.")
            self.model = None

    async def connect(self, command: str = "python", args: List[str] = None):
        """Connect to the MCP server."""
        if args is None:
            args = ["server.py"]
        
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=None
        )
        
        try:
            # Connect to server using async context manager
            self.transport = await stdio_client(server_params)
            self.read_stream, self.write_stream = self.transport.__aenter__()
            self.session = ClientSession(self.read_stream, self.write_stream)
            
            # Initialize the session
            init_result = await self.session.initialize()
            
            # Load capabilities
            await self._load_capabilities()
            
            print("You are connected!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            return False

    async def _load_capabilities(self):
        """Load tools, resources, and prompts from the server."""
        if not self.session:
            return
        
        try:
            # List tools
            tools_result = await self.session.list_tools()
            self.tools = tools_result.tools if tools_result.tools else []
            
            # List resources
            resources_result = await self.session.list_resources()
            self.resources = resources_result.resources if resources_result.resources else []
            
            # List prompts
            prompts_result = await self.session.list_prompts()
            self.prompts = prompts_result.prompts if prompts_result.prompts else []
            
            # For now, we'll handle resource templates as empty
            self.resource_templates = []
            
        except Exception as e:
            print(f"⚠️  Error loading capabilities: {e}")

    async def main_loop(self):
        """Main client loop - exact equivalent of TypeScript version."""
        while True:
            try:
                # Main menu selection
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
                    await self.handle_tools_menu()
                elif option == "Resources":
                    await self.handle_resources_menu()
                elif option == "Prompts":
                    await self.handle_prompts_menu()
                elif option == "Query":
                    await self.handle_query()
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("👋 Goodbye!")

    async def handle_tools_menu(self):
        """Handle tools selection and execution."""
        if not self.tools:
            print("No tools available.")
            return
        
        # Create tool choices
        tool_choices = []
        for tool in self.tools:
            name = getattr(tool, 'title', None) or tool.name
            tool_choices.append((tool.name, f"{name} - {tool.description}"))
        
        questions = [
            inquirer.List('tool_name',
                        message="Select a tool",
                        choices=[choice[1] for choice in tool_choices],
            ),
        ]
        answers = inquirer.prompt(questions)
        
        if not answers:
            return
        
        # Find selected tool
        selected_display = answers['tool_name']
        tool_name = None
        for choice in tool_choices:
            if choice[1] == selected_display:
                tool_name = choice[0]
                break
        
        if tool_name:
            tool = next((t for t in self.tools if t.name == tool_name), None)
            if tool:
                await self.handle_tool(tool)
            else:
                print("Tool not found.")

    async def handle_tool(self, tool: Tool):
        """Execute a specific tool."""
        print(f"\n🔧 Executing tool: {tool.name}")
        print(f"Description: {tool.description}")
        
        # Collect arguments
        args = {}
        if hasattr(tool.inputSchema, 'properties') and tool.inputSchema.properties:
            for key, value in tool.inputSchema.properties.items():
                param_type = value.get('type', 'string') if isinstance(value, dict) else 'string'
                questions = [
                    inquirer.Text(key, message=f"Enter value for {key} ({param_type})"),
                ]
                answers = inquirer.prompt(questions)
                if answers and answers[key]:
                    # Convert to appropriate type
                    if param_type == 'integer':
                        try:
                            args[key] = int(answers[key])
                        except ValueError:
                            print(f"❌ {key} must be an integer!")
                            return
                    elif param_type == 'boolean':
                        args[key] = answers[key].lower() in ['true', '1', 'yes', 'y']
                    else:
                        args[key] = answers[key]
        
        try:
            # Call the tool
            result = await self.session.call_tool(tool.name, args)
            
            # Display result
            if result.content:
                for content in result.content:
                    if hasattr(content, 'text'):
                        print(content.text)
                    else:
                        print(str(content))
            else:
                print("No content returned")
                
        except Exception as e:
            print(f"❌ Error executing tool: {e}")

    async def handle_resources_menu(self):
        """Handle resources selection and access."""
        if not self.resources and not self.resource_templates:
            print("No resources available.")
            return
        
        # Create resource choices
        resource_choices = []
        for resource in self.resources:
            resource_choices.append((resource.uri, f"{resource.name} - {resource.description}"))
        
        for template in self.resource_templates:
            resource_choices.append((template.uriTemplate, f"{template.name} - {template.description}"))
        
        questions = [
            inquirer.List('resource_uri',
                        message="Select a resource",
                        choices=[choice[1] for choice in resource_choices],
            ),
        ]
        answers = inquirer.prompt(questions)
        
        if not answers:
            return
        
        # Find selected resource URI
        selected_display = answers['resource_uri']
        resource_uri = None
        for choice in resource_choices:
            if choice[1] == selected_display:
                resource_uri = choice[0]
                break
        
        if resource_uri:
            await self.handle_resource(resource_uri)

    async def handle_resource(self, uri: str):
        """Access a specific resource."""
        print(f"\n📂 Accessing resource: {uri}")
        
        # Handle parameterized URIs
        final_uri = uri
        import re
        param_matches = re.findall(r'\{([^}]+)\}', uri)
        
        if param_matches:
            for param_name in param_matches:
                questions = [
                    inquirer.Text('param_value', message=f"Enter value for {param_name}"),
                ]
                answers = inquirer.prompt(questions)
                if answers and answers['param_value']:
                    final_uri = final_uri.replace(f"{{{param_name}}}", answers['param_value'])
        
        try:
            result = await self.session.read_resource(final_uri)
            
            if result.contents:
                for content in result.contents:
                    if hasattr(content, 'text'):
                        try:
                            # Try to parse and pretty-print JSON
                            data = json.loads(content.text)
                            print(json.dumps(data, indent=2))
                        except json.JSONDecodeError:
                            print(content.text)
                    else:
                        print(str(content))
            else:
                print("No content found")
                
        except Exception as e:
            print(f"❌ Error accessing resource: {e}")

    async def handle_prompts_menu(self):
        """Handle prompts selection and execution."""
        if not self.prompts:
            print("No prompts available.")
            return
        
        # Create prompt choices
        prompt_choices = [(prompt.name, f"{prompt.name} - {prompt.description}") for prompt in self.prompts]
        
        questions = [
            inquirer.List('prompt_name',
                        message="Select a prompt",
                        choices=[choice[1] for choice in prompt_choices],
            ),
        ]
        answers = inquirer.prompt(questions)
        
        if not answers:
            return
        
        # Find selected prompt
        selected_display = answers['prompt_name']
        prompt_name = None
        for choice in prompt_choices:
            if choice[1] == selected_display:
                prompt_name = choice[0]
                break
        
        if prompt_name:
            prompt = next((p for p in self.prompts if p.name == prompt_name), None)
            if prompt:
                await self.handle_prompt(prompt)
            else:
                print("Prompt not found.")

    async def handle_prompt(self, prompt: Prompt):
        """Execute a specific prompt."""
        print(f"\n💭 Using prompt: {prompt.name}")
        print(f"Description: {prompt.description}")
        
        # Collect prompt arguments
        args = {}
        if prompt.arguments:
            for arg in prompt.arguments:
                questions = [
                    inquirer.Text('arg_value', message=f"Enter value for {arg.name}"),
                ]
                answers = inquirer.prompt(questions)
                if answers and answers['arg_value']:
                    args[arg.name] = answers['arg_value']
        
        try:
            result = await self.session.get_prompt(prompt.name, args)
            
            for message in result.messages:
                await self.handle_server_message_prompt(message)
                
        except Exception as e:
            print(f"❌ Error executing prompt: {e}")

    async def handle_server_message_prompt(self, message):
        """Handle server message prompt."""
        if not hasattr(message.content, 'type') or message.content.type != "text":
            return None
        
        print(message.content.text)
        
        questions = [
            inquirer.Confirm('run', message="Would you like to run the above prompt", default=True),
        ]
        answers = inquirer.prompt(questions)
        
        if not answers or not answers['run']:
            return None
        
        if not self.model:
            print("❌ AI model not available. Please set GEMINI_API_KEY.")
            return None
        
        try:
            response = self.model.generate_content(message.content.text)
            return response.text
        except Exception as e:
            print(f"❌ Error generating AI response: {e}")
            return None

    async def handle_query(self):
        """Handle AI-powered queries with tool integration."""
        if not self.model:
            print("❌ AI features not available. Please set GEMINI_API_KEY.")
            return
        
        questions = [
            inquirer.Text('query', message="Enter your query"),
        ]
        answers = inquirer.prompt(questions)
        
        if not answers or not answers['query']:
            return
        
        query = answers['query']
        
        try:
            # Create tool descriptions for the AI
            tool_info = []
            for tool in self.tools:
                tool_desc = f"Tool: {tool.name} - {tool.description}"
                if hasattr(tool.inputSchema, 'properties') and tool.inputSchema.properties:
                    params = list(tool.inputSchema.properties.keys())
                    tool_desc += f" (Parameters: {', '.join(params)})"
                tool_info.append(tool_desc)
            
            # Enhanced prompt with context
            enhanced_prompt = f"""
You are helping with a Hospital Management System. Available tools:
{chr(10).join(tool_info)}

User query: {query}

Please provide a helpful response. If you need to suggest using any tools, mention which tool and what parameters would be needed.
"""
            
            response = self.model.generate_content(enhanced_prompt)
            print(f"\n🤖 AI Response:\n{response.text}")
            
            # Check if AI suggests tool usage
            if any(tool.name.lower() in response.text.lower() for tool in self.tools):
                questions = [
                    inquirer.Confirm('use_tools', message="The AI suggested using tools. Would you like to go to the tools menu?", default=True),
                ]
                answers = inquirer.prompt(questions)
                
                if answers and answers['use_tools']:
                    await self.handle_tools_menu()
                    
        except Exception as e:
            print(f"❌ Error processing query: {e}")

    async def disconnect(self):
        """Disconnect from the server."""
        if self.session:
            # Clean up session
            self.session = None
            self.read_stream = None
            self.write_stream = None
            print("🔌 Disconnected from server")


async def main():
    """Main entry point - exact equivalent of TypeScript main()."""
    client = HospitalMCPClient()
    
    # Connect to server (pointing to Python server)
    connected = await client.connect("python", ["server.py"])
    if not connected:
        return 1
    
    try:
        # Run main loop
        await client.main_loop()
    except KeyboardInterrupt:
        print("\n🔌 Disconnecting...")
    finally:
        await client.disconnect()
    
    return 0


if __name__ == "__main__":
    # Check for required dependencies
    missing_deps = []
    try:
        import mcp
    except ImportError:
        missing_deps.append("mcp")
    
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
