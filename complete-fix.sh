#!/bin/bash
# One-Command Fix for Sentinel Agent Health Check Issue
# This script completely rebuilds the container with all fixes

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Sentinel Agent - Complete Rebuild & Fix               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

step() {
    echo -e "${BLUE}▶${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# Step 1: Check prerequisites
step "Checking prerequisites..."

if ! command -v docker-compose &> /dev/null; then
    error "docker-compose not found. Please install Docker Compose."
    exit 1
fi
success "Docker Compose found"

if ! command -v ollama &> /dev/null; then
    warning "Ollama not found in PATH"
    echo "  Make sure Ollama is installed and running"
else
    success "Ollama found"
fi
echo ""

# Step 2: Stop existing container
step "Stopping existing containers..."
docker-compose down 2>/dev/null || true
success "Containers stopped"
echo ""

# Step 3: Clean old data
step "Cleaning old data..."
rm -f data/auth.db data/INITIAL_CREDENTIALS.txt data/*.json data/*.db .sentinel_* 2>/dev/null || true
success "Old data cleaned"
echo ""

# Step 4: Check if Ollama is running
step "Checking Ollama server..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    success "Ollama is running on localhost:11434"
else
    warning "Ollama doesn't seem to be running"
    echo ""
    echo "Please start Ollama in another terminal:"
    echo "  ${BLUE}ollama serve${NC}"
    echo ""
    read -p "Press Enter when Ollama is running, or Ctrl+C to exit..."
fi
echo ""

# Step 5: Pull/verify model
step "Checking for llama3:8b model..."
if ollama list 2>/dev/null | grep -q "llama3:8b"; then
    success "Model llama3:8b is available"
else
    warning "Model llama3:8b not found"
    echo "  Pulling model (this may take a while)..."
    ollama pull llama3:8b
    success "Model downloaded"
fi
echo ""

# Step 6: Build container
step "Building container (this takes 3-5 minutes)..."
echo ""
if docker-compose build --no-cache; then
    echo ""
    success "Container built successfully"
else
    echo ""
    error "Build failed. Check errors above."
    exit 1
fi
echo ""

# Step 7: Start container
step "Starting container..."
docker-compose up -d
success "Container started"
echo ""

# Step 8: Wait for health check
step "Waiting for container to become healthy..."
echo "  This may take up to 90 seconds..."
echo ""

SECONDS_WAITED=0
MAX_WAIT=120

while [ $SECONDS_WAITED -lt $MAX_WAIT ]; do
    STATUS=$(docker-compose ps sentinel-agent 2>/dev/null | grep sentinel-agent | grep -o "(healthy)" || echo "")
    
    if [ -n "$STATUS" ]; then
        echo ""
        success "Container is HEALTHY! (took ${SECONDS_WAITED} seconds)"
        break
    fi
    
    # Show progress every 10 seconds
    if [ $((SECONDS_WAITED % 10)) -eq 0 ] && [ $SECONDS_WAITED -gt 0 ]; then
        echo "  Still waiting... (${SECONDS_WAITED}s / ${MAX_WAIT}s)"
    fi
    
    sleep 2
    SECONDS_WAITED=$((SECONDS_WAITED + 2))
done

echo ""

# Check final status
if docker-compose ps sentinel-agent 2>/dev/null | grep -q "(healthy)"; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                  ✓ SUCCESS!                                ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Extract credentials
    step "Extracting admin credentials..."
    echo ""
    docker-compose logs sentinel-agent | grep -A 3 "DEFAULT ADMIN CREDENTIALS"
    echo ""
    
    success "Setup complete! Next steps:"
    echo ""
    echo "  1. Run automated setup:"
    echo "     ${GREEN}python3 sentinel_auto.py setup${NC}"
    echo ""
    echo "  2. Run demo attacks:"
    echo "     ${GREEN}python3 sentinel_auto.py demo${NC}"
    echo ""
    echo "  3. Access the services:"
    echo "     API: ${BLUE}http://localhost:8000${NC}"
    echo "     Dashboard: ${BLUE}http://localhost:8501${NC}"
    echo ""
    
else
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                ✗ CONTAINER UNHEALTHY                       ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    error "Container did not become healthy after ${SECONDS_WAITED} seconds"
    echo ""
    echo "Troubleshooting steps:"
    echo ""
    echo "  1. Check container logs:"
    echo "     ${YELLOW}docker-compose logs sentinel-agent${NC}"
    echo ""
    echo "  2. Run diagnostics:"
    echo "     ${YELLOW}chmod +x quick-diagnose.sh && ./quick-diagnose.sh${NC}"
    echo ""
    echo "  3. Test API startup:"
    echo "     ${YELLOW}docker exec sentinel-agent python test_api_startup.py${NC}"
    echo ""
    echo "  4. Check the debug guide:"
    echo "     ${YELLOW}cat HEALTHCHECK_DEBUG.md${NC}"
    echo ""
    
    exit 1
fi
