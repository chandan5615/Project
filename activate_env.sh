#!/bin/bash
# Quick activation script for Sentinel Agent virtual environment

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run ./setup.sh first to create the environment."
    exit 1
fi

echo "✅ Activating virtual environment..."
source venv/bin/activate

echo "✅ Environment activated!"
echo "You can now run: sudo python main.py"
echo ""
echo "To deactivate later, run: deactivate"
