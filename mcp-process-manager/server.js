/**
 * MCP Process Manager - Node.js backend for spawning MCP servers
 */

const { spawn } = require('child_process');
const express = require('express');
const cors = require('cors');
const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');
// Add reports dir reference
const reportsDir = path.join(__dirname, '../backend-python/reports');

// Helper: detect usable python interpreter (prefers project venv)
function detectPython() {
  const candidates = [
    process.env.VENV_PYTHON,
    path.join(process.cwd(), '.venv-py312', 'Scripts', 'python.exe'),
    path.join(__dirname, '..', '.venv-py312', 'Scripts', 'python.exe'),
    path.join(process.cwd(), '.venv', 'Scripts', 'python.exe')
  ].filter(Boolean);
  for (const c of candidates) {
    if (c && fs.existsSync(c)) return c;
  }
  return null; // fallback handled later
}

const resolvedBackendCwd = path.join(__dirname, '../backend-python');
const resolvedPython = detectPython();

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
      
      // Timeout after 30 seconds
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error('Request timeout'));
        }
      }, 30000);
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

app.use(cors());
app.use(express.json());
// NEW: serve reports directory statically so frontend can fetch files directly if needed
if (fs.existsSync(reportsDir)) {
  console.log('📂 Serving reports directory at /reports from', reportsDir);
  app.use('/reports', express.static(reportsDir));
}

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
  try {
    // If already running, don't start again – prevents second failing spawn
    if (mcpManager.mcpProcess) {
      return res.json({
        success: true,
        message: 'MCP server already running',
        serverInfo: mcpManager.getServerInfo()
      });
    }

    let config = req.body || {};

    // Normalize cwd
    config.cwd = resolvedBackendCwd;

    // If command missing or just 'python', replace with detected venv interpreter
    if (!config.command || config.command.toLowerCase() === 'python') {
      if (resolvedPython) {
        config.command = resolvedPython;
      } else {
        // Last resort: try 'python' but warn
        console.warn('⚠️ No virtual env python found, falling back to system python');
        config.command = 'python';
      }
    }

    // Default args if not supplied
    if (!config.args || !Array.isArray(config.args) || config.args.length === 0) {
      config.args = ['comprehensive_server.py'];
    }

    const started = await mcpManager.startMCPServer(config);
    if (started) {
      res.json({
        success: true,
        message: 'MCP server started',
        serverInfo: mcpManager.getServerInfo()
      });
    } else {
      res.status(500).json({ success: false, error: 'Failed to start MCP server' });
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
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

app.get('/reports/discharge/download/:reportNumber.pdf', async (req, res) => {
  const reportNumber = req.params.reportNumber;
  console.log('📥 PDF download request received for', reportNumber);
  if (!reportNumber) {
    return res.status(400).json({ success: false, error: 'Missing report number' });
  }
  try {
    // Verify underlying markdown exists – prevents fake/simulated report numbers
    const markdownPath = findMarkdownForReport(reportNumber);
    if (!markdownPath) {
      return res.status(404).json({ success: false, error: 'Base markdown for this report number not found. Generate the report first.' });
    }
    if (!mcpManager.mcpProcess) {
      console.log('❌ MCP process not running');
      return res.status(503).json({ success: false, error: 'MCP server not running' });
    }
    let toolName = 'mcp_hospital-mana_download_discharge_report'; // use the full prefixed name
    if (!mcpManager.tools.has(toolName)) {
      // Try suffix strategy as fallback
      const alt = findToolBySuffix('download_discharge_report');
      if (alt) {
        console.log('🔁 Adjusted tool name to', alt);
        toolName = alt;
      } else {
        console.log('⚠️ download_discharge_report tool not in list. Available:', Array.from(mcpManager.tools.keys()));
        return res.status(500).json({ success: false, error: 'download_discharge_report tool not registered', available_tools: Array.from(mcpManager.tools.keys()) });
      }
    }
    console.log('🔧 Calling tool', toolName, 'with report_number', reportNumber);
    const toolResult = await mcpManager.callTool(toolName, { report_number: reportNumber, download_format: 'pdf' });
    console.log('🔧 Tool raw result:', JSON.stringify(toolResult));
    
    // Handle the nested structure returned by the MCP tool
    if (!toolResult || !toolResult.content || !Array.isArray(toolResult.content)) {
      return res.status(500).json({ success: false, error: 'Invalid tool response format', toolResult });
    }
    
    // Extract the actual result from MCP response
    const mcpContent = toolResult.content[0];
    if (!mcpContent || mcpContent.type !== 'text') {
      return res.status(500).json({ success: false, error: 'Invalid MCP content format', toolResult });
    }
    
    let actualResult;
    try {
      actualResult = JSON.parse(mcpContent.text);
    } catch (parseError) {
      return res.status(500).json({ success: false, error: 'Failed to parse tool result JSON', parseError: parseError.message });
    }
    
    if (!actualResult.success || !actualResult.data) {
      return res.status(500).json({ success: false, error: 'Tool failed or returned no data', actualResult });
    }
    
    let filePath = actualResult.data.download_path || actualResult.data.path || actualResult.data.file_path;
    console.log('📄 Reported download_path:', filePath);
    if (!filePath) {
      return res.status(500).json({ success: false, error: 'No download path in tool result', toolResult });
    }
    if (!path.isAbsolute(filePath)) {
      filePath = path.join(resolvedBackendCwd, filePath);
      console.log('🛠 Resolved relative path to', filePath);
    }
    if (!fs.existsSync(filePath)) {
      console.log('❌ File does not exist on disk at', filePath);
      return res.status(404).json({ success: false, error: 'PDF file not found on disk after generation', resolved_path: filePath });
    }
    console.log('✅ Streaming PDF', filePath);
    const filename = path.basename(filePath);
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    fs.createReadStream(filePath)
      .on('error', e => { console.error('Stream error:', e); if (!res.headersSent) res.status(500).end('File stream error'); })
      .pipe(res);
  } catch (e) {
    console.error('Download endpoint error:', e);
    res.status(500).json({ success: false, error: e.message, stack: e.stack });
  }
});

// New: simple endpoint to list current & download files for debugging
app.get('/reports/debug/list', (req, res) => {
  try {
    const current = [];
    const downloads = [];
    const currentDir = path.join(resolvedBackendCwd, 'reports', 'discharge', 'current');
    const downloadsDir = path.join(resolvedBackendCwd, 'reports', 'discharge', 'downloads');
    if (fs.existsSync(currentDir)) {
      for (const f of fs.readdirSync(currentDir)) current.push(f);
    }
    if (fs.existsSync(downloadsDir)) {
      for (const f of fs.readdirSync(downloadsDir)) downloads.push(f);
    }
    res.json({ success: true, current, downloads, toolNames: Array.from(mcpManager.tools.keys()) });
  } catch (e) {
    res.status(500).json({ success: false, error: e.message });
  }
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, async () => {
  console.log(`🌐 MCP Process Manager server running on port ${PORT}`);

  // Auto-start only if not already running
  if (!mcpManager.mcpProcess) {
    try {
      console.log('🚀 Auto-starting MCP server...');
      const autoConfig = {
        command: resolvedPython || 'python',
        args: ['comprehensive_server.py'],
        cwd: resolvedBackendCwd,
        env: {}
      };
      await mcpManager.startMCPServer(autoConfig);
      console.log('✅ MCP server auto-started successfully');
    } catch (error) {
      console.error('❌ Failed to auto-start MCP server:', error.message);
      console.log('💡 You can manually start it via POST /mcp/start');
    }
  }
});

module.exports = MCPProcessManager;

// Utility: find tool by suffix (handles possible name prefix differences)
function findToolBySuffix(suffix) {
  for (const name of mcpManager.tools.keys()) {
    if (name.endsWith(suffix)) return name;
  }
  return null;
}

// Utility: find markdown file for report
function findMarkdownForReport(reportNumber) {
  const currentDir = path.join(resolvedBackendCwd, 'reports', 'discharge', 'current');
  const archiveDir = path.join(resolvedBackendCwd, 'reports', 'discharge', 'archive');
  const patterns = [currentDir, archiveDir];
  for (const dir of patterns) {
    if (!fs.existsSync(dir)) continue;
    const files = fs.readdirSync(dir).filter(f => f.startsWith(reportNumber + '_') && f.endsWith('.md'));
    if (files.length) {
      return path.join(dir, files[0]);
    }
  }
  return null;
}
