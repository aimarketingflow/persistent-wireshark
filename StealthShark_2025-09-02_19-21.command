#!/bin/bash
# StealthShark Network Monitor GUI Launcher
# Updated: 2025-09-02_19-21 - Fixed path to project directory and enhanced GUI with timer fixes
# Created: 2025-08-31

echo "🦈 Starting StealthShark Enhanced GUI..."
echo "================================"

# Navigate to the actual StealthShark project directory
cd "/Users/flowgirl/Documents/StealthShark"

# Verify we're in the right directory
if [ ! -f "enhanced_wireshark_monitor_gui.py" ]; then
    echo "❌ Error: Cannot find enhanced_wireshark_monitor_gui.py"
    echo "Current directory: $(pwd)"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ Found StealthShark project files"
echo "📁 Working directory: $(pwd)"

# Launch the enhanced GUI with timer fixes
echo "🚀 Launching Enhanced GUI with timer fixes..."
python3 enhanced_wireshark_monitor_gui.py

echo ""
echo "StealthShark GUI closed."
read -p "Press Enter to exit..."
