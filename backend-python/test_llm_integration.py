#!/usr/bin/env python3
"""
Test script for LLM integration in Hospital Management System
"""

import asyncio
import os
from dotenv import load_dotenv
from client import HospitalManagementClient

# Load environment variables
load_dotenv()

async def test_llm_integration():
    """Test the LLM integration functionality."""
    print("🧪 Testing LLM Integration for Hospital Management System")
    print("=" * 60)
    
    # Create client instance
    client = HospitalManagementClient()
    
    # Check if LLM is properly configured
    if client.llm_model:
        print("✅ LLM (Google Gemini) initialized successfully")
    else:
        print("❌ LLM not available - check GEMINI_API_KEY")
        return
    
    # Test queries
    test_queries = [
        "Hello, I need help with hospital management",
        "Show me information about patients",
        "What is the current bed availability?",
        "Can you analyze the hospital's current state?",
        "How many departments do we have?",
        "Check the supply inventory status",
        "Schedule an appointment for a patient",
        "Optimize hospital resources using AI"
    ]
    
    print(f"\n🎯 Testing {len(test_queries)} natural language queries:")
    print("-" * 40)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[Test {i}] Query: '{query}'")
        try:
            # Test the LLM response without MCP connection
            if client.llm_model:
                system_prompt = """
                You are an intelligent hospital management AI assistant. Analyze the user's query and provide:
                1. What they want to do
                2. Which hospital management tool would be appropriate
                3. A helpful response
                
                User Query: """ + query
                
                response = client.llm_model.generate_content(system_prompt)
                print(f"✅ LLM Response: {response.text[:200]}...")
            else:
                print("❌ LLM not available")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Small delay between tests
        await asyncio.sleep(0.5)
    
    print(f"\n🎉 LLM Integration Test Completed!")
    print("The LLM can now be used to process natural language queries")
    print("for hospital management tasks.")
    
    # Test interactive mode
    print(f"\n🎮 Interactive Test Mode")
    print("Type 'exit' to quit")
    
    while True:
        try:
            user_input = input("\n🤖 Ask me anything about hospital management: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if user_input and client.llm_model:
                response = client.llm_model.generate_content(f"""
                You are a hospital management AI assistant. The user asked: "{user_input}"
                
                Provide a helpful response about hospital management.
                """)
                print(f"💡 AI Response: {response.text}")
            elif not client.llm_model:
                print("❌ LLM not available")
            else:
                print("Please enter a valid question.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm_integration())
