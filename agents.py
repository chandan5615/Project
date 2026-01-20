"""
Sentinel Agent - AI Crew Definitions
Defines three specialized agents for security operations.
"""
import os
import socket
import sys
from crewai import Agent, LLM

# Try to load from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_automated_ollama_url():
    """
    Automatically resolves the best URL for Ollama.
    Works for network_mode: host (Linux) and standard bridge (WSL2/Mac/Windows).
    """
    # 1. Priority: Check if the user manually set an override in .env
    env_url = os.getenv("OLLAMA_BASE_URL")
    if env_url:
        return env_url
    
    # 2. Check if we can reach Ollama on the loopback (Best for network_mode: host)
    # Using 127.0.0.1 instead of 'localhost' prevents "Name not known" errors.
    return "http://127.0.0.1:11434"

# Initialize LLM with automatic URL detection
llm = LLM(
    model="ollama/llama3:8b", 
    base_url=get_automated_ollama_url(),
    temperature=0.7
)

# Safety check for Google API Key (if you still use it for other tasks)
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    print("Warning: GOOGLE_API_KEY not set. Ensure Ollama is running.", file=sys.stderr)

# Keep these as placeholders so CrewAI doesn't look for OpenAI keys
os.environ["OPENAI_API_KEY"] = "NA"

# --- Agent Definitions ---

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
