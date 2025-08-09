/**
 * MCP Process Manager - Node.js backend for spawning MCP servers
 */

const { spawn } = require('child_process');
const express = require('express');
const cors = require('cors');
const WebSocket = require('ws');

class MCPProcessManager {
  constructor() {
    this.mcpProcess = null;
    this.isConnected = false;
    this.tools = new Map();
    this.pendingRequests = new Map();
    this.requestId = 0;
    this.serverInfo = {};
    this.websocketClients = new Set();
  }

  /**
   * Start MCP server process
   */
  async startMCPServer(config) {
    console.log('🚀 Starting MCP server with config:', config);
    
    try {
      // First, test database connectivity
      console.log('🔍 Testing database connectivity...');
      const dbTestProcess = spawn('uv', ['run', 'python', 'test_db_connection.py'], {
        cwd: config.cwd,
        env: { ...process.env, ...config.env },
        stdio: ['pipe', 'pipe', 'pipe']
      });
      
      const dbTestResult = await new Promise((resolve) => {
        let output = '';
        let errorOutput = '';
        
        dbTestProcess.stdout?.on('data', (data) => {
          output += data.toString();
          console.log(`DB Test: ${data.toString().trim()}`);
        });
        
        dbTestProcess.stderr?.on('data', (data) => {
          errorOutput += data.toString();
          console.error(`DB Test Error: ${data.toString().trim()}`);
        });
        
        dbTestProcess.on('close', (code) => {
          resolve({ code, output, errorOutput });
        });
      });
      
      if (dbTestResult.code !== 0) {
        console.log('⚠️ Database test failed, but continuing with MCP server startup...');
      } else {
        console.log('✅ Database test passed!');
      }
      
      // Prepare spawn options
      const spawnOptions = {
        env: { ...process.env, ...config.env },
        stdio: ['pipe', 'pipe', 'pipe']
      };
      
      // Add working directory if specified
      if (config.cwd) {
        spawnOptions.cwd = config.cwd;
        console.log('📁 Working directory:', config.cwd);
      }
      
      // Spawn the MCP server process
      this.mcpProcess = spawn(config.command, config.args || [], spawnOptions);

      this.serverInfo = {
        command: config.command,
        args: config.args || [],
        env: config.env || {},
        cwd: config.cwd || process.cwd(),
        pid: this.mcpProcess.pid
      };

      // Set up event handlers
      this.setupProcessHandlers();
      
      // Initialize MCP protocol
      await this.initializeMCP();
      
      this.isConnected = true;
      console.log('✅ MCP server started successfully');
      
      return true;
    } catch (error) {
      console.error('❌ Failed to start MCP server:', error);
      return false;
    }
  }

  /**
   * Set up process event handlers
   */
  setupProcessHandlers() {
    this.mcpProcess.stdout.on('data', (data) => {
      this.handleMCPMessage(data);
    });

    this.mcpProcess.stderr.on('data', (data) => {
      console.error('MCP stderr:', data.toString());
    });

    this.mcpProcess.on('close', (code) => {
      console.log(`MCP process exited with code ${code}`);
      this.isConnected = false;
      this.broadcastToClients({ type: 'disconnected', code });
    });

    this.mcpProcess.on('error', (error) => {
      console.error('MCP process error:', error);
      this.broadcastToClients({ type: 'error', error: error.message });
    });
  }

  /**
   * Handle incoming MCP messages
   */
  handleMCPMessage(data) {
    const lines = data.toString().split('\n').filter(line => line.trim());
    
    for (const line of lines) {
      try {
        const message = JSON.parse(line);
        console.log('📨 MCP message:', message);
        
        if (message.id && this.pendingRequests.has(message.id)) {
          // Response to our request
          const { resolve, reject } = this.pendingRequests.get(message.id);
          this.pendingRequests.delete(message.id);
          
          if (message.error) {
            reject(new Error(message.error.message || 'MCP error'));
          } else {
            resolve(message.result);
          }
        }
      } catch (parseError) {
        console.error('Failed to parse MCP message:', parseError);
      }
    }
  }

  /**
   * Initialize MCP protocol
   */
  async initializeMCP() {
    // Send initialize request
    const initResult = await this.sendMCPRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {
        roots: {
          listChanged: true
        },
        sampling: {}
      },
      clientInfo: {
        name: 'hospital-management-client',
        version: '1.0.0'
      }
    });

    console.log('MCP initialize result:', initResult);

    // Send initialized notification
    await this.sendMCPNotification('notifications/initialized');

    // List available tools
    const toolsResult = await this.sendMCPRequest('tools/list');
    
    if (toolsResult && toolsResult.tools) {
      for (const tool of toolsResult.tools) {
        this.tools.set(tool.name, tool);
      }
      
      this.serverInfo.tools = Array.from(this.tools.keys());
      this.serverInfo.toolCount = this.tools.size;
      
      console.log(`📋 Loaded ${this.tools.size} MCP tools:`, this.serverInfo.tools);
    }
  }

  /**
   * Send MCP request
   */
  async sendMCPRequest(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++this.requestId;
      const request = {
        jsonrpc: '2.0',
        id,
        method,
        params
      };

      this.pendingRequests.set(id, { resolve, reject });
      
      this.mcpProcess.stdin.write(JSON.stringify(request) + '\n');
      
      // Timeout after 300 seconds (5 minutes) to allow for package installation
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error('Request timeout'));
        }
      }, 300000);
    });
  }

  /**
   * Send MCP notification
   */
  async sendMCPNotification(method, params = {}) {
    const notification = {
      jsonrpc: '2.0',
      method,
      params
    };

    this.mcpProcess.stdin.write(JSON.stringify(notification) + '\n');
  }

  /**
   * Call MCP tool
   */
  async callTool(toolName, args) {
    if (!this.tools.has(toolName)) {
      throw new Error(`Tool ${toolName} not found`);
    }

    const result = await this.sendMCPRequest('tools/call', {
      name: toolName,
      arguments: args
    });

    return result;
  }

  /**
   * Get tools formatted for OpenAI
   */
  getToolsForOpenAI() {
    const functions = [];
    
    for (const [name, tool] of this.tools) {
      const functionDef = {
        name: name,
        description: tool.description || `Call ${name} tool`,
        parameters: tool.inputSchema || {
          type: 'object',
          properties: {}
        }
      };
      
      functions.push(functionDef);
    }
    
    return functions;
  }

  /**
   * Get server information
   */
  getServerInfo() {
    return {
      ...this.serverInfo,
      isConnected: this.isConnected,
      toolCount: this.tools.size,
      tools: Array.from(this.tools.keys())
    };
  }

  /**
   * Broadcast to WebSocket clients
   */
  broadcastToClients(message) {
    for (const client of this.websocketClients) {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify(message));
      }
    }
  }

  /**
   * Stop MCP server
   */
  async stop() {
    if (this.mcpProcess) {
      this.mcpProcess.kill();
      this.mcpProcess = null;
    }
    this.isConnected = false;
    this.tools.clear();
    this.pendingRequests.clear();
  }
}

// Create Express server
const app = express();
const server = require('http').createServer(app);
const wss = new WebSocket.Server({ server });

// More aggressive CORS configuration
app.use((req, res, next) => {
  const origin = req.headers.origin;
  
  // Always allow these origins
  const allowedOrigins = [
    'http://localhost:3000',
    'http://localhost:5173', 
    'http://hospital-alb-1667599615.us-east-1.elb.amazonaws.com'
  ];
  
  if (allowedOrigins.includes(origin) || !origin || origin.endsWith('.amazonaws.com')) {
    res.setHeader('Access-Control-Allow-Origin', origin || '*');
  }
  
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Max-Age', '86400'); // 24 hours
  
  // Handle preflight
  if (req.method === 'OPTIONS') {
    console.log('Handling preflight request from:', origin);
    return res.status(200).end();
  }
  
  next();
});
app.use(express.json());

const mcpManager = new MCPProcessManager();

// WebSocket connection handling
wss.on('connection', (ws) => {
  console.log('📱 WebSocket client connected');
  mcpManager.websocketClients.add(ws);
  
  ws.on('close', () => {
    mcpManager.websocketClients.delete(ws);
  });
});

// API Routes
app.post('/mcp/start', async (req, res) => {
  console.log('🚀 Received MCP start request from origin:', req.headers.origin);
  
  try {
    const config = req.body;
    console.log('📋 Starting MCP with config:', config);
    
    // Set a timeout for the response
    const timeout = setTimeout(() => {
      if (!res.headersSent) {
        console.log('⏰ MCP start timeout - sending partial response');
        res.json({ 
          success: true, 
          message: 'MCP server starting (this may take a moment)...',
          serverInfo: { isConnected: false, toolCount: 0, tools: [] }
        });
      }
    }, 25000); // 25 second timeout
    
    const started = await mcpManager.startMCPServer(config);
    clearTimeout(timeout);
    
    if (!res.headersSent) {
      if (started) {
        res.json({ 
          success: true, 
          message: 'MCP server started successfully',
          serverInfo: mcpManager.getServerInfo()
        });
      } else {
        res.status(500).json({ 
          success: false, 
          error: 'Failed to start MCP server' 
        });
      }
    }
  } catch (error) {
    console.error('❌ Error starting MCP server:', error);
    if (!res.headersSent) {
      res.status(500).json({ 
        success: false, 
        error: error.message 
      });
    }
  }
});

app.post('/mcp/call', async (req, res) => {
  try {
    const { toolName, args } = req.body;
    const result = await mcpManager.callTool(toolName, args);
    
    res.json({ 
      success: true, 
      result 
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

app.get('/mcp/tools', (req, res) => {
  try {
    const tools = mcpManager.getToolsForOpenAI();
    res.json({ 
      success: true, 
      tools,
      serverInfo: mcpManager.getServerInfo()
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

app.get('/mcp/status', (req, res) => {
  res.json({
    success: true,
    serverInfo: mcpManager.getServerInfo()
  });
});

// Health check endpoint for load balancer
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    service: 'mcp-process-manager'
  });
});

app.post('/mcp/stop', async (req, res) => {
  try {
    await mcpManager.stop();
    res.json({ 
      success: true, 
      message: 'MCP server stopped' 
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Diagnostic endpoint to check environment and auto-start MCP
app.get('/mcp/diagnose', async (req, res) => {
  const fs = require('fs');
  const { execSync } = require('child_process');
  
  try {
    const diagnostics = {
      timestamp: new Date().toISOString(),
      workingDirectory: process.cwd(),
      backendPythonExists: fs.existsSync(`${process.cwd()}/backend-python`),
      pythonExecutable: null,
      uvAvailable: false,
      pythonDependencies: null,
      mcpServerStatus: mcpManager.getServerInfo(),
      autoStartAttempted: false
    };

    // Check if UV is available
    try {
      execSync('uv --version', { stdio: 'pipe' });
      diagnostics.uvAvailable = true;
    } catch (e) {
      diagnostics.uvAvailable = false;
    }

    // Check Python executable
    try {
      const pythonVersion = execSync('python3 --version', { stdio: 'pipe' }).toString().trim();
      diagnostics.pythonExecutable = pythonVersion;
    } catch (e) {
      try {
        const pythonVersion = execSync('python --version', { stdio: 'pipe' }).toString().trim();
        diagnostics.pythonExecutable = pythonVersion;
      } catch (e2) {
        diagnostics.pythonExecutable = 'Not found';
      }
    }

    // Auto-start MCP server if not connected
    if (!mcpManager.isConnected && diagnostics.backendPythonExists && diagnostics.uvAvailable) {
      try {
        console.log('🔧 Auto-starting MCP server from diagnostic endpoint...');
        const config = {
          command: 'bash',
          args: ['start_mcp_server.sh'],
          env: { 
            PYTHONPATH: '/backend-python',
            DATABASE_URL: 'postgresql://postgres:postgres@localhost:5432/hospital_management'
          },
          cwd: '/backend-python'
        };
        
        mcpManager.startMCPServer(config);
        diagnostics.autoStartAttempted = true;
      } catch (startError) {
        diagnostics.autoStartError = startError.message;
      }
    }

    res.json({
      success: true,
      diagnostics
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`🌐 MCP Process Manager server running on port ${PORT}`);
  console.log(`📁 Working directory: ${process.cwd()}`);
  console.log(`🐍 Backend Python path: ${process.cwd()}/backend-python`);
  
  // Test if backend-python directory exists
  const fs = require('fs');
  const backendPath = `${process.cwd()}/backend-python`;
  if (fs.existsSync(backendPath)) {
    console.log('✅ Backend Python directory found');
  } else {
    console.log('⚠️ Backend Python directory not found - MCP server may not work');
  }
});

module.exports = MCPProcessManager;
