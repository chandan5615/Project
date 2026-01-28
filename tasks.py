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
        Analyze the following security event and provide a severity assessment.
        DO NOT use any tools in this task.
        
        Information provided:
        - Log Line: {log_line}
        - Source IP: {ip_address}
        - Detected Attack Type: {attack_type}
        - Initial Severity Assessment: {severity}
        
        Your analysis tasks:
        1. Examine the log line for patterns indicating malicious activity
        2. Analyze the detected attack type: {attack_type}
        3. Confirm or adjust the severity assessment (Low/Medium/High/Critical)
        4. Identify suspicious indicators in the log line
        5. Assess if this could be legitimate admin activity or clearly malicious
        
        Respond with ONLY a JSON report:
        {{
          "severity": "Low/Medium/High/Critical",
          "attack_type": "{attack_type}",
          "analysis": "detailed analysis",
          "indicators": ["pattern1", "pattern2"],
          "recommendation": "action to take"
        }}
        """,
        agent=triage_analyst,
        expected_output="JSON string with severity assessment and analysis"
    )
    
    # Task 2: Threat Intelligence Research with Cross-Correlation
    threat_intel_task = Task(
        description=f"""
        Research threat intelligence for IP: {ip_address}
        
        Use tools correctly - pass ONLY required parameters as simple values:
        - check_ip_threat: Pass just the IP string "{ip_address}"
        - check_web_logs_for_ip: Pass IP "{ip_address}" and log_path "/var/log/apache2/access.log"
        
        CRITICAL: Call each tool EXACTLY ONCE. Do not repeat tool calls.
        
        Your tasks:
        1. Call check_ip_threat tool with IP "{ip_address}"
        2. Call check_web_logs_for_ip tool with IP "{ip_address}"
        3. Analyze results to determine threat level
        4. Assess if IP is known malicious
        5. Check for multi-vector attack (IP in both auth and web logs)
        
        Respond with ONLY JSON:
        {{
          "threat_level": "low/medium/high/critical",
          "is_known_malicious": false,
          "intelligence_summary": "string",
          "confidence": "low/medium/high",
          "cross_correlation": {{
            "appears_in_web_logs": false,
            "web_log_occurrences": 0,
            "multi_vector_attack": false
          }}
        }}
        """,
        agent=threat_intel_researcher,
        expected_output="JSON string with threat intelligence assessment",
        context=[triage_task]
    )
    
    # Task 3: Incident Response Planning
    response_task = Task(
        description=f"""
        Create an incident response plan for IP: {ip_address}
        
        Use tools correctly:
        - generate_firewall_rule: Pass just the IP string "{ip_address}"
        - Call it ONLY ONCE
        
        Your tasks:
        1. Call generate_firewall_rule tool with IP "{ip_address}"
        2. Review severity and threat level from previous tasks
        3. Determine if immediate action is required
        4. Create remediation and monitoring plans
        
        Respond with ONLY JSON:
        {{
          "action_required": true,
          "firewall_rule": "iptables command string",
          "remediation_steps": ["block ip", "monitor logs"],
          "monitoring_recommendations": ["watch for similar attacks"],
          "risk_assessment": "High risk due to directory traversal",
          "multi_vector_response": false
        }}
        """,
        agent=incident_responder,
        expected_output="JSON string with incident response plan",
        context=[triage_task, threat_intel_task]
    )
    
    # Task 4: Autonomous Enforcement with Resilience Loop
    enforcement_task = Task(
        description=f"""
        Execute security enforcement actions for IP: {ip_address}
        
        Use tools correctly:
        - execute_iptables_rule: Pass the exact iptables command string
        - verify_firewall_rule: Pass just the IP string "{ip_address}"
        - Call each ONLY ONCE
        
        Your tasks:
        1. If action_required is true, call execute_iptables_rule with the firewall command
        2. Call verify_firewall_rule with IP "{ip_address}" to verify it was applied
        3. Report success or failure
        
        Respond with ONLY JSON:
        {{
          "enforcement_executed": true,
          "firewall_rule_verified": true,
          "attempts_made": 1,
          "final_status": "success",
          "verification_details": {{
            "rule_active": true,
            "ip_blocked": true
          }}
        }}
        """,
        agent=enforcer_agent,
        expected_output="JSON string with enforcement results",
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
