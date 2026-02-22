#!/bin/bash
# Sentinel Agent - Smart Startup Script
# Automatically detects if Ollama is running on host or needs Docker

set -e

OLLAMA_MODEL="${OLLAMA_MODEL:-llama3:8b}"
OLLAMA_URL="http://127.0.0.1:11434"

echo "=========================================="
echo "  Sentinel Agent - Smart Startup"
echo "=========================================="
echo ""

# Function to check if Ollama is running on host
check_host_ollama() {
    if curl -s "${OLLAMA_URL}/api/tags" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check if model is available
check_model() {
    local host="$1"
    if curl -s "${host}/api/tags" 2>/dev/null | grep -q "$OLLAMA_MODEL"; then
        return 0
    else
        return 1
    fi
}

# Check if Ollama is running on host
echo "Checking for Ollama on host system..."
if check_host_ollama; then
    echo "✅ Ollama is running on host at ${OLLAMA_URL}"
    
    # Check if model is available
    echo "Checking for model: ${OLLAMA_MODEL}..."
    if check_model "${OLLAMA_URL}"; then
        echo "✅ Model ${OLLAMA_MODEL} is available"
    else
        echo "⚠️  Model ${OLLAMA_MODEL} not found. Pulling..."
        ollama pull "${OLLAMA_MODEL}"
        echo "✅ Model pulled successfully"
    fi
    
    echo ""
    echo "Starting Sentinel Agent (using host Ollama)..."
    docker compose up -d --build sentinel-agent
    
else
    echo "❌ Ollama not found on host"
    echo ""
    echo "Starting Ollama in Docker..."
    
    # Start with the ollama profile
    docker compose --profile with-ollama up -d --build
    
    echo ""
    echo "Waiting for Ollama to be ready..."
    
    # Wait for Ollama container to be healthy
    RETRIES=30
    while [ $RETRIES -gt 0 ]; do
        if docker compose exec -T ollama ollama list > /dev/null 2>&1; then
            echo "✅ Ollama is ready"
            break
        fi
        echo "  Waiting... ($RETRIES attempts remaining)"
        sleep 5
        RETRIES=$((RETRIES - 1))
    done
    
    if [ $RETRIES -eq 0 ]; then
        echo "❌ Ollama failed to start. Check logs with: docker compose logs ollama"
        exit 1
    fi
    
    # Pull model if needed
    echo "Checking for model: ${OLLAMA_MODEL}..."
    if ! docker compose exec -T ollama ollama list | grep -q "$OLLAMA_MODEL"; then
        echo "Pulling model ${OLLAMA_MODEL}... (this may take a few minutes)"
        docker compose exec -T ollama ollama pull "${OLLAMA_MODEL}"
        echo "✅ Model pulled successfully"
    else
        echo "✅ Model ${OLLAMA_MODEL} is available"
    fi
fi

echo ""
echo "=========================================="
echo "  Sentinel Agent Started Successfully!"
echo "=========================================="
echo ""
echo "Useful commands:"
echo "  View logs:     docker compose logs -f"
echo "  Stop:          docker compose down"
echo "  View attacks:  docker compose exec sentinel-agent python view_attacks.py"
echo ""
echo "Ollama URL: ${OLLAMA_URL}"
echo "Model: ${OLLAMA_MODEL}"
echo ""

# Show container status
docker compose ps
