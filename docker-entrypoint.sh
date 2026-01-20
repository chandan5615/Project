#!/bin/bash
# Sentinel Agent - Docker Entrypoint Script

set -e

echo "=========================================="
echo "Sentinel Agent - Container Starting"
echo "=========================================="

# Check if API key is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "ERROR: GOOGLE_API_KEY environment variable is not set"
    echo "Please set it in docker-compose.yml or .env file"
    exit 1
fi

# Check if log files exist (warn if not)
if [ ! -f "${AUTH_LOG_PATH:-/var/log/auth.log}" ]; then
    echo "WARNING: Auth log file not found: ${AUTH_LOG_PATH:-/var/log/auth.log}"
    echo "The container will create it if possible, but monitoring may not work correctly"
fi

if [ ! -f "${WEB_LOG_PATH:-/var/log/apache2/access.log}" ]; then
    echo "WARNING: Web log file not found: ${WEB_LOG_PATH:-/var/log/apache2/access.log}"
    echo "The container will create it if possible, but monitoring may not work correctly"
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
echo "Configuration:"
echo "  Auth Log: ${AUTH_LOG_PATH:-/var/log/auth.log}"
echo "  Web Log: ${WEB_LOG_PATH:-/var/log/apache2/access.log}"
echo "  Data Directory: /app/data"
echo "  Logs Directory: /app/logs"
echo ""

# Execute the main command
exec "$@"
