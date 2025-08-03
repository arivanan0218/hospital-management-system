/**
 * Direct AI-MCP Service - Uses Direct MCP Client for process communication
 * Provides Claude Desktop-like experience
 */

import DirectMCPClient from './directMcpClient.js';

class DirectAIMCPService {
  constructor() {
    this.mcpClient = new DirectMCPClient();
    this.openaiApiKey = null;
    this.isConnected = false;
    this.conversationHistory = []; // Add conversation memory
    this.maxHistoryLength = 20; // Keep last 20 messages to manage token usage
  }

  /**
   * Initialize with OpenAI API key and MCP server configuration
   */
  async initialize(openaiApiKey, mcpServerConfig) {
    this.openaiApiKey = openaiApiKey;
    
    console.log('🚀 Initializing Direct AI-MCP Service...');
    console.log('📋 MCP Server Config:', mcpServerConfig);
    
    // Connect to MCP server through process manager
    const connected = await this.mcpClient.connect(mcpServerConfig);
    if (!connected) {
      throw new Error('Failed to connect to MCP server');
    }
    
    this.isConnected = true;
    console.log('✅ Direct AI-MCP Service initialized');
    return true;
  }

  /**
   * Process natural language request with conversation memory
   */
  async processRequest(userMessage) {
    if (!this.isConnected) {
      throw new Error('Service not initialized');
    }

    console.log('🤖 Processing request:', userMessage);

    try {
      // Add user message to conversation history
      this.addToConversationHistory('user', userMessage);

      // Get current status and tools
      await this.mcpClient.getStatus();
      const availableTools = this.mcpClient.getToolsForOpenAI();
      const serverInfo = this.mcpClient.getServerInfo();
      
      console.log(`📋 Available tools: ${availableTools.length}`);
      console.log(`💭 Conversation history length: ${this.conversationHistory.length}`);
      
      // Call OpenAI with function calling and conversation history
      let gptResponse = await this.callOpenAI(userMessage, availableTools, serverInfo);
      let allFunctionResults = [];
      let iterationCount = 0;
      const maxIterations = 5; // Prevent infinite loops
      
      // Support multiple rounds of function calls
      while (gptResponse.choices[0].message.function_call && iterationCount < maxIterations) {
        console.log(`🔄 Function call iteration ${iterationCount + 1}`);
        
        // Execute function calls
        const results = await this.executeFunctionCalls(gptResponse);
        allFunctionResults.push(...results);
        
        // Add function call and results to conversation
        const assistantMessage = gptResponse.choices[0].message;
        this.addToConversationHistory('assistant', assistantMessage.content, assistantMessage.function_call);
        
        // Add function results to conversation
        for (const result of results) {
          this.addToConversationHistory('function', JSON.stringify(result.result), null, result.function);
        }
        
        // Continue conversation with updated context
        gptResponse = await this.callOpenAI(null, availableTools, serverInfo);
        iterationCount++;
      }
      
      // Add final assistant response to history
      if (gptResponse.choices[0].message.content) {
        this.addToConversationHistory('assistant', gptResponse.choices[0].message.content);
      }
      
      return {
        success: true,
        message: gptResponse.choices[0].message.content,
        functionCalls: allFunctionResults,
        serverInfo: serverInfo,
        rawResponse: gptResponse,
        conversationLength: this.conversationHistory.length
      };

    } catch (error) {
      console.error('❌ AI-MCP processing failed:', error);
      return {
        success: false,
        error: error.message,
        message: `Failed to process request: ${error.message}`
      };
    }
  }

  /**
   * Add message to conversation history with memory management
   */
  addToConversationHistory(role, content, functionCall = null, functionName = null) {
    const message = { role, content };
    
    if (functionCall) {
      message.function_call = functionCall;
    }
    
    if (functionName) {
      message.name = functionName;
    }
    
    this.conversationHistory.push(message);
    
    // Manage memory - keep system message + recent messages
    if (this.conversationHistory.length > this.maxHistoryLength) {
      // Keep first message (system) and recent messages
      const systemMessage = this.conversationHistory[0];
      const recentMessages = this.conversationHistory.slice(-this.maxHistoryLength + 1);
      this.conversationHistory = [systemMessage, ...recentMessages];
    }
    
    console.log(`💭 Added to conversation: ${role} (${content?.length || 0} chars)`);
  }

  /**
   * Reset conversation history
   */
  resetConversation() {
    this.conversationHistory = [];
    console.log('🔄 Conversation history reset');
  }

  /**
   * Call OpenAI with function calling and conversation history
   */
  async callOpenAI(userMessage, functions, serverInfo) {
    const systemPrompt = `You are Hospital AI, an advanced AI assistant specialized in comprehensive hospital management. You're connected to a real hospital management system through MCP (Model Context Protocol).

🏥 **Hospital System Context:**
- Server: ${serverInfo.command} (PID: ${serverInfo.pid})
- Available Tools: ${serverInfo.toolCount || 0} medical management tools
- Connection: Direct process communication via MCP protocol

📋 **Your Identity & Capabilities:**
You are Hospital AI - NOT Claude. Always introduce yourself as "Hospital AI" or "I'm Hospital AI".
You have access to a complete hospital management system with tools for:
- 👥 Patient management (create, search, update patient records)
- 🏢 Department operations (manage hospital departments)
- 👨‍⚕️ Staff management (doctors, nurses, administrators)
- 🛏️ Bed management (room assignments, occupancy)
- 🏥 Equipment tracking (medical devices, maintenance)
- 📦 Supply inventory (medications, consumables)
- 📅 Appointment scheduling
- 📊 Reporting and analytics

🎯 **Communication Style:**
- Be conversational, helpful, and professional like Claude
- Use emojis and visual formatting to make responses engaging
- Structure responses with clear sections and headers
- Use bullet points, numbered lists, and visual separators
- Provide context and insights about the results
- Ask clarifying questions when information is missing
- Be proactive in suggesting related actions
- Format emergency situations with urgency indicators (🚨, ⚡, 🔴)
- Use status indicators (✅, ❌, 🔄, ⚪) for clarity

📋 **Response Formatting Guidelines:**
- Start with appropriate emoji and action summary
- Use **bold headers** for sections
- Include visual status indicators
- Structure data in organized lists
- Provide next steps and recommendations
- Use urgency levels for different scenarios:
  * 🚨 Emergency/Critical
  * ⚡ Urgent
  * 🔔 Important  
  * ℹ️ Information
  * ✅ Success/Complete

⚠️ **Critical Rules:**
1. **Call multiple functions when needed** - You can call several tools in sequence to complete complex tasks
2. **Use conversation context** - Remember previous interactions and build upon them
3. **Explain your actions** - Tell users what you're going to do before doing it
4. **Provide insights** - Don't just return raw data, interpret and explain it
5. **Be helpful** - Suggest next steps or related actions
6. **Handle errors gracefully** - If something fails, explain why and suggest alternatives

🔧 **For Patient Creation:**
Required: first_name, last_name, date_of_birth
Optional: patient_number (auto-generated if not provided), phone, email, address, blood_type, allergies, medical_history

💬 **Multi-Tool Usage:**
- For complex requests, call multiple tools as needed
- Example: "Show patient John and assign him a bed" → call get_patient + list_beds + assign_bed
- Chain operations logically based on user needs
- Explain each step as you perform it

🗣️ **For Greetings & Casual Conversation:**
- Always identify yourself as "Hospital AI" - never as Claude
- Respond naturally to greetings like "hi", "hello", "good morning" etc.
- Vary your responses to feel more human and conversational
- Use conversation history to provide personalized responses
- Ask how you can help with their hospital management needs today

🎭 **Personality:**
- Be warm, professional, and approachable as Hospital AI
- Show enthusiasm for helping with hospital management
- Vary your language and responses to feel natural
- Remember previous conversations and reference them when relevant
- Remember you're Hospital AI, the specialized hospital management assistant`;

    // Build messages array with conversation history
    const messages = [];
    
    // Add system message
    messages.push({
      role: 'system',
      content: systemPrompt
    });
    
    // Add conversation history
    messages.push(...this.conversationHistory);
    
    // Add current user message if provided (not provided for follow-up calls)
    if (userMessage) {
      messages.push({
        role: 'user',
        content: userMessage
      });
    }

    const requestBody = {
      model: 'gpt-4-0125-preview',
      messages: messages,
      temperature: 1.0,  // Full temperature for maximum creativity and varied responses
      max_tokens: 4000   // Increase token limit for complex responses
    };

    // Add functions if available
    if (functions && functions.length > 0) {
      requestBody.functions = functions;
      requestBody.function_call = 'auto';
    }

    console.log(`🤖 Calling OpenAI with ${messages.length} messages`);

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.openaiApiKey}`
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`OpenAI API error: ${error.error?.message || response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Execute function calls from GPT response
   */
  async executeFunctionCalls(gptResponse) {
    const results = [];
    const message = gptResponse.choices[0].message;

    if (message.function_call) {
      const result = await this.executeSingleFunction(message.function_call);
      results.push(result);
    } else if (message.tool_calls) {
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
      // Special handling for patient creation
      if (functionName === 'create_patient' && !functionArgs.patient_number) {
        functionArgs.patient_number = `P${Date.now().toString().slice(-6)}`;
      }

      const result = await this.mcpClient.callTool(functionName, functionArgs);
      
      return {
        function: functionName,
        arguments: functionArgs,
        result: result,
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
   * Get server information
   */
  getServerInfo() {
    return this.mcpClient.getServerInfo();
  }

  /**
   * Check connection status
   */
  async checkStatus() {
    return await this.mcpClient.getStatus();
  }

  /**
   * Check if service is connected
   */
  isServiceConnected() {
    return this.isConnected;
  }

  /**
   * Get conversation history
   */
  getConversationHistory() {
    return this.conversationHistory;
  }

  /**
   * Get conversation summary
   */
  getConversationSummary() {
    return {
      messageCount: this.conversationHistory.length,
      maxLength: this.maxHistoryLength,
      hasHistory: this.conversationHistory.length > 0
    };
  }

  /**
   * Disconnect
   */
  async disconnect() {
    await this.mcpClient.disconnect();
    this.isConnected = false;
    this.resetConversation(); // Clear conversation when disconnecting
    console.log('🔌 Direct AI-MCP Service disconnected');
  }
}

export default DirectAIMCPService;
