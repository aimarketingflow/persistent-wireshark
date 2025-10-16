#!/bin/bash
# LoopbackShark Network Monitor GUI Launcher
# Advanced loopback traffic analysis with pattern recognition
# Created: 2025-09-08

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Change to LoopbackShark directory
cd "$SCRIPT_DIR/LoopbackShark"

# Launch LoopbackShark GUI
echo "🦈 Starting LoopbackShark - Advanced Loopback Traffic Monitor..."
echo "📁 Working directory: $(pwd)"

python3 loopbackshark_gui.py
