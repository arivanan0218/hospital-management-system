# MCP Process Manager Dockerfile
FROM node:18-alpine

# Install Python and required dependencies including bash and PostgreSQL client
RUN apk add --no-cache python3 py3-pip python3-dev gcc musl-dev postgresql-dev libffi-dev bash postgresql-client

# Install UV package manager (with system packages override for Alpine)
RUN pip3 install uv --break-system-packages

# Set working directory
WORKDIR /app

# Copy package files
COPY mcp-process-manager/package*.json ./

# Install dependencies as root
RUN npm install --production

# Verify express installation
RUN node -e "console.log('Express version:', require('express/package.json').version)"

# Copy application code from the root context
COPY mcp-process-manager/ ./

# Copy backend-python files for MCP server access
COPY backend-python/ ./backend-python

# Make scripts executable
RUN chmod +x ./backend-python/start_mcp_server.sh

# Install Python dependencies using UV (as root)
WORKDIR /app/backend-python
RUN uv sync
WORKDIR /app

# Create non-root user and change ownership
RUN addgroup -g 1001 appgroup && adduser -u 1001 -G appgroup -s /bin/sh -D appuser
RUN chown -R appuser:appgroup /app
USER appuser

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "const http = require('http'); http.get('http://localhost:3001/mcp/status', (res) => process.exit(res.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))"

# Start the server
CMD ["node", "server.js"]
