# Build stage
FROM node:24-alpine AS builder

WORKDIR /app

# Declare build argument for API URL
ARG VITE_API_URL
# Set as environment variable for Vite
ENV VITE_API_BASE_URL=$VITE_API_URL

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application (Vite will use VITE_API_URL)
RUN npm run build

# Production stage
FROM node:24-alpine

WORKDIR /app

# Install serve to run the built app
RUN npm install -g serve

# Copy built assets from builder
COPY --from=builder /app/dist ./dist

# Create non-root user (use existing node user or create new one)
RUN adduser -D -u 1001 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check (required for Container Apps)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ || exit 1

# Serve the application
CMD ["serve", "-s", "dist", "-l", "8080"]
