"""
Sentinel Agent - Security Playbooks (Tasks)
Defines the workflow tasks for the AI crew.
"""

from typing import List
from crewai import Task
from agents import triage_analyst, threat_intel_researcher, incident_responder, enforcer_agent
import json


def create_security_incident_tasks(ip_address: str, log_line: str, attack_type: str = "unknown", severity: str = "medium") -> List[Task]:
    """
    Create a sequence of tasks for handling a security incident.
    
    Args:
        ip_address: The suspicious IP address
        log_line: The log line that triggered the alert
        
    Returns:
        List of Task objects in execution order
    """
    
    # Task 1: Triage Analysis
    triage_task = Task(
        description=f"""
        Analyze the following security event:
        - Log Line: {log_line}
        - Source IP: {ip_address}
        - Detected Attack Type: {attack_type}
        - Initial Severity Assessment: {severity}
        
        Your tasks:
        1. Examine the log line for patterns indicating malicious activity
        2. Use get_system_context() to understand current system state
        3. Analyze the detected attack type: {attack_type}
        4. Determine the severity of this event (Low/Medium/High/Critical)
        5. Assess if this could be legitimate admin activity or clearly malicious
        6. Provide a structured JSON report with:
           - severity: string
           - attack_type: string (confirmed attack type)
           - analysis: string
           - indicators: array of suspicious patterns found
           - recommendation: string
        
        Format your response as valid JSON.
        """,
        agent=triage_analyst,
        expected_output="JSON string with severity assessment and analysis"
    )
    
    # Task 2: Threat Intelligence Research with Cross-Correlation
    threat_intel_task = Task(
        description=f"""
        Research the threat intelligence for IP address: {ip_address} and perform cross-correlation.
        
        Your tasks:
        1. Use check_ip_threat() to gather threat intelligence on this IP
        2. CRITICAL CROSS-CORRELATION: Use check_web_logs_for_ip() to check if this IP that is 
           brute-forcing SSH also appears in web access logs. This indicates a multi-vector attack.
        3. Analyze the results and determine if this IP is known malicious
        4. Check if this IP appears in any threat databases
        5. Assess the threat level based on intelligence gathered
        6. If the IP appears in both SSH and web logs, escalate the threat level
        7. Provide a structured JSON report with:
           - threat_level: string (low/medium/high/critical)
           - is_known_malicious: boolean
           - intelligence_summary: string
           - confidence: string (low/medium/high)
           - cross_correlation: object with:
             - appears_in_web_logs: boolean
             - web_log_occurrences: number
             - multi_vector_attack: boolean
        
        Format your response as valid JSON.
        """,
        agent=threat_intel_researcher,
        expected_output="JSON string with threat intelligence assessment and cross-correlation data",
        context=[triage_task]
    )
    
    # Task 3: Incident Response Planning
    response_task = Task(
        description=f"""
        Create an incident response plan for the security event involving IP: {ip_address}
        
        Based on the triage analysis and threat intelligence gathered:
        1. Review the severity and threat level assessments
        2. Consider the cross-correlation results - if this is a multi-vector attack, 
           the response should be more aggressive
        3. Use generate_firewall_rule() to create the appropriate blocking rule
        4. Determine if immediate action is required or if monitoring is sufficient
        5. Create a comprehensive remediation plan
        6. Provide a structured JSON report with:
           - action_required: boolean
           - firewall_rule: string (iptables command)
           - remediation_steps: array of strings
           - monitoring_recommendations: array of strings
           - risk_assessment: string
           - multi_vector_response: boolean (if cross-correlation detected multi-vector)
        
        Format your response as valid JSON.
        """,
        agent=incident_responder,
        expected_output="JSON string with incident response plan and firewall rule",
        context=[triage_task, threat_intel_task]
    )
    
    # Task 4: Autonomous Enforcement with Resilience Loop
    enforcement_task = Task(
        description=f"""
        Execute the security enforcement actions for IP: {ip_address} with resilience verification.
        
        Based on the incident response plan:
        1. If action_required is true, use execute_iptables_rule() to block the IP
        2. CRITICAL RESILIENCE LOOP: After executing the firewall rule, use verify_firewall_rule() 
           to check if the rule was successfully added to the firewall table
        3. If verification fails, the execute_iptables_rule tool will automatically retry with 
           alternative command variations (up to 3 attempts)
        4. Verify the rule exists after each attempt
        5. If the rule still doesn't exist after all attempts, try alternative methods:
           - Use ufw instead of iptables
           - Try different iptables command syntax
        6. Provide a structured JSON report with:
           - enforcement_executed: boolean
           - firewall_rule_verified: boolean
           - attempts_made: number
           - final_status: string (success/failed/partial)
           - verification_details: object
        
        Format your response as valid JSON.
        """,
        agent=enforcer_agent,
        expected_output="JSON string with enforcement execution results and verification status",
        context=[triage_task, threat_intel_task, response_task]
    )
    
    return [triage_task, threat_intel_task, response_task, enforcement_task]


def parse_agent_response(response: str) -> dict:
    """
    Parse agent response, attempting to extract JSON if present.
    
    Args:
        response: Agent response string
        
    Returns:
        Parsed dictionary, or original response if parsing fails
    """
    try:
        # Try to find JSON in the response
        json_match = None
        
        # Look for JSON block
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            return json.loads(json_str)
        
        # If no JSON found, return as-is
        return {"raw_response": response}
    except json.JSONDecodeError:
        return {"raw_response": response, "parse_error": "Could not parse JSON"}
