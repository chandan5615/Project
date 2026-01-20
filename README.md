# Sentinel Agent

An autonomous, multi-agent AI Security Operations Center (SOC) analyst designed for Linux systems. Sentinel Agent uses CrewAI for orchestration and Ollama (Llama 3) as the local LLM engine to monitor, analyze, and respond to security threats in real-time.

## Features

- **Real-time Log Monitoring**: Watches `/var/log/auth.log` for failed login attempts
- **Multi-Agent AI Analysis**: Three specialized AI agents work together:
  - **Triage Analyst**: Analyzes logs and determines event severity
  - **Threat Intelligence Researcher**: Checks IP reputation and threat intelligence
  - **Incident Responder**: Generates remediation plans and firewall rules
- **Human-in-the-Loop Security**: Requires explicit approval before executing any blocking actions
- **Structured JSON Reporting**: All agent communications use structured JSON format
- **Modular Architecture**: Clean separation of sensors, agents, tasks, and tools

## Architecture

```
Sentinel Agent
├── sensors/          # Input modules (log watchers, network sniffers)
│   └── auth_sensor.py
├── tools/            # Python functions for OSINT and firewall actions
│   └── tools.py
├── agents.py         # AI Crew definitions
├── tasks.py          # Security playbooks
└── main.py           # Entry point and event loop
```

## Prerequisites

- Python 3.10 or higher
- Linux system (for `/var/log/auth.log` and `iptables`)
- **TEMPORARY**: Google Gemini API key (currently using Gemini instead of Ollama)
- Root/sudo privileges (for reading log files and executing firewall rules)

### Setting up Google Gemini API (Temporary)

1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set the environment variable:
   ```bash
   # Linux/macOS
   export GOOGLE_API_KEY="your-api-key-here"
   
   # Windows PowerShell
   $env:GOOGLE_API_KEY="your-api-key-here"
   
   # Windows CMD
   set GOOGLE_API_KEY=your-api-key-here
   ```
3. Verify the API key is set:
   ```bash
   echo $GOOGLE_API_KEY  # Linux/macOS
   echo $env:GOOGLE_API_KEY  # Windows PowerShell
   ```

### Installing Ollama (Currently Commented Out)

**Note:** The code currently uses Gemini API. To switch back to Ollama:
1. Uncomment Ollama imports in `agents.py`
2. Comment out Gemini imports
3. Install Ollama from [https://ollama.ai](https://ollama.ai)
4. Pull the Llama 3 model:
   ```bash
   ollama pull llama3:8b
   ```
5. Verify Ollama is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```

## Installation

### Docker Deployment (Recommended)

For easy deployment on Linux servers, use Docker:

```bash
# Quick start with Docker
docker compose up -d

# See DOCKER_QUICKSTART.md for 5-minute setup
# See DOCKER_DEPLOYMENT.md for detailed Docker guide
```

### Manual Installation

### Quick Setup (Recommended)

**Linux/macOS:**
```bash
chmod +x setup.sh
./setup.sh
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.\setup.ps1
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
setup.bat
venv\Scripts\activate.bat
```

### Manual Setup

1. Clone or download this repository

2. Create and activate a virtual environment:
   ```bash
   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   
   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Ensure you have the required system permissions:
   - Read access to `/var/log/auth.log` (may require sudo)
   - Execute permissions for `iptables` (requires sudo)

**Important:** Always activate the virtual environment before running Sentinel Agent to ensure all dependencies are available in one isolated environment.

## Usage

### Basic Usage

**Important:** Make sure your virtual environment is activated first!

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Run Sentinel Agent with default settings
sudo python main.py
```

**Note**: `sudo` is required to:
- Read `/var/log/auth.log`
- Execute `iptables` commands (if approved)

### Custom Log Path

Monitor a different log file:

```bash
sudo python main.py --log-path /path/to/your/auth.log
```

### Testing Mode

For testing on systems without `/var/log/auth.log`, the sensor will create the directory structure automatically. You can manually add test log entries:

```bash
# In another terminal, simulate a failed login
echo "Jan 1 12:00:00 hostname sshd[1234]: Failed password for user from 192.168.1.100 port 22" >> /var/log/auth.log
```

## How It Works

1. **Sensor Layer**: The `auth_sensor.py` module uses the `watchdog` library to monitor `/var/log/auth.log` for new entries containing "Failed password"

2. **Event Detection**: When a failed login is detected, the sensor extracts the source IP address using regex patterns

3. **AI Crew Orchestration**: The main event loop creates a CrewAI crew with three specialized agents:
   - **Triage Analyst** analyzes the log entry and system context
   - **Threat Intelligence Researcher** checks the IP's reputation
   - **Incident Responder** generates a remediation plan

4. **Human Approval**: Before any firewall rule is executed, the system:
   - Displays the proposed action
   - Requests user confirmation
   - Requires a second confirmation with "EXECUTE"

5. **Action Execution**: If approved, the firewall rule is executed using `iptables`

## Security Guardrails

- **Human-in-the-Loop**: All `os.system()` and `subprocess` calls for blocking IPs require explicit user approval
- **Double Confirmation**: Two separate prompts before executing firewall rules
- **JSON Enforcement**: Agents are instructed to communicate using structured JSON
- **Error Handling**: Comprehensive error handling for permissions, missing commands, and timeouts

## Configuration

### LLM Configuration

Edit `agents.py` to change the Ollama model or connection:

```python
llm = OllamaLLM(
    model="llama3:8b",  # Change model here
    base_url="http://localhost:11434",  # Change Ollama URL
    temperature=0.7,
)
```

### Threat Intelligence

The `check_ip_threat()` function in `tools/tools.py` currently uses a simulated API. To integrate with real threat intelligence APIs:

1. Sign up for an API key (e.g., AbuseIPDB)
2. Modify `check_ip_threat()` to use the actual API
3. Store API keys securely (environment variables recommended)

## Project Structure

```
.
├── main.py              # Entry point, event loop, and orchestration
├── agents.py            # CrewAI agent definitions
├── tasks.py             # Security playbook tasks
├── sensors/
│   ├── __init__.py
│   └── auth_sensor.py   # Authentication log monitor
├── tools/
│   ├── __init__.py
│   └── tools.py         # Security tools (IP check, firewall, system context)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Troubleshooting

### "Permission denied" errors
- Ensure you're running with `sudo` for log file access and firewall commands

### "iptables command not found"
- Install iptables: `sudo apt-get install iptables` (Debian/Ubuntu) or equivalent

### Ollama connection errors
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
- Check the model is available: `ollama list`
- Ensure the base_url in `agents.py` matches your Ollama instance

### Log file not found
- On some systems, auth logs may be in `/var/log/secure` (RHEL/CentOS)
- Use `--log-path` to specify the correct location

## Development

### Adding New Sensors

Create new sensor modules in `sensors/` following the pattern in `auth_sensor.py`:

1. Inherit from `FileSystemEventHandler` or implement a custom monitoring class
2. Define a callback function signature
3. Integrate with the main event loop in `main.py`

### Adding New Tools

Add new CrewAI tools in `tools/tools.py`:

1. Use the `@tool` decorator from `crewai_tools`
2. Define clear input/output types
3. Add the tool to relevant agents in `agents.py`

### Customizing Agents

Modify agent definitions in `agents.py`:
- Adjust `role`, `goal`, and `backstory` for different specializations
- Add or remove tools from the `tools` list
- Change `verbose` and `allow_delegation` settings

## License

This project is provided as-is for educational and security research purposes.

## Disclaimer

This tool is designed for authorized security monitoring only. Ensure you have proper authorization before monitoring systems or blocking IP addresses. The authors are not responsible for misuse of this software.
