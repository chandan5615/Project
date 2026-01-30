"""
Sentinel Agent - AI Crew Definitions
Defines three specialized agents for security operations.
Uses Ollama for local LLM inference.
"""
import os
import socket
import sys
import logging
from crewai import Agent, LLM
from tools.tools import (
    check_ip_threat, get_system_context, generate_firewall_rule, extract_ip_from_log,
    check_web_logs_for_ip, verify_firewall_rule, execute_iptables_rule,
    kill_process, change_permissions
)

# Module logger
logger = logging.getLogger(__name__) 

# Try to load from .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_ollama_url() -> str:
    """
    Get the Ollama server URL.
    Checks environment variable first, then defaults to localhost.
    
    For Docker containers, set OLLAMA_BASE_URL appropriately:
    - Linux with network_mode: host -> http://127.0.0.1:11434
    - Docker bridge network -> http://host.docker.internal:11434
    - Remote server -> http://<server-ip>:11434
    """
    env_url = os.getenv("OLLAMA_BASE_URL")
    if env_url:
        return env_url
    
    # Default to localhost - works for Linux native and network_mode: host
    return "http://127.0.0.1:11434"


def check_ollama_connection():
    """
    Check if Ollama server is reachable and print helpful error message if not.
    """
    import urllib.request
    import urllib.error
    
    url = get_ollama_url()
    try:
        # Try to connect to Ollama's API endpoint
        req = urllib.request.Request(f"{url}/api/tags", method='GET')
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                logger.info(f"✅ Ollama server is reachable at {url}")
                return True
    except urllib.error.URLError as e:
        logger.warning(f"⚠️  Warning: Cannot reach Ollama server at {url}")
        logger.warning(f"   Error: {e.reason}")
        logger.warning("   Make sure Ollama is running: ollama serve")
        logger.warning("   Or set OLLAMA_BASE_URL environment variable")
    except Exception as e:
        logger.warning(f"⚠️  Warning: Error checking Ollama connection: {e}")
    
    return False


# Check Ollama connection at startup (skipable via SENTINEL_SKIP_OLLAMA_CHECK=1)
if os.getenv('SENTINEL_SKIP_OLLAMA_CHECK', '0') != '1':
    check_ollama_connection()

# Get Ollama model from environment or use default
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b")

# Initialize LLM with Ollama
llm = LLM(
    model=f"ollama/{OLLAMA_MODEL}",
    base_url=get_ollama_url(),
    temperature=0.7
)

# Keep these as placeholders so CrewAI doesn't look for OpenAI keys
os.environ["OPENAI_API_KEY"] = "NA"

# --- Agent Definitions ---
# (Your triage_analyst, threat_intel_researcher, etc. remain the same)

# Triage Analyst Agent
triage_analyst = Agent(
    role="Senior SOC Analyst",
    goal="Analyze Linux logs and network metadata to distinguish between legitimate admin activity and malicious intrusion attempts",
    backstory="""You are an expert at analyzing Linux logs and network metadata. 
    You have years of experience in Security Operations Centers and can quickly identify 
    patterns that indicate malicious activity versus normal administrative operations. 
    You excel at triaging security events and determining their severity and legitimacy.""",
    verbose=True,
    allow_delegation=False,
    llm=llm,
    tools=[get_system_context, extract_ip_from_log],
)


# Threat Intelligence Researcher Agent
threat_intel_researcher = Agent(
    role="Cyber Intelligence Expert",
    goal="Use external APIs and OSINT tools to verify if IP addresses, hashes, or patterns belong to known botnets or hackers. Perform cross-correlation by checking if IPs appearing in SSH brute-force attempts also appear in web access logs.",
    backstory="""You are a specialized cyber intelligence expert with deep knowledge of threat 
    intelligence feeds, OSINT tools, and malicious actor patterns. You use various APIs and 
    databases to check the reputation of IP addresses, analyze malware hashes, and identify 
    known attack patterns. You excel at cross-correlating data from multiple sources - if an IP 
    is brute-forcing SSH, you proactively check if that same IP is also attacking web services. 
    Your research helps determine if an incident is part of a larger threat campaign or an 
    isolated event.""",
    verbose=True,
    allow_delegation=False,
    llm=llm,
    tools=[check_ip_threat, check_web_logs_for_ip],
)


# Incident Responder Agent
incident_responder = Agent(
    role="System Defense Engineer",
    goal="Generate precise technical remediation plans specializing in Linux iptables, ufw, and process management",
    backstory="""You are a system defense engineer with extensive experience in Linux security 
    hardening and incident response. You specialize in creating precise firewall rules using 
    iptables and ufw, managing processes, and implementing security controls. You understand 
    the technical nuances of Linux systems and can generate actionable remediation steps that 
    balance security with system functionality.""",
    verbose=True,
    allow_delegation=False,
    llm=llm,
    tools=[generate_firewall_rule, get_system_context],
)


# Enforcer Agent - Autonomous tool-belt agent
enforcer_agent = Agent(
    role="Security Enforcer",
    goal="Autonomously execute security remediation actions including firewall rules, process termination, and permission changes. Use resilience loops to verify actions were successful.",
    backstory="""You are a security enforcer with autonomous authority to execute defensive actions. 
    You have a comprehensive tool-belt including iptables for firewall management, systemctl/kill 
    for process management, and chmod for permission changes. You always verify your actions were 
    successful - after blocking an IP, you check the firewall table to confirm the rule exists. 
    If verification fails, you automatically retry with alternative methods. You are methodical, 
    persistent, and ensure every defensive action is properly implemented.""",
    verbose=True,
    allow_delegation=False,
    llm=llm,
    tools=[execute_iptables_rule, verify_firewall_rule, kill_process, change_permissions, get_system_context],
)
