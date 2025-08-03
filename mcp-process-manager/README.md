# MCP Process Manager

A Node.js backend service that spawns and manages MCP servers for direct process communication, similar to Claude Desktop's approach.

## Features

- **Direct Process Spawning**: Spawns MCP servers as child processes
- **JSON-RPC Protocol**: Communicates with MCP servers via stdin/stdout
- **Real-time Updates**: WebSocket support for connection status
- **REST API**: HTTP endpoints for managing MCP servers
- **Tool Discovery**: Automatically discovers and loads MCP tools

## Quick Start

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Start the Process Manager**:
   ```bash
   npm start
   ```
   Or on Windows:
   ```bash
   start_process_manager.bat
   ```

3. **Server runs on**: `http://localhost:3001`

## API Endpoints

### POST /mcp/start
Start an MCP server process with configuration:
```json
{
  "command": "python",
  "args": ["-m", "backend_python.comprehensive_server"],
  "env": {
    "PYTHONPATH": "c:\\Users\\Arivanan\\hospital-management-system\\backend-python"
  }
}
```

### POST /mcp/call
Call an MCP tool:
```json
{
  "toolName": "list_patients",
  "args": {}
}
```

### GET /mcp/tools
Get available tools formatted for OpenAI function calling.

### GET /mcp/status
Get current MCP server status and information.

### POST /mcp/stop
Stop the running MCP server.

## WebSocket

Connect to `ws://localhost:3001` for real-time status updates.

## Configuration

The process manager accepts Claude Desktop-style MCP server configurations:

```json
{
  "command": "python",
  "args": ["-m", "your_mcp_server"],
  "env": {
    "PYTHONPATH": "/path/to/your/server"
  }
}
```

## Hospital MCP Server Example

```json
{
  "command": "python",
  "args": ["-m", "backend_python.comprehensive_server"],
  "env": {
    "PYTHONPATH": "c:\\Users\\Arivanan\\hospital-management-system\\backend-python"
  }
}
```

This will start the hospital management MCP server with 32+ tools for patient management, department operations, staff management, and more.
