#!/bin/bash
# StealthShark Network Monitor Launcher
# Updated: 2025-09-26 - Fixed to work with available files
# Created: 2025-08-31

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🦈 StealthShark Network Monitor"
echo "================================"
echo ""
echo "Available monitoring options:"
echo "1) Persistent Wireshark Monitor (Advanced)"
echo "2) Simple TShark Monitor (Lightweight)"
echo "3) Multi-Interface Shark GUI (ALL interfaces)"
echo "4) LoopbackShark GUI (Localhost only)"
echo "5) Enhanced Wireshark GUI (Full featured)"
echo "6) Test GUI functionality"
echo "7) Exit"
echo ""

read -p "Select option (1-7): " choice

case $choice in
    1)
        echo "🦈 Starting Persistent Wireshark Monitor..."
        python3 persistent_wireshark_monitor.py
        ;;
    2)
        echo "🦈 Starting Simple TShark Monitor..."
        python3 simple_tshark_monitor.py
        ;;
    3)
        echo "🦈 Starting Multi-Interface Shark GUI (ALL interfaces)..."
        python3 multi_interface_shark_gui.py
        ;;
    4)
        echo "🦈 Starting LoopbackShark GUI (Localhost only)..."
        cd LoopbackShark
        PYTHONPATH=".:$PYTHONPATH" python3 loopbackshark_gui.py
        ;;
    5)
        echo "🦈 Starting Enhanced Wireshark GUI (Full featured)..."
        python3 enhanced_wireshark_monitor_gui.py
        ;;
    6)
        echo "🧪 Running GUI Tests..."
        python3 test_gui.py
        ;;
    7)
        echo "Goodbye! 🦈"
        exit 0
        ;;
    *)
        echo "Invalid option. Starting Persistent Wireshark Monitor by default..."
        python3 persistent_wireshark_monitor.py
        ;;
esac
