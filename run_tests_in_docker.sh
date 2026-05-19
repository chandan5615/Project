#!/bin/bash
# Run Sentinel Agent tests inside Docker container where permissions are available

set -e

TARGET_IP="${1:-10.87.146.89}"
CONTAINER_NAME="sentinel-agent"

echo "======================================================================"
echo "  Sentinel Agent - Running Tests in Docker"
echo "======================================================================"
echo ""
echo "Target: $TARGET_IP"
echo "Container: $CONTAINER_NAME"
echo ""

# Verify container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "❌ Container '$CONTAINER_NAME' is not running!"
    echo "   Run: docker-compose up -d"
    exit 1
fi

echo "📝 Running auth attack tests..."
docker exec "$CONTAINER_NAME" python3 test_attacks.py
echo ""

echo "📝 Running web attack tests..."
docker exec -e "SENTINEL_TEST_TARGET=http://localhost:8000" \
    "$CONTAINER_NAME" python3 test_web_attacks.py
echo ""

echo "✅ Tests completed!"
echo ""

echo "📊 Checking database for detected incidents..."
docker exec "$CONTAINER_NAME" sqlite3 /app/data/sentinel_intel.db \
    "SELECT COUNT(*) as total_incidents FROM incidents;" || echo "No incidents table"
echo ""

echo "🔐 Checking blocked IPs..."
docker exec "$CONTAINER_NAME" sqlite3 /app/data/sentinel_intel.db \
    "SELECT COUNT(*) as blocked_ips FROM blocked_ips WHERE status='active';" || echo "No active blocks"
echo ""

echo "⚪ Checking whitelisted IPs..."
docker exec "$CONTAINER_NAME" sqlite3 /app/data/sentinel_intel.db \
    "SELECT COUNT(*) as whitelisted FROM safe_ips;" || echo "No whitelist"
echo ""

echo "📋 Recent incidents:"
docker exec "$CONTAINER_NAME" sqlite3 /app/data/sentinel_intel.db \
    "SELECT source_ip, attack_type, severity FROM incidents ORDER BY timestamp DESC LIMIT 10;" || echo "No incidents"
echo ""

echo "======================================================================"
echo "  Test run complete!"
echo "======================================================================"
