# Frontend Dockerfile
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Accept build argument for MCP bridge URL
ARG VITE_MCP_BRIDGE_URL=http://localhost:3001

# Set environment variable for Vite build
ENV VITE_MCP_BRIDGE_URL=$VITE_MCP_BRIDGE_URL

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application with environment variables
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
