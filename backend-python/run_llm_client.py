#!/usr/bin/env python3
"""
Hospital Management System with LLM Integration
Start script for the enhanced AI-powered client
"""

import asyncio
from client import HospitalManagementClient

async def main():
    """Main entry point for LLM-integrated hospital management system."""
    print("🏥 Hospital Management System with LLM Integration")
    print("=" * 55)
    print("🧠 Powered by Google Gemini AI")
    print("🤖 Natural Language Processing Enabled")
    print("=" * 55)
    
    client = HospitalManagementClient()
    
    if client.llm_model:
        print("✅ Google Gemini LLM initialized successfully")
        print("🎯 You can now ask questions in natural language!")
    else:
        print("⚠️ LLM not available - running in basic mode")
        print("💡 Add GEMINI_API_KEY to .env file for full AI capabilities")
    
    print("\n📋 Choose your mode:")
    print("1. Interactive Menu (All Features)")
    print("2. Natural Language Chat Mode")
    print("3. Run LLM Integration Demo")
    print("4. Test LLM Only")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            print("🚀 Starting interactive menu...")
            await client.run_interactive_mode()
        elif choice == "2":
            print("💬 Starting natural language chat mode...")
            await chat_mode(client)
        elif choice == "3":
            print("🧪 Running LLM integration demo...")
            await client.demo_llm_integration()
        elif choice == "4":
            print("🧠 Testing LLM only...")
            await test_llm_only(client)
        else:
            print("Invalid choice. Starting interactive menu...")
            await client.run_interactive_mode()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

async def chat_mode(client):
    """Natural language chat mode."""
    print("\n💬 === NATURAL LANGUAGE CHAT MODE ===")
    print("Ask me anything about hospital management in natural language!")
    print("Type 'exit', 'quit', or 'bye' to return to main menu")
    print("Type 'menu' to see available operations")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n🤖 You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Returning to main menu...")
                break
            elif user_input.lower() == 'menu':
                print("""
📋 Available Operations:
• Patient management: "show patients", "add a patient"
• Bed management: "check bed availability", "show beds"
• Staff info: "list staff members", "show departments"
• Equipment: "check equipment status", "list equipment"
• Supplies: "show inventory", "check low stock items"
• Analysis: "analyze hospital state", "give me an overview"
• AI features: "run autonomous management", "optimize resources"
                """)
                continue
            
            if user_input:
                print("🧠 AI: Processing your request...")
                response = await client.intelligent_query_handler(user_input)
                print(f"🤖 AI: {response}")
            else:
                print("Please enter a valid question.")
                
        except KeyboardInterrupt:
            print("\n👋 Returning to main menu...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_llm_only(client):
    """Test LLM functionality without MCP connection."""
    print("\n🧠 === LLM TEST MODE ===")
    
    if not client.llm_model:
        print("❌ LLM not available. Check GEMINI_API_KEY configuration.")
        return
    
    print("Testing Google Gemini LLM responses...")
    print("Type 'exit' to quit")
    
    while True:
        try:
            user_input = input("\n🧠 Test Query: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                break
            
            if user_input:
                prompt = f"""
You are a hospital management AI assistant. The user asked: "{user_input}"

Provide a helpful, professional response about hospital management.
Be specific about what actions could be taken or what information is relevant.
"""
                response = client.llm_model.generate_content(prompt)
                print(f"🤖 Gemini Response: {response.text}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
