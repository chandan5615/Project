# Sentinel Agent - Dockerfile
FROM python:3.10-slim as builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make libc6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.10-slim

# --- FIX: ALL SYSTEM TOOLS INSTALLED HERE AS ROOT ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    iptables \
    net-tools \
    curl \
    util-linux \
    procps \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY . .

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

RUN mkdir -p /app/logs /app/data && \
    chmod 755 /app/logs /app/data

RUN useradd -m -u 1000 sentinel && \
    chown -R sentinel:sentinel /app

# Switch to non-root user (Note: iptables will still need --privileged)
USER sentinel

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
VOLUME ["/app/logs", "/app/data"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import os; exit(0 if os.path.exists('/app/data/attack_records.json') else 1)" || exit 1

CMD ["python", "main.py"]