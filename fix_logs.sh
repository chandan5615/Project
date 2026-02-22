#!/bin/bash
# ==============================================================================
# Sentinel Agent - Fix Log Paths
# ==============================================================================
# This script updates the log paths to use actual system logs
# ==============================================================================

echo "🔧 Stopping Sentinel Agent..."
docker-compose down

echo ""
echo "🚀 Starting Sentinel Agent with correct log paths..."
# Set environment variables for log paths
export AUTH_LOG_PATH=/var/log/auth.log
export WEB_LOG_PATH=/var/log/apache2/access.log

docker-compose up -d

echo ""
echo "⏳ Waiting 10 seconds for initialization..."
sleep 10

echo ""
echo "📊 Checking logs..."
docker-compose logs sentinel-agent --tail=50 | grep -E "Auth log monitoring|Web log monitoring|Monitoring"

echo ""
echo "✅ Done! Agent should now be monitoring:"
echo "   - Auth log: /var/log/auth.log"
echo "   - Apache log: /var/log/apache2/access.log"
echo ""
echo "📈 View live logs with:"
echo "   docker-compose logs -f sentinel-agent"
