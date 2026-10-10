#!/bin/bash
# Install omarchy-cursor theme
# Usage: ./install.sh [--theme <name>] [--base "#hex"]

set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Installing dependencies..."
source .venv/bin/activate
pip install -e . -q

echo "Building and installing theme..."
python build.py "$@" --install
