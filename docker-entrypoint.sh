#!/bin/bash
# Sentinel Agent - Docker Entrypoint Script
# Automatically detects Ollama on host or Docker

set -e

echo "=========================================="
echo "Sentinel Agent - Container Starting"
echo "=========================================="

# Ollama connection settings
OLLAMA_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11434}"
OLLAMA_MODEL_NAME="${OLLAMA_MODEL:-llama3:8b}"

echo ""
echo "Detecting Ollama server..."

# Function to check Ollama connection
check_ollama() {
    local url="$1"
    curl -s "${url}/api/tags" > /dev/null 2>&1
}

# Function to check if model exists
check_model() {
    local url="$1"
    local model="$2"
    curl -s "${url}/api/tags" 2>/dev/null | grep -q "$model"
}

# Try to connect to Ollama
MAX_RETRIES=60
RETRY_COUNT=0
OLLAMA_FOUND=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    # Check host Ollama (127.0.0.1:11434)
    if check_ollama "http://127.0.0.1:11434"; then
        OLLAMA_URL="http://127.0.0.1:11434"
        OLLAMA_FOUND=true
        echo "[SUCCESS] Found Ollama on host at ${OLLAMA_URL}"
        break
    fi
    
    # Check Docker Ollama (ollama:11434 - for bridge network)
    if check_ollama "http://ollama:11434"; then
        OLLAMA_URL="http://ollama:11434"
        OLLAMA_FOUND=true
        echo "[SUCCESS] Found Ollama in Docker at ${OLLAMA_URL}"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $((RETRY_COUNT % 10)) -eq 0 ]; then
        echo "Waiting for Ollama server... (attempt $RETRY_COUNT/$MAX_RETRIES)"
    fi
    sleep 2
done

if [ "$OLLAMA_FOUND" = false ]; then
    echo "[WARNING] Could not connect to Ollama server"
    echo "   Tried: http://127.0.0.1:11434 and http://ollama:11434"
    echo ""
    echo "   To fix this, either:"
    echo "   1. Install Ollama on host: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "   2. Or run with Docker Ollama: ./start.sh"
    echo ""
    echo "   Continuing anyway - the agent may fail to process events"
    OLLAMA_URL="http://127.0.0.1:11434"
else
    # Check if model is available
    echo "Checking for model: ${OLLAMA_MODEL_NAME}..."
    if check_model "$OLLAMA_URL" "$OLLAMA_MODEL_NAME"; then
        echo "[SUCCESS] Model ${OLLAMA_MODEL_NAME} is available"
    else
        echo "[WARNING] Model ${OLLAMA_MODEL_NAME} not found"
        echo "   Please pull it: ollama pull ${OLLAMA_MODEL_NAME}"
    fi
fi

# Export the detected URL for the Python application
export OLLAMA_BASE_URL="$OLLAMA_URL"

# Check if log files exist (warn if not)
echo ""
if [ ! -f "${AUTH_LOG_PATH:-/var/log/auth.log}" ]; then
    echo "[WARNING] Auth log not found: ${AUTH_LOG_PATH:-/var/log/auth.log}"
else
    echo "[SUCCESS] Auth log found: ${AUTH_LOG_PATH:-/var/log/auth.log}"
fi

if [ ! -f "${WEB_LOG_PATH:-/var/log/apache2/access.log}" ]; then
    echo "[WARNING] Web log not found: ${WEB_LOG_PATH:-/var/log/apache2/access.log}"
else
    echo "[SUCCESS] Web log found: ${WEB_LOG_PATH:-/var/log/apache2/access.log}"
fi

# Create data directory if it doesn't exist
mkdir -p /app/data /app/logs

# Set permissions
chmod 755 /app/data /app/logs

# Create /var/log/apache2 symlink for testing environments
if [ ! -d /var/log/apache2 ]; then
    mkdir -p /var/log/apache2
    touch /var/log/apache2/access.log
    echo "[INFO] Created Apache2 log directory"
fi

# Grant sentinel user sudo access for firewall operations
if [ "$(id -u)" = "0" ]; then
    echo "sentinel ALL=(ALL) NOPASSWD: /sbin/iptables, /sbin/iptables-save, /sbin/ip6tables" > /etc/sudoers.d/sentinel-firewall 2>/dev/null || true
    chmod 0440 /etc/sudoers.d/sentinel-firewall 2>/dev/null || true
fi

# Check if attack_records.json exists, create if not
if [ ! -f "/app/data/attack_records.json" ]; then
    echo "[]" > /app/data/attack_records.json
    chmod 644 /app/data/attack_records.json
fi

# Display configuration
echo ""
echo "=========================================="
echo "Configuration:"
echo "  Ollama URL: $OLLAMA_URL"
echo "  Ollama Model: ${OLLAMA_MODEL_NAME}"
echo "  Auth Log: ${AUTH_LOG_PATH:-/var/log/auth.log}"
echo "  Web Log: ${WEB_LOG_PATH:-/var/log/apache2/access.log}"
echo "  Data Directory: /app/data"
echo "=========================================="
echo ""
echo "Starting Sentinel Agent..."
echo ""

# Execute the main command
exec "$@"
