#!/bin/bash
# CLI Dashboard Launcher for Linux/Mac
# Ensures database initialization before starting dashboard

echo "============================================================"
echo "Sentinel Agent - CLI Dashboard Launcher"
echo "============================================================"
echo ""

# Step 1: Initialize databases
echo "[1/2] Initializing databases..."
python3 init_database.py
if [ $? -ne 0 ]; then
    echo "⚠ Warning: Database initialization had issues"
    echo "Attempting to continue anyway..."
fi
echo ""

# Step 2: Launch dashboard
echo "[2/2] Starting CLI dashboard..."
echo ""
python3 dashboard/cli_dashboard.py

echo ""
echo "Dashboard stopped"
