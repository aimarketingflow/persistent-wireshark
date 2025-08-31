#!/bin/bash

# StealthShark CLI Launcher
# Desktop launcher for command-line monitoring

echo "🦈 Starting StealthShark CLI Monitor..."
echo "======================================"

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
VENV_DIR="$SCRIPT_DIR/venv"
if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
fi

# Check for user registration (optional)
python3 -c "from user_registration import check_and_prompt_registration; check_and_prompt_registration()" 2>/dev/null || true

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
    
    echo "Installing dependencies..."
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
else
    echo "Virtual environment already exists."
fi

# Show usage options
echo ""
echo "StealthShark CLI Options:"
echo "1. Enhanced Memory Monitor (recommended)"
echo "2. Simple TShark Monitor"
echo "3. Exit"
echo ""

# Ask for duration
read -p "Enter capture duration in hours (default: 4): " duration
if [ -z "$duration" ]; then
    duration="4"
fi
echo "Using $duration hour rotation cycles"

read -p "Select option (1-3): " choice

case $choice in
    1)
        echo "Launching Enhanced Memory Monitor with $duration hour rotation..."
        python3 enhanced_memory_monitor.py --duration $duration
        ;;
    2)
        echo "Available interfaces: en0, en1, awdl0"
        read -p "Enter interfaces to monitor (space-separated): " interfaces
        if [ -z "$interfaces" ]; then
            interfaces="en0"
        fi
        echo "Launching Simple Monitor on: $interfaces with $duration hour rotation"
        python3 simple_tshark_monitor.py $interfaces --duration $duration
        ;;
    3)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid option. Launching Enhanced Monitor with $duration hour rotation..."
        python3 enhanced_memory_monitor.py --duration $duration
        ;;
esac

echo ""
echo "StealthShark CLI session ended."
read -p "Press Enter to exit..."
