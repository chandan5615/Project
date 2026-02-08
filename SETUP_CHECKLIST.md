# Sentinel Agent v2.2 - Setup Checklist

Use this checklist to ensure your fresh clone setup is working properly.

---

## Pre-Setup Checklist (Before You Start)

- [ ] **System Requirements Met**
  - [ ] Docker installed (`docker --version`)
  - [ ] Docker Compose installed (`docker-compose --version`)
  - [ ] Python 3.7+ installed (`python3 --version`)
  - [ ] Ports 8000, 8501, 11434 available

- [ ] **Repository Cloned**
  - [ ] Cloned from GitHub (`git clone ...`)
  - [ ] In correct directory (`cd Project`)
  - [ ] All files present (`ls docker-compose.yml` shows file)

---

## Phase 1: Reset Old Database (CRITICAL!)

- [ ] **Stop Running Container**
  - [ ] Run: `docker-compose down`
  - [ ] Verify: No containers running (`docker ps`)

- [ ] **Remove Old Database Files**
  - [ ] Run: `rm -f data/auth.db`
  - [ ] Run: `rm -f data/INITIAL_CREDENTIALS.txt`
  - [ ] Run: `rm -f data/attack_records.json data/sentinel_intel.db data/metrics.db`
  - [ ] Verify: `ls data/` shows empty directory

> **Why?** The cloned repo includes old database files. Removing them forces fresh credential generation with new password logging.

---

## Phase 2: Start Ollama on Host

- [ ] **Open New Terminal**
  - [ ] New terminal/tab ready
  - [ ] Still in Project directory or home directory

- [ ] **Start Ollama Service**
  - [ ] Run: `ollama serve`
  - [ ] Wait: See "Listening on 127.0.0.1:11434" in output
  - [ ] Verify: In another terminal, `curl http://localhost:11434/api/tags` returns model list
  - [ ] ✅ **LEAVE THIS TERMINAL OPEN**

> **⚠️ Critical:** Ollama must keep running. Don't close this terminal!

---

## Phase 3: Build Docker Image

- [ ] **In Original Terminal (Project Directory)**
  - [ ] Back in original terminal with Project
  - [ ] Verify: pwd shows `/home/ubuntu/Project` or similar

- [ ] **Build Docker Image**
  - [ ] Run: `docker-compose build --no-cache`
  - [ ] Wait: Until you see "FINISHED" and "naming to docker.io/library/sentinel-agent:2.2"
  - [ ] Verify: `docker images | grep sentinel-agent` shows image

---

## Phase 4: Start Container

- [ ] **Start Services**
  - [ ] Run: `docker-compose up -d`
  - [ ] Verify: Returns "Creating sentinel-agent ... done"

- [ ] **Wait for Startup**
  - [ ] Run: `sleep 5`
  - [ ] Run: `docker-compose ps`
  - [ ] Verify: Shows "Up (healthy)" - if "unhealthy", wait and retry

- [ ] **Check Status Multiple Times**
  - [ ] Run: `docker-compose ps` (1st check)
  - [ ] If unhealthy: Wait 10 seconds
  - [ ] Run: `docker-compose ps` (2nd check)
  - [ ] Continue until "healthy" appears

---

## Phase 5: Extract Credentials

- [ ] **Get Password from Logs**
  - [ ] Run: `docker-compose logs sentinel-agent | grep -A 2 "DEFAULT ADMIN CREDENTIALS"`
  - [ ] Write down the password (long random string)
  - [ ] **SAVE THIS PASSWORD SOMEWHERE SAFE**

- [ ] **Or Check Credentials File**
  - [ ] Run: `cat data/INITIAL_CREDENTIALS.txt`
  - [ ] Should show username: `admin` and random password
  - [ ] If not found, go back to Phase 1 (database reset)

---

## Phase 6: Verify API

- [ ] **Health Check**
  - [ ] Run: `curl http://localhost:8000/api/health`
  - [ ] Should return: `{"status":"healthy","version":"2.2",...}`

- [ ] **Manual Login Test (Optional)**
  - [ ] Run: 
    ```bash
    curl -X POST http://localhost:8000/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username":"admin","password":"YOUR_PASSWORD_HERE"}'
    ```
  - [ ] Replace `YOUR_PASSWORD_HERE` with the password you got
  - [ ] Should return: `{"token":"eyJ...","expires_in":86400}`

---

## Phase 7: Install Automation Dependencies

- [ ] **Install Python Requests Library**
  - [ ] Run: `pip3 install requests`
  - [ ] Verify: `python3 -c "import requests; print(requests.__version__)"`

- [ ] **Verify Scripts Exist**
  - [ ] Run: `ls -la sentinel_auto.py sentinel_setup.sh`
  - [ ] Both files should be present

---

## Phase 8: Run Automated Setup

- [ ] **Extract Password & Get Token**
  - [ ] Run: `python3 sentinel_auto.py setup`
  - [ ] Should complete with: "✓ Baseline captured"
  - [ ] Files created: `.sentinel_password` and `.sentinel_token`
  - [ ] Verify: `ls -la .sentinel_*`

---

## Phase 9: Run Full Demo

- [ ] **Run All Attack Tests**
  - [ ] Run: `python3 sentinel_auto.py demo`
  - [ ] This takes 5-7 minutes
  - [ ] Watch for: "Testing SSH...", "Testing SQL...", "Testing DDoS..."
  - [ ] Should end with: "✓ Full demo completed"

- [ ] **Files Created**
  - [ ] `test_results/` directory should exist
  - [ ] Multiple JSON files: `baseline_metrics.json`, `incidents.json`, `current_metrics.json`
  - [ ] Verify: `ls -la test_results/`

---

## Phase 10: Check Results

- [ ] **View Status Dashboard**
  - [ ] Run: `python3 sentinel_auto.py status`
  - [ ] Should show: Baseline events, new incidents, threats detected

- [ ] **View JSON Results**
  - [ ] Run: `cat test_results/incidents.json | python3 -m json.tool | head -30`
  - [ ] Should show detected attacks with timestamps

- [ ] **View Container Logs (Optional)**
  - [ ] Run: `docker-compose logs sentinel-agent | tail -50`
  - [ ] Should show detection events from the tests

---

## ✅ Success Checklist

If all sections above are checked, your setup is complete:

- [ ] Database was fresh (reset)
- [ ] Ollama is running and connected
- [ ] Docker container is healthy
- [ ] API is responding with health status
- [ ] Credentials were extracted successfully
- [ ] `sentinel_auto.py setup` completed
- [ ] `sentinel_auto.py demo` completed all tests
- [ ] `sentinel_auto.py status` shows results
- [ ] Test result JSON files exist

---

## 🚀 What's Next?

At this point, you can:

1. **Read the User Guide** - Understand all available features
   ```bash
   cat docs_markdown/USER_GUIDE.md | less
   ```

2. **View API Documentation**
   - Swagger UI: http://localhost:8000/docs

3. **Change Admin Password**
   - Use the API or dashboard to change password immediately

4. **Set Up Rate Limiting**
   - Whitelist your IPs in the IP management section

5. **Configure Monitoring**
   - Set up continuous monitoring for your environment

---

## 🐛 Troubleshooting

If any step fails:

1. **Find the issue:** Look at the last successful checkbox
2. **Check logs:** `docker-compose logs sentinel-agent`
3. **See TROUBLESHOOTING.md** for detailed solutions
4. **Run verification script:** `bash verify_setup.sh`

---

## 📚 Documentation Links

- [FRESH_START_GUIDE.md](FRESH_START_GUIDE.md) - Complete setup guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues & fixes
- [USER_GUIDE.md](docs_markdown/USER_GUIDE.md) - Features & API
- [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) - Automation tools
- [QUICK_START_AUTOMATION.md](QUICK_START_AUTOMATION.md) - Quick reference

---

**Good luck! You've got this! 🎉**
