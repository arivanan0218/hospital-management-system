/**
 * AI-Powered MCP Service - Similar to Claude Desktop
 * Uses OpenAI GPT to analyze natural language and call appropriate MCP tools
 */

import MCPClient from './mcpClient.js';

class AIMCPService {
  constructor() {
    this.mcpClient = new MCPClient();
    this.openaiApiKey = null;
    this.isConnected = false;
  }

  /**
   * Initialize the service with OpenAI API key
   */
  async initialize(openaiApiKey) {
    this.openaiApiKey = openaiApiKey;
    
    // Connect to MCP server
    const connected = await this.mcpClient.connect();
    if (!connected) {
      throw new Error('Failed to connect to MCP server');
    }
    
    this.isConnected = true;
    console.log('✅ AI-MCP Service initialized successfully');
    return true;
  }

  /**
   * Process natural language request using GPT and execute MCP tools
   */
  async processRequest(userMessage) {
    if (!this.isConnected) {
      throw new Error('Service not initialized');
    }

    console.log('🤖 Processing natural language request:', userMessage);

    try {
      // Get available tools from MCP server
      const availableTools = this.mcpClient.getTools();
      
      // Create function definitions for GPT
      const functionDefinitions = this.createFunctionDefinitions(availableTools);
      
      // Call OpenAI GPT with function calling
      const gptResponse = await this.callOpenAI(userMessage, functionDefinitions);
      
      // Execute the function calls determined by GPT
      const results = await this.executeFunctionCalls(gptResponse);
      
      return {
        success: true,
        message: gptResponse.choices[0].message.content,
        functionCalls: results,
        rawResponse: gptResponse
      };

    } catch (error) {
      console.error('❌ AI-MCP processing failed:', error);
      return {
        success: false,
        error: error.message,
        message: 'Failed to process request'
      };
    }
  }

  /**
   * Create OpenAI function definitions from MCP tools
   */
  createFunctionDefinitions(tools) {
    const functions = [];
    
    tools.forEach(tool => {
      // Map MCP tool to OpenAI function format
      const func = {
        name: tool.name,
        description: tool.description,
        parameters: {
          type: "object",
          properties: {},
          required: []
        }
      };

      // Add common parameters based on tool type
      if (tool.name.includes('create_patient')) {
        func.parameters.properties = {
          first_name: { type: "string", description: "Patient's first name" },
          last_name: { type: "string", description: "Patient's last name" },
          date_of_birth: { type: "string", description: "Date of birth in YYYY-MM-DD format" },
          phone: { type: "string", description: "Phone number" },
          email: { type: "string", description: "Email address" },
          address: { type: "string", description: "Home address" },
          gender: { type: "string", description: "Gender (male/female)" },
          patient_number: { type: "string", description: "Unique patient number" }
        };
        func.parameters.required = ["first_name", "last_name", "date_of_birth"];
      } else if (tool.name.includes('create_department')) {
        func.parameters.properties = {
          name: { type: "string", description: "Department name" },
          description: { type: "string", description: "Department description" },
          floor_number: { type: "integer", description: "Floor number" },
          phone: { type: "string", description: "Department phone" },
          email: { type: "string", description: "Department email" }
        };
        func.parameters.required = ["name"];
      } else if (tool.name.includes('create_room')) {
        func.parameters.properties = {
          room_number: { type: "string", description: "Room number" },
          department_id: { type: "string", description: "Department ID" },
          room_type: { type: "string", description: "Room type (standard, icu, emergency, etc.)" },
          floor_number: { type: "integer", description: "Floor number" },
          capacity: { type: "integer", description: "Room capacity" }
        };
        func.parameters.required = ["room_number", "department_id"];
      } else if (tool.name.includes('create_bed')) {
        func.parameters.properties = {
          bed_number: { type: "string", description: "Bed number" },
          room_id: { type: "string", description: "Room ID" },
          bed_type: { type: "string", description: "Bed type (standard, icu, etc.)" },
          status: { type: "string", description: "Bed status (available, occupied, etc.)" }
        };
        func.parameters.required = ["bed_number", "room_id"];
      } else if (tool.name.includes('list_')) {
        // List tools typically don't need parameters
        func.parameters.properties = {};
      }

      functions.push(func);
    });

    return functions;
  }

  /**
   * Call OpenAI GPT with function calling capability
   */
  async callOpenAI(userMessage, functions) {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.openaiApiKey}`
      },
      body: JSON.stringify({
        model: 'gpt-4-0125-preview',
        messages: [
          {
            role: 'system',
            content: `You are a hospital management assistant connected to an MCP server with hospital management tools. 
            
You can help users with:
- Creating and managing patients
- Creating departments, rooms, and beds
- Listing hospital data
- Managing appointments, staff, equipment, and supplies

CRITICAL RULES:
1. NEVER call create_patient function unless you have ALL required information:
   - First name (required)
   - Last name (required) 
   - Date of birth in YYYY-MM-DD format (required)

2. If user asks to create a patient but doesn't provide required info, respond conversationally asking for the missing details. DO NOT call any functions.

3. Only call functions when you have all required parameters.

4. Always provide helpful, conversational responses explaining what you're doing.

For patient creation, generate a unique patient number like P123456.
For listing operations, always call the appropriate list function.

Available MCP tools: ${functions.map(f => f.name).join(', ')}`
          },
          {
            role: 'user',
            content: userMessage
          }
        ],
        functions: functions,
        function_call: 'auto',
        temperature: 0.1
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`OpenAI API error: ${error.error?.message || response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Execute function calls determined by GPT
   */
  async executeFunctionCalls(gptResponse) {
    const results = [];
    const message = gptResponse.choices[0].message;

    if (message.function_call) {
      // Single function call
      const result = await this.executeSingleFunction(message.function_call);
      results.push(result);
    } else if (message.tool_calls) {
      // Multiple function calls (newer API format)
      for (const toolCall of message.tool_calls) {
        const result = await this.executeSingleFunction(toolCall.function);
        results.push(result);
      }
    }

    return results;
  }

  /**
   * Execute a single function call
   */
  async executeSingleFunction(functionCall) {
    const functionName = functionCall.name;
    let functionArgs;
    
    try {
      functionArgs = JSON.parse(functionCall.arguments);
    } catch (parseError) {
      return {
        function: functionName,
        arguments: functionCall.arguments,
        error: `Invalid function arguments: ${parseError.message}`,
        success: false
      };
    }

    console.log(`🔧 Executing MCP tool: ${functionName}`, functionArgs);

    try {
      // Special handling for patient creation - generate patient number
      if (functionName === 'create_patient' && !functionArgs.patient_number) {
        functionArgs.patient_number = `P${Date.now().toString().slice(-6)}`;
      }

      // Call the MCP tool
      const result = await this.mcpClient.callTool(functionName, functionArgs);
      
      // Check if the result indicates success or failure
      if (result.error) {
        return {
          function: functionName,
          arguments: functionArgs,
          error: result.error,
          success: false
        };
      }
      
      return {
        function: functionName,
        arguments: functionArgs,
        result: result.result,
        success: true
      };
    } catch (error) {
      console.error(`❌ Function execution failed: ${functionName}`, error);
      return {
        function: functionName,
        arguments: functionArgs,
        error: error.message,
        success: false
      };
    }
  }

  /**
   * Check if service is connected
   */
  isServiceConnected() {
    return this.isConnected;
  }

  /**
   * Disconnect from services
   */
  async disconnect() {
    await this.mcpClient.disconnect();
    this.isConnected = false;
    console.log('🔌 AI-MCP Service disconnected');
  }
}

export default AIMCPService;
