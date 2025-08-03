/**
 * Universal MCP Client - Similar to Claude Desktop
 * Can connect to any MCP server and dynamically discover tools
 */

class UniversalMCPClient {
  constructor() {
    this.connected = false;
    this.tools = new Map();
    this.serverConfig = null;
    this.requestId = 0;
  }

  /**
   * Connect to any MCP server
   */
  async connect(serverConfig) {
    try {
      this.serverConfig = serverConfig;
      console.log('🚀 Connecting to MCP server:', serverConfig);
      
      // Test connection and discover tools
      await this.discoverTools();
      
      this.connected = true;
      console.log('✅ Connected to MCP server successfully');
      return true;
    } catch (error) {
      console.error('❌ Failed to connect to MCP server:', error);
      return false;
    }
  }

  /**
   * Discover available tools from the MCP server
   */
  async discoverTools() {
    try {
      let response;
      
      // Try different common MCP server endpoints
      const endpoints = [
        `${this.serverConfig.url}/tools`,
        `${this.serverConfig.url}/list_tools`,
        `${this.serverConfig.url}/mcp/tools`
      ];

      for (const endpoint of endpoints) {
        try {
          response = await fetch(endpoint, {
            headers: this.serverConfig.headers || {}
          });
          
          if (response.ok) {
            break;
          }
        } catch (err) {
          continue;
        }
      }

      if (!response || !response.ok) {
        throw new Error(`Unable to reach MCP server at ${this.serverConfig.url}`);
      }

      const data = await response.json();
      
      // Handle different response formats
      let tools = data.tools || data.result?.tools || data;
      
      if (!Array.isArray(tools)) {
        if (data.tools) {
          tools = data.tools;
        } else {
          throw new Error('Server response does not contain tools array');
        }
      }
      
      // Store tools
      this.tools.clear();
      tools.forEach(tool => {
        this.tools.set(tool.name, tool);
      });
      
      console.log(`🛠️ Discovered ${tools.length} MCP tools:`, Array.from(this.tools.keys()));
      return Array.from(this.tools.values());
    } catch (error) {
      console.error('❌ Failed to discover tools:', error);
      throw error;
    }
  }

  /**
   * Call a tool with arguments
   */
  async callTool(toolName, args = {}) {
    if (!this.connected) {
      throw new Error('MCP client not connected');
    }

    if (!this.tools.has(toolName)) {
      throw new Error(`Tool '${toolName}' not found`);
    }

    try {
      console.log(`🔧 Calling MCP tool: ${toolName}`, args);
      
      // Try different tool endpoint patterns
      const endpoints = [
        `${this.serverConfig.url}/tools/${toolName}`,
        `${this.serverConfig.url}/call/${toolName}`,
        `${this.serverConfig.url}/mcp/call/${toolName}`
      ];

      let response;
      for (const endpoint of endpoints) {
        try {
          response = await fetch(endpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              ...(this.serverConfig.headers || {})
            },
            body: JSON.stringify(args)
          });
          
          if (response.ok) {
            break;
          }
        } catch (err) {
          continue;
        }
      }

      if (!response || !response.ok) {
        const errorText = await response?.text() || 'Unknown error';
        throw new Error(`Tool call failed: ${response?.status} ${errorText}`);
      }

      const result = await response.json();
      console.log(`✅ Tool result for ${toolName}:`, result);
      
      return result;
    } catch (error) {
      console.error(`❌ Tool call failed for ${toolName}:`, error);
      throw error;
    }
  }

  /**
   * Get tool schema for OpenAI function calling
   */
  getToolsForOpenAI() {
    const functions = [];
    
    this.tools.forEach(tool => {
      const func = {
        name: tool.name,
        description: tool.description || `Execute ${tool.name} tool`,
        parameters: {
          type: "object",
          properties: {},
          required: []
        }
      };

      // Try to infer parameters from tool schema if available
      if (tool.inputSchema) {
        func.parameters = tool.inputSchema;
      } else if (tool.parameters) {
        func.parameters = tool.parameters;
      } else {
        // Generic parameters for unknown tools
        func.parameters.properties = {
          args: {
            type: "object",
            description: "Arguments for the tool"
          }
        };
      }

      functions.push(func);
    });

    return functions;
  }

  /**
   * Get available tools
   */
  getTools() {
    return Array.from(this.tools.values());
  }

  /**
   * Check if connected
   */
  isConnected() {
    return this.connected;
  }

  /**
   * Get server info
   */
  getServerInfo() {
    return {
      url: this.serverConfig?.url,
      toolCount: this.tools.size,
      tools: Array.from(this.tools.keys())
    };
  }

  /**
   * Disconnect
   */
  disconnect() {
    this.connected = false;
    this.tools.clear();
    this.serverConfig = null;
    console.log('🔌 Disconnected from MCP server');
  }
}

export default UniversalMCPClient;
