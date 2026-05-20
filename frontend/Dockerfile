# Build stage
FROM node:20-slim as builder

# Install wget and curl for healthchecks (useful for dev mode)
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget curl && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the frontend code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Install wget for healthchecks
RUN apk add --no-cache wget

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]