#!/bin/bash
# Diagnostic script to check Sentinel Agent container status

echo "=============================================="
echo "Sentinel Agent Diagnostics"
echo "=============================================="
echo ""

echo "1. Container Status:"
docker-compose ps
echo ""

echo "2. Checking if container is running:"
docker ps | grep sentinel-agent
echo ""

echo "3. Latest container logs (last 50 lines):"
docker-compose logs --tail=50 sentinel-agent
echo ""

echo "4. Health check status:"
docker inspect sentinel-agent | grep -A 10 "Health"
echo ""

echo "5. Checking if API port 8000 is accessible:"
curl -s http://localhost:8000/api/health || echo "API not responding"
echo ""

echo "6. Checking if Ollama is running on host:"
curl -s http://localhost:11434/api/tags > /dev/null && echo "✓ Ollama is running" || echo "✗ Ollama is not running"
echo ""

echo "7. Network connectivity test:"
docker exec sentinel-agent curl -s http://localhost:11434/api/tags > /dev/null && echo "✓ Container can reach Ollama" || echo "✗ Container cannot reach Ollama"
echo ""

echo "=============================================="
echo "Diagnostics complete"
echo "=============================================="
