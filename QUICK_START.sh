#!/bin/bash
# ==============================================================================
# QUICK START GUIDE - Run This After Setup
# ==============================================================================
# CHANGE TRACKING (2026-02-23): Created quick-start guide for immediate use
#
# This guide helps you get Sentinel Agent running immediately after setup.
# ==============================================================================

cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 SENTINEL AGENT - QUICK START GUIDE                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

📋 STEP-BY-STEP INSTRUCTIONS FOR YOUR UBUNTU SYSTEM:

┌──────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: RUN THE SETUP SCRIPT (First Time Only)                              │
└──────────────────────────────────────────────────────────────────────────────┘

  cd ~/Project
  chmod +x setup_local_env.sh
  ./setup_local_env.sh

  ✓ This creates a virtual environment and installs all dependencies
  ✓ No more "externally-managed-environment" errors!


┌──────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: ACTIVATE THE VIRTUAL ENVIRONMENT (Every Time)                       │
└──────────────────────────────────────────────────────────────────────────────┘

  source venv/bin/activate

  Your prompt should change to show: (venv)


┌──────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: MAKE SURE OLLAMA IS RUNNING                                         │
└──────────────────────────────────────────────────────────────────────────────┘

  # Check if Ollama is running:
  curl http://localhost:11434/api/tags

  # If not running, start it:
  ollama serve

  # In another terminal, verify your model:
  ollama list
  # Should show: llama3:8b


┌──────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: RUN SENTINEL AGENT                                                  │
└──────────────────────────────────────────────────────────────────────────────┘

  # Option A: Main agent (monitors logs and analyzes attacks)
  python3 main.py

  # Option B: CLI Dashboard (view stored incidents)
  python3 dashboard/cli_dashboard.py

  # Option C: Web Dashboard (requires browser)
  streamlit run dashboard/web_dashboard.py


┌──────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: GENERATE TEST ATTACKS (Optional)                                    │
└──────────────────────────────────────────────────────────────────────────────┘

  # In another terminal (with venv activated):
  python3 test_attacks.py


┌──────────────────────────────────────────────────────────────────────────────┐
│ TROUBLESHOOTING COMMON ISSUES                                               │
└──────────────────────────────────────────────────────────────────────────────┘

❌ ERROR: "Permission denied: '/app'"
   ✅ FIX: Already fixed! Code now uses ./data instead of /app/data

❌ ERROR: "externally-managed-environment"
   ✅ FIX: Use the virtual environment (step 2)

❌ ERROR: AI analysis hangs forever
   ✅ FIX: Already fixed! Now times out after 5 minutes
   💡 TIP: Increase timeout if needed: export CREW_TIMEOUT=600

❌ ERROR: "streamlit: command not found"
   ✅ FIX: Make sure venv is activated, then:
          pip install streamlit pandas plotly rich

❌ ERROR: "Cannot connect to Ollama"
   ✅ FIX: Start Ollama in another terminal:
          ollama serve


┌──────────────────────────────────────────────────────────────────────────────┐
│ USEFUL COMMANDS                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

  # View database entries:
  sqlite3 data/sentinel_intel.db "SELECT * FROM incidents LIMIT 10;"

  # Check Ollama models:
  ollama list

  # View Sentinel logs:
  tail -f logs/sentinel.log

  # Deactivate virtual environment when done:
  deactivate


┌──────────────────────────────────────────────────────────────────────────────┐
│ ENVIRONMENT VARIABLES (Optional Customization)                              │
└──────────────────────────────────────────────────────────────────────────────┘

  Create a .env file (already created by setup script):

  SENTINEL_DATA_DIR=./data
  SENTINEL_LOG_DIR=./logs
  OLLAMA_BASE_URL=http://127.0.0.1:11434
  OLLAMA_MODEL=llama3:8b
  OLLAMA_TIMEOUT=300
  CREW_TIMEOUT=300
  AUTH_LOG=/var/log/auth.log
  WEB_LOG=/var/log/apache2/access.log


┌──────────────────────────────────────────────────────────────────────────────┐
│ WHAT WAS FIXED TODAY (2026-02-23)                                           │
└──────────────────────────────────────────────────────────────────────────────┘

  ✅ Fixed database path errors (no more /app permission denied)
  ✅ Fixed Ollama timeout hangs (5-minute timeout with fallback)
  ✅ Created virtual environment setup scripts
  ✅ Auto-detect Docker vs local environment
  ✅ Added change tracking comments in all files

  📄 See CHANGES_2026-02-23.md for detailed change log


┌──────────────────────────────────────────────────────────────────────────────┐
│ RUNNING IN DOCKER (Alternative)                                             │
└──────────────────────────────────────────────────────────────────────────────┘

  If you prefer Docker instead of local Python:

  # Start containers:
  docker-compose up -d

  # View logs:
  docker-compose logs -f sentinel-agent

  # Access CLI dashboard in container:
  docker exec -it sentinel-agent python3 dashboard/cli_dashboard.py

  # Stop containers:
  docker-compose down


╔══════════════════════════════════════════════════════════════════════════════╗
║                              🎉 YOU'RE ALL SET!                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Need help? Check:
- CHANGES_2026-02-23.md (detailed change log)
- README.md (project documentation)
- Inline comments in code (search for "CHANGE TRACKING")

EOF

echo ""
echo "Do you want to run the setup now? [y/N]"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "Starting setup..."
    exec ./setup_local_env.sh
else
    echo "Run './setup_local_env.sh' when ready!"
fi
