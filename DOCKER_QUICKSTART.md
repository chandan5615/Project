# Docker Quick Start Guide

Get Sentinel Agent running in Docker in 5 minutes!

## Prerequisites

- Linux server with Docker installed
- Google Gemini API key

## Step 1: Install Docker (if not installed)

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker compose version
```

## Step 2: Get the Project

```bash
# Clone or download project
cd /opt
git clone <repository-url> sentinel-agent
cd sentinel-agent

# OR extract downloaded files
# cd /opt/sentinel-agent
```

## Step 3: Configure

```bash
# Create .env file
cat > .env << EOF
GOOGLE_API_KEY=your-api-key-here
AUTH_LOG_PATH=/var/log/auth.log
WEB_LOG_PATH=/var/log/apache2/access.log
EOF

# Secure it
chmod 600 .env
```

## Step 4: Build and Run

```bash
# Build image
docker compose build

# Start container
docker compose up -d

# View logs
docker compose logs -f
```

## Step 5: Verify

```bash
# Check container status
docker compose ps

# View attack records (after some time)
docker compose exec sentinel-agent python view_attacks.py
```

## That's It!

Your Sentinel Agent is now running in Docker!

## Common Commands

```bash
# Stop
docker compose stop

# Start
docker compose start

# Restart
docker compose restart

# View logs
docker compose logs -f

# Stop and remove
docker compose down
```

## Next Steps

- Read `DOCKER_DEPLOYMENT.md` for detailed configuration
- Set up systemd service for auto-start
- Configure backups
- Set up monitoring
