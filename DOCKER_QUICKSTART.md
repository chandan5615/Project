# Docker Quick Start Guide

Get Sentinel Agent running in Docker in 5 minutes! Uses **Ollama** for local LLM inference - no API keys required!

## Prerequisites

- Linux server with Docker installed
- At least 8GB RAM (16GB recommended for larger models)
- ~5GB disk space for the LLM model

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

## Step 2: Clone the Project

```bash
# Clone repository
cd /opt
git clone <repository-url> sentinel-agent
cd sentinel-agent
```

## Step 3: Configure (Optional)

The default configuration works out of the box. Optionally create a `.env` file for custom settings:

```bash
# Create .env file (optional)
cat > .env << 'EOF'
# Ollama model to use (default: llama3:8b)
OLLAMA_MODEL=llama3:8b

# Log file paths (defaults shown)
AUTH_LOG_PATH=/var/log/auth.log
WEB_LOG_PATH=/var/log/apache2/access.log
EOF

chmod 600 .env
```

## Step 4: Build and Run

```bash
# Build and start all containers (Ollama + Sentinel Agent)
docker compose up -d

# This will:
# 1. Start Ollama server
# 2. Download the LLM model (first run only, ~4GB)
# 3. Start Sentinel Agent

# Watch the logs
docker compose logs -f
```

**Note:** First run takes 5-10 minutes to download the LLM model.

## Step 5: Verify

```bash
# Check all containers are running
docker compose ps

# Check Ollama is working
curl http://localhost:11434/api/tags

# View Sentinel Agent logs
docker compose logs sentinel-agent

# View attack records (after some activity)
docker compose exec sentinel-agent python view_attacks.py
```

## That's It!

Your Sentinel Agent is now running with a local Ollama LLM!

## Common Commands

```bash
# Stop all containers
docker compose stop

# Start all containers
docker compose start

# Restart all containers
docker compose restart

# View logs (all containers)
docker compose logs -f

# View logs (specific container)
docker compose logs -f sentinel-agent
docker compose logs -f ollama

# Stop and remove containers
docker compose down

# Stop and remove containers + delete model data
docker compose down -v
```

## Using Different Models

You can use different Ollama models by setting `OLLAMA_MODEL`:

```bash
# Smaller model (faster, uses less RAM)
echo "OLLAMA_MODEL=llama3.2:3b" > .env
docker compose up -d

# Larger model (slower, more accurate)
echo "OLLAMA_MODEL=llama3:70b" > .env
docker compose up -d
```

## GPU Support (NVIDIA)

For faster inference with NVIDIA GPU, edit `docker-compose.yml` and uncomment the GPU section under the `ollama` service:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

Then restart:
```bash
docker compose down
docker compose up -d
```

## Troubleshooting

### Model download is slow
The first run downloads ~4GB. Be patient or use a smaller model:
```bash
echo "OLLAMA_MODEL=llama3.2:3b" > .env
```

### Out of memory
Use a smaller model or increase system RAM:
```bash
echo "OLLAMA_MODEL=llama3.2:3b" > .env
```

### Container keeps restarting
Check logs for errors:
```bash
docker compose logs sentinel-agent
docker compose logs ollama
```

### Ollama not responding
```bash
# Check if Ollama container is running
docker compose ps ollama

# Restart Ollama
docker compose restart ollama
```

## Next Steps

- Read `DOCKER_DEPLOYMENT.md` for advanced configuration
- Set up systemd service for auto-start on boot
- Configure log rotation and backups
- Set up monitoring and alerting
