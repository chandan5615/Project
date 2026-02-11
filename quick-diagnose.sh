#!/bin/bash
# Quick diagnostic - find out why container isn't healthy

echo "=== Container Status ==="
docker-compose ps

echo ""
echo "=== Last 100 Lines of Logs ==="
docker-compose logs --tail=100 sentinel-agent

echo ""
echo "=== Checking API Port 8000 ==="
sleep 3
curl -v http://localhost:8000/api/health 2>&1 || echo "Failed to connect"

echo ""
echo "=== Health Check Command Test (from inside container) ==="
docker exec sentinel-agent curl -f http://localhost:8000/api/health 2>&1 || echo "Health check failed"

echo ""
echo "=== Processes Inside Container ==="
docker exec sentinel-agent ps aux

echo ""
echo "=== Checking if Python processes are running ==="
docker exec sentinel-agent pgrep -a python
