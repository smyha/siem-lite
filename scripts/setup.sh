#!/bin/bash
# SIEM Lite Setup Script (new version)
# This script sets up the Python environment and installs dependencies.

set -e

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "📦 Virtual environment already exists"
fi

source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies from pyproject.toml
pip install .

echo "✅ Environment setup complete." 