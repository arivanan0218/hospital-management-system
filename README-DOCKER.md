# Hospital Management System - Docker Deployment Guide

## Project Overview

This hospital management system consists of 3 main components:

1. **Backend Python** (Port 8000) - FastMCP server with PostgreSQL database
2. **MCP Process Manager** (Port 3001) - Node.js service for managing MCP servers
3. **Frontend** (Port 80) - React application with Vite build

## Prerequisites

- Docker and Docker Compose installed
- Git (to clone the repository)

## Quick Start

### 1. Environment Setup

Copy the environment template:
```bash
cp .env.docker .env
```

Edit `.env` file with your API keys:
- `GEMINI_API_KEY` - Required for backend AI features
- `VITE_CLAUDE_API_KEY` - Optional, for Claude AI
- `VITE_OPENAI_API_KEY` - Optional, for OpenAI GPT
- `VITE_GROQ_API_KEY` - Optional, for Groq AI
- `VITE_GOOGLE_API_KEY` - Optional, for Google AI

### 2. Deploy with Docker

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh start
```

**Windows:**
```cmd
deploy.bat start
```

### 3. Access the Application

- **Frontend**: http://localhost
- **MCP Manager**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **Database**: localhost:5432

## Available Commands

| Command | Description |
|---------|-------------|
| `start` | Build and start all services (default) |
| `stop` | Stop all services |
| `restart` | Restart all services |
| `logs` | Show logs from all services |
| `cleanup` | Stop services and remove volumes/networks |
| `status` | Show service status and URLs |

## Service Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│    Frontend     │───▶│  MCP Manager     │───▶│ Backend Python  │
│   (React/Vite)  │    │   (Node.js)      │    │   (FastMCP)     │
│     Port 80     │    │    Port 3001     │    │    Port 8000    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                  │                       │
                                  │                       ▼
                                  │              ┌─────────────────┐
                                  │              │   PostgreSQL    │
                                  │              │   Database      │
                                  │              │    Port 5432    │
                                  │              └─────────────────┘
                                  │
                               WebSocket
                              Connection
```

## Development vs Production

### Development Mode
```bash
# Backend Python
cd backend-python
python comprehensive_server.py

# MCP Manager
cd mcp-process-manager
node server.js

# Frontend
cd frontend
npm run dev
```

### Production Mode (Docker)
```bash
./deploy.sh start
```

## Database Management

The PostgreSQL database is automatically set up with:
- Database: `hospital_management`
- User: `postgres`
- Password: `postgres`
- Host: `postgres` (container) / `localhost` (external)
- Port: `5432`

### Database Initialization

The backend Python service automatically:
1. Creates database tables on startup
2. Sets up initial schema
3. Populates sample data if needed

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 80, 3001, 8000, and 5432 are not in use
2. **API keys missing**: Check `.env` file has required API keys
3. **Docker permissions**: On Linux, ensure user is in docker group

### View Logs
```bash
./deploy.sh logs
```

### Check Service Status
```bash
./deploy.sh status
```

### Clean Restart
```bash
./deploy.sh cleanup
./deploy.sh start
```

## Health Checks

All services include health checks:
- **Frontend**: Nginx status
- **MCP Manager**: HTTP endpoint `/mcp/status`
- **Backend**: Database connection test
- **Database**: PostgreSQL ready check

## Security Considerations

1. **Environment Variables**: Never commit `.env` with real API keys
2. **Database**: Change default PostgreSQL credentials in production
3. **Network**: Services communicate via Docker internal network
4. **CORS**: Configured for local development, adjust for production

## Scaling

For production scaling:
1. Use external managed PostgreSQL database
2. Deploy services to separate containers/servers
3. Add load balancer for frontend
4. Use environment-specific configuration
5. Implement proper logging and monitoring

## Monitoring

Access service health:
- MCP Manager Status: http://localhost:3001/mcp/status
- Available Tools: http://localhost:3001/mcp/tools

## Backup

Database data is persisted in Docker volume `postgres_data`. To backup:
```bash
docker-compose exec postgres pg_dump -U postgres hospital_management > backup.sql
```

To restore:
```bash
cat backup.sql | docker-compose exec -T postgres psql -U postgres hospital_management
```
