/**
 * Universal AI-MCP Service - Works like Claude Desktop
 * Can connect to any MCP server and use OpenAI for natural language processing
 */

import UniversalMCPClient from './universalMcpClient.js';

class UniversalAIMCPService {
  constructor() {
    this.mcpClient = new UniversalMCPClient();
    this.openaiApiKey = null;
    this.isConnected = false;
  }

  /**
   * Initialize with OpenAI API key and MCP server config
   */
  async initialize(openaiApiKey, mcpServerConfig) {
    this.openaiApiKey = openaiApiKey;
    
    // Connect to MCP server
    const connected = await this.mcpClient.connect(mcpServerConfig);
    if (!connected) {
      throw new Error('Failed to connect to MCP server');
    }
    
    this.isConnected = true;
    console.log('✅ Universal AI-MCP Service initialized');
    return true;
  }

  /**
   * Process natural language request
   */
  async processRequest(userMessage) {
    if (!this.isConnected) {
      throw new Error('Service not initialized');
    }

    console.log('🤖 Processing request:', userMessage);

    try {
      // Get available tools for OpenAI
      const availableTools = this.mcpClient.getToolsForOpenAI();
      const serverInfo = this.mcpClient.getServerInfo();
      
      // Call OpenAI with function calling
      const gptResponse = await this.callOpenAI(userMessage, availableTools, serverInfo);
      
      // Execute function calls
      const results = await this.executeFunctionCalls(gptResponse);
      
      return {
        success: true,
        message: gptResponse.choices[0].message.content,
        functionCalls: results,
        serverInfo: serverInfo,
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
   * Call OpenAI with function calling
   */
  async callOpenAI(userMessage, functions, serverInfo) {
    const systemPrompt = `You are a universal assistant connected to an MCP (Model Context Protocol) server.

MCP Server Information:
- URL: ${serverInfo.url}
- Available Tools: ${serverInfo.tools.join(', ')}
- Total Tools: ${serverInfo.toolCount}

You can help users by:
1. Understanding their natural language requests
2. Calling the appropriate MCP tools to fulfill their requests
3. Providing helpful responses about the results

IMPORTANT RULES:
- Only call functions when you have sufficient information
- If you need more details from the user, ask for them instead of calling functions
- Always provide clear, helpful responses about what you're doing
- Explain the results in a user-friendly way

The MCP server provides various tools that you can use to help the user. Analyze their request and determine which tools to call.`;

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
            content: systemPrompt
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
  isServiceConnected() {
    return this.isConnected;
  }

  /**
   * Disconnect
   */
  async disconnect() {
    await this.mcpClient.disconnect();
    this.isConnected = false;
    console.log('🔌 Universal AI-MCP Service disconnected');
  }
}

export default UniversalAIMCPService;
