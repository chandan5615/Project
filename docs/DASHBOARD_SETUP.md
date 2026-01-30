# Zero-Exposure Admin Dashboard — Setup

Overview
- The Dashboard is implemented as a FastAPI app (`dashboard/app.py`). It is intended to bind to `127.0.0.1` inside the runtime so it is not reachable from external networks by default.

Running locally (recommended for testing)
1. Activate your project's virtual environment (PowerShell):
   ```powershell
   . .\venv\Scripts\Activate.ps1
   ```
2. Install requirements for dashboard (FastAPI + Uvicorn):
   ```powershell
   pip install fastapi uvicorn
   ```
3. Run the dashboard (binds to 127.0.0.1):
   ```powershell
   uvicorn dashboard.app:app --host 127.0.0.1 --port 8080
   ```
4. Open `http://127.0.0.1:8080` in your browser. You will be prompted for Basic Auth credentials.

Secure access via SSH tunnel
- From your admin workstation:
  ssh -L 8080:127.0.0.1:8080 admin@your-server.example.com
- Then open `http://127.0.0.1:8080` locally.

Docker Compose (internal-only, no published ports)
- Use the `dashboard` profile so the dashboard service is optional and not started by default:
  ```bash
  docker compose up -d --profile dashboard
  ```
- The compose service is intentionally configured with `network_mode: none` and **does not** publish ports.
- To securely access it remotely, SSH to the host and start the dashboard there or use an SSH tunnel to the host's loopback (recommended). Example:
  ```bash
  # On remote host
  uvicorn dashboard.app:app --host 127.0.0.1 --port 8080

  # On admin workstation
  ssh -L 8080:127.0.0.1:8080 admin@your-server.example.com
  # Then open http://127.0.0.1:8080 locally
  ```

Basic Auth and WebSocket token
- The dashboard requires HTTP Basic credentials defined by environment variables:
  - `DASHBOARD_USER` (default: `sentinel`)
  - `DASHBOARD_PASS` (default: `sentinel`)
- When you load the dashboard in your browser (after Basic Auth), it generates a short-lived WebSocket token (TTL configurable by `DASHBOARD_WS_TOKEN_TTL`) used to upgrade to `ws://`.
- Do not expose these credentials publicly; change them in production and store secrets securely.

Docker Notes
- **Do not** publish the dashboard port in docker-compose or Dockerfile. If you need remote access, create an SSH tunnel to the host machine; do not expose the service publicly.

Tunnel helper
- Use `scripts/tunnel_admin.sh` or `scripts/tunnel_admin.ps1` for quick instructions.
