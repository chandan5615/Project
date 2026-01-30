#!/usr/bin/env bash
# Tunnel helper for Zero-Exposure Admin Dashboard
# Usage:
#  - If dashboard runs inside container named 'sentinel-agent' and listens on 127.0.0.1:8080 inside the container:
#    ssh -L 8080:127.0.0.1:8080 user@remote-host
#  - If you run locally in Docker: run the dashboard inside the container and use 'docker exec' to start a temporary relay.

echo "One way to access the dashboard securely from your admin workstation:"
echo "  ssh -L 8080:127.0.0.1:8080 admin@your-server.example.com"
echo "Then open http://127.0.0.1:8080 in your browser and authenticate with Basic Auth."

echo "If you prefer Docker on the host: SSH to the host and run the dashboard locally (binds to 127.0.0.1):"
echo "  uvicorn dashboard.app:app --host 127.0.0.1 --port 8080"
echo "Then create the SSH tunnel from your workstation as above."
echo "Note: Do NOT publish dashboard ports in docker-compose; use SSH tunneling to avoid exposure."
