#!/bin/bash

# Deployment Script for Test Case API
# Supports both development and production deployments

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Test Case API Deployment"
echo "============================"
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Select deployment mode
echo "Select deployment mode:"
echo "1) Development (with admin interface)"
echo "2) Production (client interface only, with SSL)"
read -p "Enter choice (1-2): " MODE

case $MODE in
    1)
        ENV_FILE=".env.development"
        COMPOSE_FILE="docker-compose.yml"
        echo ""
        echo "📋 Development Deployment"
        ;;
    2)
        ENV_FILE=".env.production"
        COMPOSE_FILE="docker-compose.yml"
        echo ""
        echo "📋 Production Deployment"
        
        # Check for SSL certificates
        if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
            echo "⚠️  SSL certificates not found!"
            read -p "Do you want to set up SSL now? (y/n): " SETUP_SSL
            if [ "$SETUP_SSL" = "y" ]; then
                bash setup-ssl.sh
            else
                echo "❌ SSL certificates are required for production deployment"
                exit 1
            fi
        fi
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# Check for environment file
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  Environment file not found: $ENV_FILE"
    echo "Creating from template..."
    cp "${ENV_FILE}.example" "$ENV_FILE" 2>/dev/null || true
    echo "📝 Please edit $ENV_FILE with your configuration"
    read -p "Press Enter to continue..."
fi

# Pull/build images
echo ""
echo "📦 Pulling/building Docker images..."
docker-compose -f "$COMPOSE_FILE" build --no-cache

# Start services
echo ""
echo "🚀 Starting services..."
docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service status
echo ""
echo "🔍 Service Status:"
docker-compose -f "$COMPOSE_FILE" ps

# Health check
echo ""
echo "🏥 Health Check:"
if curl -f http://localhost/health &> /dev/null; then
    echo "✅ API is healthy"
else
    echo "⚠️  API health check failed. Check logs with: docker-compose logs -f"
fi

# Display access information
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Access URLs:"
if [ "$MODE" = "1" ]; then
    echo "   Admin Interface:  http://localhost/admin"
    echo "   Client Interface: http://localhost/client"
    echo "   API:              http://localhost/api/"
else
    echo "   Client Interface: https://localhost/client (or your domain)"
    echo "   API:              https://localhost/api/ (or your domain)"
    echo "   Note: Admin interface is disabled in production"
fi
echo ""
echo "📊 Useful commands:"
echo "   View logs:     docker-compose -f $COMPOSE_FILE logs -f"
echo "   Stop services: docker-compose -f $COMPOSE_FILE down"
echo "   Restart:       docker-compose -f $COMPOSE_FILE restart"
echo ""

# Pull Ollama model
echo "🤖 Setting up Ollama model..."
read -p "Do you want to pull the Ollama model now? (y/n): " PULL_MODEL
if [ "$PULL_MODEL" = "y" ]; then
    MODEL_NAME="llama3:latest"
    read -p "Enter model name (default: llama3:latest): " INPUT_MODEL
    MODEL_NAME=${INPUT_MODEL:-$MODEL_NAME}
    
    echo "Pulling model: $MODEL_NAME"
    docker exec test-case-ollama ollama pull "$MODEL_NAME"
    echo "✅ Model pulled successfully!"
fi

echo ""
echo "🎉 All done! Your Test Case API is ready to use."
