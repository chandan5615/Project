# Ollama Setup Guide

This project uses **Ollama** for local LLM inference. Follow these steps to set up:

## Step 1: Install Ollama

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### macOS
```bash
brew install ollama
```

### Windows
Download from [https://ollama.ai/download](https://ollama.ai/download)

## Step 2: Pull the LLM Model

The default model is `llama3:8b`. Pull it with:

```bash
ollama pull llama3:8b
```

### Alternative Models
You can use other models by setting the `OLLAMA_MODEL` environment variable:

```bash
# Smaller model (faster, less accurate)
ollama pull llama3.2:3b
export OLLAMA_MODEL="llama3.2:3b"

# Larger model (slower, more accurate)
ollama pull llama3:70b
export OLLAMA_MODEL="llama3:70b"

# Code-focused model
ollama pull codellama:7b
export OLLAMA_MODEL="codellama:7b"
```

## Step 3: Start Ollama Server

```bash
ollama serve
```

The server runs on `http://127.0.0.1:11434` by default.

## Step 4: Verify Setup

```bash
# Check if Ollama is running
curl http://127.0.0.1:11434/api/tags

# Test a simple prompt
ollama run llama3:8b "Hello, respond with 'Ollama is working!'"
```

## Step 5: Configure Environment (Optional)

Create a `.env` file in the project root for custom settings:

```env
# Custom Ollama server URL (default: http://127.0.0.1:11434)
OLLAMA_BASE_URL=http://127.0.0.1:11434

# Custom model (default: llama3:8b)
OLLAMA_MODEL=llama3:8b
```

## Step 6: Run Sentinel Agent

```bash
# Activate virtual environment first
source venv/bin/activate     # Linux/macOS
# or
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Run the agent
python main.py
```

## Docker Configuration

When running in Docker, configure the Ollama URL based on your setup:

### Linux with `network_mode: host`
```env
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

### Docker bridge network (default)
```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

### Remote Ollama server
```env
OLLAMA_BASE_URL=http://<server-ip>:11434
```

## Troubleshooting

### "Cannot reach Ollama server"
1. Make sure Ollama is running: `ollama serve`
2. Check if the port is accessible: `curl http://127.0.0.1:11434/api/tags`
3. Verify the `OLLAMA_BASE_URL` environment variable is correct

### "Model not found"
1. Pull the model first: `ollama pull llama3:8b`
2. List available models: `ollama list`
3. Check you're using the correct model name

### Slow responses
- Use a smaller model like `llama3.2:3b`
- Ensure you have enough RAM (8GB+ recommended)
- Consider using GPU acceleration if available

### Connection refused in Docker
- Use `host.docker.internal` instead of `localhost`
- Or use `network_mode: host` in docker-compose.yml (Linux only)

## GPU Acceleration

Ollama automatically uses NVIDIA GPUs if available. Verify with:

```bash
ollama run llama3:8b --verbose
# Look for "GPU" in the output
```

For AMD GPUs or troubleshooting, see [Ollama GPU documentation](https://github.com/ollama/ollama/blob/main/docs/gpu.md).
