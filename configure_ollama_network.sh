#!/bin/bash
# ==============================================================================
# Sentinel Agent - Configure Ollama for Docker Access
# ==============================================================================
# This script fixes the most common deployment issue:
# "Cannot reach Ollama server at http://127.0.0.1:11434"
#
# ROOT CAUSE:
# Ollama defaults to listening on 127.0.0.1:11434 (localhost only).
# Docker containers in bridge network mode cannot reach the host's localhost.
#
# FIX:
# Configure Ollama to listen on 0.0.0.0:11434 (all network interfaces).
# This allows containers to reach it via host.docker.internal.
#
# USAGE:
#   chmod +x configure_ollama_network.sh
#   sudo ./configure_ollama_network.sh
#
# SECURITY NOTE:
# This makes Ollama accessible on your local network (192.168.x.x).
# If you need to restrict access further, use firewall rules.
# ==============================================================================

set -e  # Exit on error

echo "=========================================="
echo "Sentinel Agent - Ollama Network Configuration"
echo "=========================================="
echo ""

# Check if running as root/sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: This script must be run as root (use sudo)"
    echo "   Usage: sudo $0"
    exit 1
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Error: Ollama is not installed"
    echo ""
    echo "Install Ollama first:"
    echo "  curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

echo "✓ Ollama is installed"
echo ""

# Check current Ollama binding
echo "Checking current Ollama network binding..."
CURRENT_BINDING=$(ss -tlnp 2>/dev/null | grep 11434 | head -n1 || echo "not running")

if echo "$CURRENT_BINDING" | grep -q "127.0.0.1:11434"; then
    echo "⚠️  Ollama is currently bound to localhost only (127.0.0.1:11434)"
    echo "   This WILL CAUSE connection errors from Docker containers."
    echo ""
elif echo "$CURRENT_BINDING" | grep -q "\*:11434"; then
    echo "✓ Ollama is already bound to all interfaces (*:11434)"
    echo "   No changes needed - configuration is correct!"
    echo ""
    read -p "Continue anyway to ensure persistence? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
else
    echo "⚠️  Ollama is not currently running"
    echo ""
fi

# Create systemd override directory
echo "Creating systemd service override directory..."
mkdir -p /etc/systemd/system/ollama.service.d/
echo "✓ Directory created: /etc/systemd/system/ollama.service.d/"
echo ""

# Create override configuration
echo "Creating service override configuration..."
cat > /etc/systemd/system/ollama.service.d/override.conf <<EOF
# Sentinel Agent - Ollama Network Configuration
# Makes Ollama accessible to Docker containers via host.docker.internal
# Created: $(date)

[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF

echo "✓ Override configuration created:"
echo "   File: /etc/systemd/system/ollama.service.d/override.conf"
echo "   Config: OLLAMA_HOST=0.0.0.0:11434"
echo ""

# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload
echo "✓ Systemd reloaded"
echo ""

# Restart Ollama service
echo "Restarting Ollama service..."
systemctl restart ollama

# Wait for service to start
echo "Waiting for Ollama to start..."
sleep 5

# Check if service started successfully
if systemctl is-active --quiet ollama; then
    echo "✓ Ollama service is running"
else
    echo "❌ Error: Ollama service failed to start"
    echo ""
    echo "Check logs:"
    echo "  sudo journalctl -u ollama -n 50"
    exit 1
fi
echo ""

# Verify new binding
echo "Verifying new network binding..."
sleep 2
NEW_BINDING=$(ss -tlnp 2>/dev/null | grep 11434 | head -n1 || echo "")

if [ -z "$NEW_BINDING" ]; then
    echo "❌ Warning: Cannot detect Ollama binding"
    echo "   Ollama may not be listening on port 11434"
    echo ""
    echo "Manual check:"
    echo "  ss -tlnp | grep 11434"
elif echo "$NEW_BINDING" | grep -q "\*:11434"; then
    echo "✅ SUCCESS! Ollama is now bound to all interfaces (*:11434)"
    echo "   Docker containers can now reach it via host.docker.internal:11434"
elif echo "$NEW_BINDING" | grep -q ":::11434"; then
    echo "✅ SUCCESS! Ollama is now bound to all interfaces (:::11434 - IPv6)"
    echo "   Docker containers can now reach it via host.docker.internal:11434"
else
    echo "⚠️  Unexpected binding: $NEW_BINDING"
    echo "   Expected: *:11434"
fi
echo ""

# Test connectivity
echo "Testing Ollama connectivity..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama API is responsive on localhost"
else
    echo "⚠️  Warning: Cannot reach Ollama API on localhost"
fi

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')
if [ -n "$SERVER_IP" ] && [ "$SERVER_IP" != "127.0.0.1" ]; then
    echo "Testing Ollama on server IP ($SERVER_IP)..."
    if curl -s "http://${SERVER_IP}:11434/api/tags" > /dev/null 2>&1; then
        echo "✅ Ollama API is responsive on server IP"
    else
        echo "⚠️  Warning: Cannot reach Ollama API on server IP"
        echo "   This may be due to firewall rules"
    fi
fi
echo ""

# Summary
echo "=========================================="
echo "✅ Configuration Complete!"
echo "=========================================="
echo ""
echo "Ollama is now configured to listen on all network interfaces."
echo "Docker containers can connect via: http://host.docker.internal:11434"
echo ""
echo "VERIFICATION COMMANDS:"
echo "  # Check binding"
echo "  ss -tlnp | grep 11434"
echo ""
echo "  # Test from host"
echo "  curl http://localhost:11434/api/tags"
echo ""
if [ -n "$SERVER_IP" ] && [ "$SERVER_IP" != "127.0.0.1" ]; then
echo "  # Test from network"
echo "  curl http://${SERVER_IP}:11434/api/tags"
echo ""
fi
echo "  # Test from Docker container (after restarting Sentinel)"
echo "  docker exec sentinel-agent curl http://host.docker.internal:11434/api/tags"
echo ""
echo "NEXT STEPS:"
echo "  1. Restart Sentinel Agent container:"
echo "     cd ~/Project"
echo "     docker-compose restart sentinel-agent"
echo ""
echo "  2. Watch logs for success message:"
echo "     docker-compose logs -f sentinel-agent | grep Ollama"
echo ""
echo "  3. Expected output:"
echo "     [SUCCESS] Found Ollama via host.docker.internal at http://host.docker.internal:11434"
echo ""
echo "SECURITY NOTE:"
echo "  Ollama is now accessible on your local network."
echo "  To restrict access, use firewall rules:"
echo "    sudo ufw allow from 172.16.0.0/12 to any port 11434  # Docker only"
echo ""
echo "Configuration persists across reboots (systemd override)."
echo ""
