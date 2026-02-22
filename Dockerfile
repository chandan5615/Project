# Sentinel Agent v2.2 - Dockerfile
# Multi-stage build for optimized production image
# 
# BUILD IMAGE: python:3.10-slim (includes build tools)
# FINAL IMAGE: python:3.10-slim (minimal, optimized)
# 
# Features:
# - All dependencies pre-installed
# - Optimized for security analysis
# - Ready for AIml, CrewAI, FastAPI
# - Ollama integration built-in
# - iptables and networking tools included

# ============================================================================
# STAGE 1: BUILDER - Compile dependencies
# ============================================================================
FROM python:3.10-slim AS builder

WORKDIR /app

# Install build dependencies (only needed for compilation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    make \
    libc6-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and create virtual environment
COPY requirements.txt .

# Create virtual environment and install packages
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# STAGE 2: RUNTIME - Production image
# ============================================================================
FROM python:3.10-slim

LABEL maintainer="Sentinel Agent Development Team"
LABEL version="2.2"
LABEL description="Autonomous AI Security Operations Center (SOC) analyst"

# Install runtime dependencies only (smaller final image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Firewall & networking
    iptables \
    net-tools \
    iproute2 \
    # Utilities
    curl \
    wget \
    git \
    # System tools
    procps \
    util-linux \
    # Debugging
    strace \
    lsof \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    SENTINEL_VERSION="2.2" \
    SENTINEL_LOG_DIR=/app/logs \
    SENTINEL_DATA_DIR=/app/data \
    LOG_LEVEL=INFO

# Create application directory
WORKDIR /app

# Copy application code
COPY . .

# Create entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Copy startup script (starts both main.py and sentinel_api.py)
COPY docker-startup.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-startup.sh

# Create required directories with proper permissions
# Create unprivileged user and set permissions
RUN adduser --system --home /app --shell /usr/sbin/nologin appuser && \
    mkdir -p /app/logs /app/data /app/data/secrets && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app/logs /app/data

# Health check - verify system is running
# Increased start-period to 60s for initial setup
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Expose ports
# - 8000: REST API (FastAPI)
# - 8501: Web Dashboard (Streamlit) - optional
EXPOSE 8000 8501

# Drop privileges
USER appuser

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Default command
CMD ["python", "main.py"]

# Volumes for persistence
VOLUME ["/app/logs", "/app/data"]

# ============================================================================
# BUILD NOTES:
# ============================================================================
# Image Size: ~1.5GB (Python + dependencies + required tools)
# Build Time: ~3-5 minutes (depending on internet speed)
# 
# To build:
#   docker build -t sentinel-agent:2.2 .
#
# To run:
#   docker run --privileged -it -p 8000:8000 sentinel-agent:2.2
#
# With docker-compose (recommended):
#   docker-compose up -d
# ==========================================================================