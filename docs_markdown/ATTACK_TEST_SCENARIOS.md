# Apache Attack Test Scenarios for Sentinel Agent

Use the following HTTP requests and command-line examples to test Sentinel Agent's detection of web attacks via the Apache access log. These simulate common web attacks and should trigger alerts if the system is working correctly.

---

## 1. SQL Injection

```
curl "http://localhost/index.php?id=1 UNION SELECT username, password FROM users"
curl "http://localhost/login.php?user=admin' OR 1=1--&pass=foo"
```

## 2. Command Injection

```
curl "http://localhost/index.php?cmd=ls;cat /etc/passwd"
curl "http://localhost/index.php?cmd=`whoami`"
```

## 3. Cross-Site Scripting (XSS)

```
curl "http://localhost/search.php?q=<script>alert('xss')</script>"
curl "http://localhost/profile.php?bio=<img src=x onerror=alert(1)>"
```

## 4. Directory Traversal

```
curl "http://localhost/index.php?file=../../../../etc/passwd"
curl "http://localhost/index.php?file=%2e%2e%2f%2e%2e%2fetc%2fpasswd"
```

## 5. SSRF (Server-Side Request Forgery)

```
curl "http://localhost/fetch.php?url=http://127.0.0.1:80/"
curl "http://localhost/fetch.php?url=file:///etc/passwd"
```

## 6. DoS/Brute Force (simulate with repeated requests)

```
for i in {1..20}; do curl "http://localhost/login.php?user=admin&pass=wrong"; done
```

---

## How to Use

1. Run Sentinel Agent and ensure it is monitoring `/var/log/apache2/access.log`.
2. Run the above `curl` commands from a terminal on the same machine or from another host targeting your Apache server.
3. Check Sentinel Agent logs and dashboard for detected attacks.

**Note:**
- Make sure Apache logging is enabled and logs are being written to `/var/log/apache2/access.log`.
- If you see no output, verify file permissions and log format compatibility.

---

## Troubleshooting

- If attacks are not detected:
  - Ensure `/var/log/apache2/access.log` is being updated (try `tail -f /var/log/apache2/access.log` while running attacks).
  - Check Sentinel Agent has read permissions for the log file.
  - Confirm the log format matches the expected patterns (see `web_sensor.py`).
  - Review the `defense/attack_detector.py` patterns for coverage.

---

**Generated: February 6, 2026**
