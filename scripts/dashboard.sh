#!/bin/bash
# SIEM Lite Dashboard Script (new version)
# This script runs the dashboard using the new CLI.

set -e

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

source venv/bin/activate

siem-lite dashboard 