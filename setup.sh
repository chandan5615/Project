#!/bin/bash
# Sentinel Agent - Setup Script
# Creates a virtual environment and installs all dependencies

echo "🚀 Setting up Sentinel Agent environment..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run Sentinel Agent:"
echo "  sudo python main.py"
echo ""
