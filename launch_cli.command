#!/bin/bash

# StealthShark CLI Launcher
# Desktop launcher for command-line monitoring

echo "🦈 Starting StealthShark CLI Monitor..."
echo "======================================"

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    echo "Installing dependencies..."
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
else
    echo "Activating existing virtual environment..."
    source venv/bin/activate
fi

# Show usage options
echo ""
echo "StealthShark CLI Options:"
echo "1. Enhanced Memory Monitor (recommended)"
echo "2. Simple TShark Monitor"
echo "3. Exit"
echo ""

read -p "Select option (1-3): " choice

case $choice in
    1)
        echo "Launching Enhanced Memory Monitor..."
        python3 enhanced_memory_monitor.py
        ;;
    2)
        echo "Available interfaces: en0, en1, awdl0"
        read -p "Enter interfaces to monitor (space-separated): " interfaces
        if [ -z "$interfaces" ]; then
            interfaces="en0"
        fi
        echo "Launching Simple Monitor on: $interfaces"
        python3 simple_tshark_monitor.py $interfaces
        ;;
    3)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid option. Launching Enhanced Monitor..."
        python3 enhanced_memory_monitor.py
        ;;
esac

echo ""
echo "StealthShark CLI session ended."
read -p "Press Enter to exit..."
