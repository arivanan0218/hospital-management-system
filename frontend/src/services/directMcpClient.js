/**
 * Direct MCP Client - Works with MCP Process Manager
 * Provides Claude Desktop-like MCP server management
 */

class DirectMCPClient {
  constructor() {
    this.processManagerUrl = 'http://localhost:3001';
    this.isConnected = false;
    this.serverInfo = {};
    this.tools = [];
    this.websocket = null;
  }

  /**
   * Connect to MCP server via process manager
   */
  async connect(mcpServerConfig) {
    console.log('🔗 Connecting to MCP server via process manager...');
    console.log('📋 Server config:', mcpServerConfig);
    console.log('🌐 Process manager URL:', this.processManagerUrl);
    
    try {
      // First check if process manager is running
      console.log('1. Checking process manager status...');
      const statusResponse = await fetch(`${this.processManagerUrl}/mcp/status`);
      if (!statusResponse.ok) {
        throw new Error(`Process manager not responding: ${statusResponse.status}`);
      }
      console.log('✅ Process manager is running');

      // Start MCP server process
      console.log('2. Starting MCP server process...');
      const response = await fetch(`${this.processManagerUrl}/mcp/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(mcpServerConfig)
      });

      const result = await response.json();
      console.log('📊 Start response:', result);
      
      if (!result.success) {
        throw new Error(result.error || 'Failed to start MCP server');
      }

      this.serverInfo = result.serverInfo;
      this.isConnected = true;
      
      // Get available tools
      await this.loadTools();
      
      // Set up WebSocket for real-time updates
      this.setupWebSocket();
      
      console.log('✅ Connected to MCP server:', this.serverInfo);
      return true;
      
    } catch (error) {
      console.error('❌ MCP connection failed:', error);
      console.error('📍 Error details:', {
        message: error.message,
        stack: error.stack,
        processManagerUrl: this.processManagerUrl
      });
      return false;
    }
  }

  /**
   * Load available tools
   */
  async loadTools() {
    try {
      const response = await fetch(`${this.processManagerUrl}/mcp/tools`);
      const result = await response.json();
      
      if (result.success) {
        this.tools = result.tools;
        this.serverInfo = { ...this.serverInfo, ...result.serverInfo };
        console.log(`📋 Loaded ${this.tools.length} tools`);
      }
    } catch (error) {
      console.error('❌ Failed to load tools:', error);
    }
  }

  /**
   * Set up WebSocket connection for real-time updates
   */
  setupWebSocket() {
    try {
      this.websocket = new WebSocket('ws://localhost:3001');
      
      this.websocket.onopen = () => {
        console.log('📱 WebSocket connected');
      };
      
      this.websocket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        console.log('📨 WebSocket message:', message);
        
        if (message.type === 'disconnected') {
          this.isConnected = false;
          console.log('🔌 MCP server disconnected');
        }
      };
      
      this.websocket.onerror = (error) => {
        console.error('📱 WebSocket error:', error);
      };
      
    } catch (error) {
      console.error('❌ WebSocket setup failed:', error);
    }
  }

  /**
   * Call MCP tool
   */
  async callTool(toolName, args) {
    if (!this.isConnected) {
      throw new Error('Not connected to MCP server');
    }

    console.log(`🔧 Calling MCP tool: ${toolName}`, args);

    try {
      const response = await fetch(`${this.processManagerUrl}/mcp/call`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          toolName,
          args
        })
      });

      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Tool call failed');
      }

      console.log(`✅ Tool result:`, result.result);
      return result.result;
      
    } catch (error) {
      console.error(`❌ Tool call failed: ${toolName}`, error);
      throw error;
    }
  }

  /**
   * Get tools formatted for OpenAI function calling
   */
  getToolsForOpenAI() {
    return this.tools;
  }

  /**
   * Get server information
   */
  getServerInfo() {
    return this.serverInfo;
  }

  /**
   * Check connection status
   */
  async getStatus() {
    try {
      const response = await fetch(`${this.processManagerUrl}/mcp/status`);
      const result = await response.json();
      
      if (result.success) {
        this.serverInfo = result.serverInfo;
        this.isConnected = result.serverInfo.isConnected;
      }
      
      return result.serverInfo;
    } catch (error) {
      console.error('❌ Status check failed:', error);
      this.isConnected = false;
      return null;
    }
  }

  /**
   * Disconnect from MCP server
   */
  async disconnect() {
    try {
      await fetch(`${this.processManagerUrl}/mcp/stop`, {
        method: 'POST'
      });

      if (this.websocket) {
        this.websocket.close();
        this.websocket = null;
      }

      this.isConnected = false;
      this.tools = [];
      this.serverInfo = {};
      
      console.log('🔌 Disconnected from MCP server');
      return true;
      
    } catch (error) {
      console.error('❌ Disconnect failed:', error);
      return false;
    }
  }
}

export default DirectMCPClient;
