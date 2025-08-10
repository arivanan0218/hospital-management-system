# Hospital Management System - Direct HTTP Architecture

This updated version removes the MCP process manager and connects the frontend directly to the Python backend using FastMCP's HTTP transport.

## 🏗️ Architecture Changes

### Before (with MCP Process Manager)
```
Frontend → MCP Process Manager → Python Backend (stdio)
   ↓              ↓                     ↓
  React      Node.js server      FastMCP stdio
```

### After (Direct HTTP)
```
Frontend → Python Backend (HTTP)
   ↓              ↓
  React      FastMCP HTTP server
```

## 🚀 Quick Start

### 1. Start the Backend Server

Choose one of these methods:

#### Option A: Using the batch file (Windows)
```bash
cd backend-python
start_server.bat
```

#### Option B: Using PowerShell (Windows)
```powershell
cd backend-python
.\start_server.ps1
```

#### Option C: Using Python directly
```bash
cd backend-python
python comprehensive_server.py
```

#### Option D: Using UV (if installed)
```bash
cd backend-python
uv run python comprehensive_server.py
```

The server will start on: `http://localhost:8000/mcp`

### 2. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at: `http://localhost:5173`

## 🔧 Configuration

### Backend Configuration
- **Port**: 8000 (configurable in `comprehensive_server.py`)
- **Transport**: `streamable_http`
- **All CRUD operations**: Available as FastMCP tools

### Frontend Configuration
- **Server URL**: `http://localhost:8000/mcp` (configurable in `directHttpMcpClient.js`)
- **OpenAI API Key**: Required for AI responses
- **No process manager**: Direct HTTP connection

## 📁 Key Files Changed

### Backend
- `comprehensive_server.py`: Updated to use HTTP transport instead of stdio
- `start_server.py`: Python startup script
- `start_server.ps1`: PowerShell startup script  
- `start_server.bat`: Windows batch startup script

### Frontend
- `directHttpMcpClient.js`: New HTTP client for direct connection
- `directHttpAiMcpService.js`: New AI service using HTTP client
- `DirectMCPChatbot.jsx`: Updated to use new HTTP services

## 🛠️ Tool Functions

All hospital management operations are available as tools:

### User Management
- `create_user`
- `get_user_by_id`
- `list_users`
- `update_user`
- `delete_user`

### Patient Management
- `create_patient`
- `get_patient_by_id`
- `list_patients`
- `search_patients`

### Department Management
- `create_department`
- `get_department_by_id`
- `list_departments`

### Staff Management
- `create_staff`
- `get_staff_by_id`
- `list_staff`

### Equipment Management
- `create_equipment`
- `get_equipment_by_id`
- `list_equipment`
- `update_equipment_status`

### Bed Management
- `create_bed`
- `list_beds`
- `assign_bed_to_patient`
- `discharge_bed`

### Appointment Management
- `create_appointment`
- `list_appointments`

### Supply Management
- `create_supply`
- `list_supplies`
- `update_supply_stock`

And many more... (see `comprehensive_server.py` for complete list)

## 🔍 Testing the Connection

1. **Test Backend Health**:
   ```bash
   curl http://localhost:8000/mcp/health
   ```

2. **Test Frontend Connection**:
   - Open the frontend UI
   - Click "Test Server Connection"
   - Should show "✅ FastMCP Server is running and ready"

## 🐛 Troubleshooting

### Backend Issues
- **Port 8000 already in use**: Change the port in `comprehensive_server.py`
- **Missing dependencies**: Run the startup scripts which auto-install dependencies
- **Database connection**: Ensure PostgreSQL is running and configured

### Frontend Issues  
- **Cannot connect to server**: Ensure backend is running on port 8000
- **CORS errors**: Backend includes CORS headers for localhost
- **OpenAI API errors**: Verify your API key has GPT-4 access

### Common Issues
- **Server not starting**: Check Python version (3.12+ recommended)
- **Tools not loading**: Verify server is running and accessible
- **Database errors**: Check database configuration in `database.py`

## 📊 Benefits of Direct HTTP Architecture

1. **Simpler**: No process manager needed
2. **Faster**: Direct HTTP connection
3. **More Reliable**: Fewer moving parts
4. **Easier Debugging**: Direct communication
5. **Better Error Handling**: HTTP status codes
6. **Scalable**: Standard HTTP server architecture

## 🔗 API Endpoints

The FastMCP server exposes these endpoints:

- `GET /mcp/health` - Health check
- `GET /mcp/tools` - List available tools
- `POST /mcp/call` - Call a tool
- `GET /mcp/stats` - Server statistics (if available)

## 🚦 Next Steps

1. Start the backend server using one of the provided scripts
2. Start the frontend development server
3. Test the connection using the UI
4. Try hospital management operations through the chat interface

The system now provides a direct, efficient connection between your React frontend and Python FastMCP backend!
