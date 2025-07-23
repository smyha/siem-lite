#!/bin/bash
# SIEM Lite Startup Script (new version)
# This script sets up the environment and starts the API server using the new CLI.

set -e

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

source venv/bin/activate

# Setup environment (idempotent)
siem-lite setup

# Start API server
siem-lite api

