#!/bin/bash

# StealthShark GUI Launcher
# Desktop launcher for PyQt6 GUI application

echo "🦈 Starting StealthShark GUI..."
echo "================================"

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Define virtual environment directory
VENV_DIR="$SCRIPT_DIR/venv"

# Activate virtual environment if it exists
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
