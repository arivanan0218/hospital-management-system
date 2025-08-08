# MCP Process Manager Dockerfile
FROM node:18-alpine

# Install Python and required dependencies
RUN apk add --no-cache python3 py3-pip python3-dev gcc musl-dev

# Install UV package manager (with system packages override for Alpine)
RUN pip3 install uv --break-system-packages

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies as root
RUN npm install --production

# Verify express installation
RUN node -e "console.log('Express version:', require('express/package.json').version)"

# Copy application code
COPY . .

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
