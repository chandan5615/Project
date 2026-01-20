"""
Sentinel Agent - AI Crew Definitions
Defines three specialized agents for security operations.
"""

from crewai import Agent, LLM
# Temporarily commented out - Ollama Local Model
# from langchain_community.llms import OllamaLLM
from tools.tools import (
    check_ip_threat, get_system_context, generate_firewall_rule, extract_ip_from_log,
    check_web_logs_for_ip, verify_firewall_rule, execute_iptables_rule,
    kill_process, change_permissions
)
import os

# Try to load from .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip loading .env file

# TEMPORARY: Using Gemini API instead of Ollama
# To restore Ollama, uncomment the OllamaLLM import above and use:
# llm = OllamaLLM(
#     model="llama3:8b",
#     base_url="http://localhost:11434",
#     temperature=0.7,
# )

# Initialize Gemini LLM via CrewAI native provider to avoid OpenAI fallback
# Make sure to set GOOGLE_API_KEY environment variable
# Option 1: Set environment variable directly
#   export GOOGLE_API_KEY="your-api-key-here" (Linux/macOS)
#   $env:GOOGLE_API_KEY="your-api-key-here" (Windows PowerShell)
#   set GOOGLE_API_KEY=your-api-key-here (Windows CMD)
# Option 2: Create a .env file with: GOOGLE_API_KEY=your-api-key-here
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    import sys
    error_msg = """
╔════════════════════════════════════════════════════════════════╗
║  ERROR: GOOGLE_API_KEY environment variable is not set        ║
╠════════════════════════════════════════════════════════════════╣
║  Please set your Google Gemini API key using one of these:    ║
║                                                                ║
║  Windows PowerShell:                                           ║
║    $env:GOOGLE_API_KEY="your-api-key-here"                    ║
║                                                                ║
║  Windows CMD:                                                  ║
║    set GOOGLE_API_KEY=your-api-key-here                        ║
║                                                                ║
║  Linux/macOS:                                                   ║
║    export GOOGLE_API_KEY="your-api-key-here"                   ║
║                                                                ║
║  OR create a .env file in the project root with:              ║
║    GOOGLE_API_KEY=your-api-key-here                            ║
║                                                                ║
║  Get your API key from: https://makersuite.google.com/app/apikey ║
╚════════════════════════════════════════════════════════════════╝
"""
    print(error_msg, file=sys.stderr)
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

llm = LLM(
    provider="google",
    model="gemini-1.5-flash",
    temperature=0.7,
    api_key=google_api_key,
)


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
