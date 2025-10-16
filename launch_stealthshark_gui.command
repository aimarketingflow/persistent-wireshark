#!/bin/bash
# StealthShark GUI Launcher
# Launches the Multi-Interface Shark GUI with proper Python environment

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Use Homebrew Python with all dependencies installed
PYTHON_PATH="/opt/homebrew/bin/python3.13"

echo "🦈 StealthShark Multi-Interface Network Monitor"
echo "=============================================="
echo ""
echo "Starting GUI application..."
echo ""

# Launch the GUI
exec "$PYTHON_PATH" multi_interface_shark_gui.py
