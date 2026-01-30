# PowerShell helper: Tunnel to the internal dashboard using SSH local port forwarding
# Example:
#  ssh -L 8080:127.0.0.1:8080 admin@your-server.example.com
Write-Host "To securely access the dashboard, run:"
Write-Host "  ssh -L 8080:127.0.0.1:8080 admin@your-server.example.com"
Write-Host "Then browse to http://127.0.0.1:8080"
