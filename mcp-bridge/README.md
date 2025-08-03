# Hospital Management System MCP Bridge

This directory contains the MCP Bridge that provides an HTTP API gateway for the Hospital Management System MCP Server. The bridge allows you to interact with the MCP server through standard HTTP REST API calls instead of the stdio MCP protocol.

## Overview

The MCP Bridge consists of:

- **mcp_bridge.py**: Main bridge server that spawns the comprehensive_server.py as a subprocess and translates HTTP requests to MCP protocol calls
- **client.py**: Example HTTP client for testing the bridge functionality
- **requirements.txt**: Python dependencies for the bridge
- **start_bridge.bat/sh**: Scripts to start the bridge server
- **test_bridge.bat/sh**: Scripts to test the bridge functionality

## Architecture

```
HTTP Client → MCP Bridge (HTTP API) → MCP Server (stdio) → Database
```

The bridge:
1. Accepts HTTP requests on port 8080
2. Translates them to MCP protocol messages
3. Communicates with the comprehensive_server.py via stdin/stdout
4. Returns HTTP responses with the results

## Quick Start

### Windows

1. Start the bridge server:
   ```cmd
   start_bridge.bat
   ```

2. In another terminal, test the bridge:
   ```cmd
   test_bridge.bat
   ```

### Linux/macOS

1. Make scripts executable:
   ```bash
   chmod +x start_bridge.sh test_bridge.sh
   ```

2. Start the bridge server:
   ```bash
   ./start_bridge.sh
   ```

3. In another terminal, test the bridge:
   ```bash
   ./test_bridge.sh
   ```

## Manual Setup

If you prefer to set up manually:

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the bridge:
   ```bash
   python mcp_bridge.py
   ```

4. Test the bridge:
   ```bash
   python client.py
   ```

## API Endpoints

The bridge provides both generic MCP tool endpoints and convenience endpoints for common operations:

### Generic Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /tools` - List all available MCP tools
- `POST /tools/{tool_name}` - Call any MCP tool with JSON payload

### Convenience Endpoints

#### Users
- `POST /users` - Create user
- `GET /users` - List users
- `GET /users/{user_id}` - Get user by ID

#### Patients
- `POST /patients` - Create patient
- `GET /patients` - List patients
- `GET /patients/{patient_id}` - Get patient by ID

#### Departments
- `POST /departments` - Create department
- `GET /departments` - List departments
- `GET /departments/{department_id}` - Get department by ID

#### Beds
- `POST /beds` - Create bed
- `GET /beds[?status=available]` - List beds (optionally filter by status)
- `POST /beds/{bed_id}/assign` - Assign bed to patient
- `POST /beds/{bed_id}/discharge` - Discharge patient from bed

#### Other Resources
- `GET /staff[?department_id=...&status=...]` - List staff
- `GET /equipment[?status=...&department_id=...]` - List equipment
- `GET /supplies[?low_stock_only=true]` - List supplies
- `GET /appointments[?doctor_id=...&patient_id=...&date=...]` - List appointments

## Example Usage

### Using curl

1. Check health:
   ```bash
   curl http://localhost:8080/health
   ```

2. List all tools:
   ```bash
   curl http://localhost:8080/tools
   ```

3. Create a user:
   ```bash
   curl -X POST http://localhost:8080/users \
     -H "Content-Type: application/json" \
     -d '{
       "username": "doctor1",
       "email": "doctor1@hospital.com",
       "password_hash": "hashed_password",
       "role": "doctor",
       "first_name": "John",
       "last_name": "Doe"
     }'
   ```

4. List users:
   ```bash
   curl http://localhost:8080/users
   ```

5. Call any MCP tool directly:
   ```bash
   curl -X POST http://localhost:8080/tools/create_department \
     -H "Content-Type: application/json" \
     -d '{"name": "Cardiology", "description": "Heart specialists"}'
   ```

### Using the Python client

```python
from client import MCPHttpClient

async def example():
    client = MCPHttpClient()
    
    # Create a user
    user = await client.create_user(
        username="nurse1",
        email="nurse1@hospital.com",
        password_hash="hashed_password",
        role="nurse",
        first_name="Jane",
        last_name="Smith"
    )
    
    # List all users
    users = await client.list_users()
    print(f"Total users: {users['count']}")
    
    await client.close()
```

## Configuration

The bridge server runs on `localhost:8080` by default. You can modify this in `mcp_bridge.py`:

```python
if __name__ == "__main__":
    uvicorn.run(
        "mcp_bridge:app",
        host="0.0.0.0",  # Change host
        port=8080,       # Change port
        reload=False,
        log_level="info"
    )
```

## Error Handling

The bridge handles errors at multiple levels:
- HTTP errors (400, 404, 500, etc.)
- MCP protocol errors
- Database connection errors
- Subprocess communication errors

All errors are logged and returned as structured JSON responses.

## Dependencies

The bridge requires:
- FastAPI for HTTP server
- uvicorn for ASGI server
- httpx for HTTP client testing
- asyncio for async operations
- The comprehensive_server.py MCP server

## Troubleshooting

1. **Bridge won't start**: Check that Python and all dependencies are installed
2. **MCP server errors**: Ensure the database is set up and accessible
3. **Connection refused**: Make sure the bridge is running on the expected port
4. **Tool not found**: Use `GET /tools` to see available tools
5. **Database errors**: Check the comprehensive_server.py database configuration

## Security Considerations

For production use:
- Configure CORS properly (currently allows all origins)
- Add authentication/authorization
- Use HTTPS
- Validate input parameters
- Rate limiting
- Logging and monitoring

This bridge is designed for development and testing. Additional security measures should be implemented for production deployment.
