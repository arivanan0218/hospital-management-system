/**
 * Native MCP Client - Direct process communication like Claude Desktop
 * Spawns MCP server processes and communicates via JSON-RPC over stdin/stdout
 */

class NativeMCPClient {
  constructor() {
    this.connected = false;
    this.tools = new Map();
    this.serverProcess = null;
    this.serverConfig = null;
    this.requestId = 0;
    this.pendingRequests = new Map();
  }

  /**
   * Start MCP server process and initialize connection
   */
  async connect(serverConfig) {
    try {
      this.serverConfig = serverConfig;
      console.log('🚀 Starting MCP server process:', serverConfig);
      
      // For web environment, we'll simulate the process communication
      // In a real Node.js environment, you'd use child_process.spawn
      await this.startServerProcess();
      await this.initializeProtocol();
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
   * Start the server process (simulated for web environment)
   */
  async startServerProcess() {
    // In a real implementation with Node.js backend:
    /*
    const { spawn } = require('child_process');
    this.serverProcess = spawn(this.serverConfig.command, this.serverConfig.args, {
      env: { ...process.env, ...this.serverConfig.env },
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    this.serverProcess.stdout.on('data', this.handleServerMessage.bind(this));
    this.serverProcess.stderr.on('data', (data) => {
      console.error('MCP Server Error:', data.toString());
    });
    */
    
    // For web environment, we'll use the existing HTTP bridge
    // but structure the communication like a real MCP client
    console.log('📡 Simulating MCP process connection via HTTP bridge...');
  }

  /**
   * Initialize MCP protocol
   */
  async initializeProtocol() {
    const initRequest = {
      jsonrpc: '2.0',
      id: this.getNextRequestId(),
      method: 'initialize',
      params: {
        protocolVersion: '2024-11-05',
        capabilities: {
          roots: {
            listChanged: true
          },
          sampling: {}
        },
        clientInfo: {
          name: 'universal-mcp-client',
          version: '1.0.0'
        }
      }
    };

    console.log('🔄 Initializing MCP protocol...');
    // For web simulation, we'll just log this
    // In real implementation: await this.sendRequest(initRequest);
  }

  /**
   * Discover available tools
   */
  async discoverTools() {
    try {
      // For web environment, use HTTP bridge to get tools
      const response = await fetch('http://localhost:8080/tools');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      let tools = data.tools || data;
      
      if (!Array.isArray(tools)) {
        throw new Error('Invalid tools response format');
      }
      
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
   * Call a tool
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
      
      // In real MCP implementation, this would be a JSON-RPC call:
      /*
      const request = {
        jsonrpc: '2.0',
        id: this.getNextRequestId(),
        method: 'tools/call',
        params: {
          name: toolName,
          arguments: args
        }
      };
      const result = await this.sendRequest(request);
      */
      
      // For web environment, use HTTP bridge
      const response = await fetch(`http://localhost:8080/tools/${toolName}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(args)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Tool call failed: ${response.status} ${errorText}`);
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
   * Send JSON-RPC request (for real MCP implementation)
   */
  async sendRequest(request) {
    return new Promise((resolve, reject) => {
      const requestId = request.id;
      this.pendingRequests.set(requestId, { resolve, reject });
      
      // In real implementation:
      // this.serverProcess.stdin.write(JSON.stringify(request) + '\n');
      
      // Timeout after 30 seconds
      setTimeout(() => {
        if (this.pendingRequests.has(requestId)) {
          this.pendingRequests.delete(requestId);
          reject(new Error('Request timeout'));
        }
      }, 30000);
    });
  }

  /**
   * Handle server messages (for real MCP implementation)
   */
  handleServerMessage(data) {
    const lines = data.toString().split('\n');
    
    for (const line of lines) {
      if (!line.trim()) continue;
      
      try {
        const message = JSON.parse(line);
        
        if (message.id && this.pendingRequests.has(message.id)) {
          const pending = this.pendingRequests.get(message.id);
          this.pendingRequests.delete(message.id);
          
          if (message.error) {
            pending.reject(new Error(message.error.message));
          } else {
            pending.resolve(message.result);
          }
        }
      } catch (error) {
        console.error('Failed to parse server message:', error);
      }
    }
  }

  /**
   * Get tools for OpenAI function calling
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

      // Use tool schema if available
      if (tool.inputSchema) {
        func.parameters = tool.inputSchema;
      } else {
        // Create generic parameters for hospital tools
        if (tool.name.includes('create_patient')) {
          func.parameters = {
            type: "object",
            properties: {
              first_name: { type: "string", description: "Patient's first name" },
              last_name: { type: "string", description: "Patient's last name" },
              date_of_birth: { type: "string", description: "Date of birth in YYYY-MM-DD format" },
              phone: { type: "string", description: "Phone number" },
              email: { type: "string", description: "Email address" },
              address: { type: "string", description: "Home address" },
              gender: { type: "string", description: "Gender (male/female)" },
              patient_number: { type: "string", description: "Unique patient number" }
            },
            required: ["first_name", "last_name", "date_of_birth"]
          };
        } else if (tool.name.includes('create_department')) {
          func.parameters = {
            type: "object",
            properties: {
              name: { type: "string", description: "Department name" },
              description: { type: "string", description: "Department description" },
              floor_number: { type: "integer", description: "Floor number" },
              phone: { type: "string", description: "Department phone" },
              email: { type: "string", description: "Department email" }
            },
            required: ["name"]
          };
        } else if (tool.name.startsWith('list_')) {
          func.parameters = {
            type: "object",
            properties: {},
            required: []
          };
        } else {
          func.parameters = {
            type: "object",
            properties: {
              args: { type: "object", description: "Tool arguments" }
            },
            required: []
          };
        }
      }

      functions.push(func);
    });

    return functions;
  }

  /**
   * Get next request ID
   */
  getNextRequestId() {
    return ++this.requestId;
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
      command: this.serverConfig?.command,
      args: this.serverConfig?.args,
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
    
    // In real implementation:
    // if (this.serverProcess) {
    //   this.serverProcess.kill();
    //   this.serverProcess = null;
    // }
    
    console.log('🔌 Disconnected from MCP server');
  }
}

export default NativeMCPClient;
