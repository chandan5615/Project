#!/bin/bash
# Sentinel Agent - Docker Entrypoint Script

set -e

echo "=========================================="
echo "Sentinel Agent - Container Starting"
echo "=========================================="

# Check Ollama connection
OLLAMA_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11434}"
echo "Checking Ollama connection at: $OLLAMA_URL"

MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s "${OLLAMA_URL}/api/tags" > /dev/null 2>&1; then
        echo "✅ Ollama server is reachable"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Waiting for Ollama server... (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "⚠️  WARNING: Could not connect to Ollama server at $OLLAMA_URL"
    echo "   Make sure Ollama is running and accessible"
    echo "   Continuing anyway - the agent may fail to process events"
fi

# Display model info
echo "Using Ollama model: ${OLLAMA_MODEL:-llama3:8b}"

# Check if log files exist (warn if not)
if [ ! -f "${AUTH_LOG_PATH:-/var/log/auth.log}" ]; then
    echo "⚠️  WARNING: Auth log file not found: ${AUTH_LOG_PATH:-/var/log/auth.log}"
    echo "   The container will monitor for it, but it may not exist yet"
fi

if [ ! -f "${WEB_LOG_PATH:-/var/log/apache2/access.log}" ]; then
    echo "⚠️  WARNING: Web log file not found: ${WEB_LOG_PATH:-/var/log/apache2/access.log}"
    echo "   The container will monitor for it, but it may not exist yet"
fi

# Create data directory if it doesn't exist
mkdir -p /app/data /app/logs

# Set permissions
chmod 755 /app/data /app/logs

# Check if attack_records.json exists, create if not
if [ ! -f "/app/data/attack_records.json" ]; then
    echo "[]" > /app/data/attack_records.json
    chmod 644 /app/data/attack_records.json
fi

# Display configuration
echo ""
echo "Configuration:"
echo "  Ollama URL: $OLLAMA_URL"
echo "  Ollama Model: ${OLLAMA_MODEL:-llama3:8b}"
echo "  Auth Log: ${AUTH_LOG_PATH:-/var/log/auth.log}"
echo "  Web Log: ${WEB_LOG_PATH:-/var/log/apache2/access.log}"
echo "  Data Directory: /app/data"
echo "  Logs Directory: /app/logs"
echo ""
echo "=========================================="
echo "Starting Sentinel Agent..."
echo "=========================================="

# Execute the main command
exec "$@"
