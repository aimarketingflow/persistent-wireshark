#!/bin/bash

# StealthShark GUI Launcher
# Desktop launcher for PyQt6 GUI application

echo "🦈 Starting StealthShark GUI..."
echo "================================"

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

# Check if PyQt6 is available
python3 -c "import PyQt6" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing PyQt6..."
    pip3 install PyQt6
fi

# Ask for duration
read -p "Enter capture duration in hours (default: 4): " duration
if [ -z "$duration" ]; then
    duration="4"
fi

# Launch the GUI
echo "Launching StealthShark GUI with $duration hour rotation cycles..."
python3 gui_memory_monitor.py --duration $duration

echo "StealthShark GUI closed."
read -p "Press Enter to exit..."
