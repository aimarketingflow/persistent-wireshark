#!/bin/bash

# Wireshark Monitor Desktop Launcher
# Launches the enhanced GUI with proper environment setup

# Set script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Launching Persistent Wireshark Monitor${NC}"
echo -e "${BLUE}AIMF LLC - Cybersecurity Tools${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "wireshark_monitor_venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Setting up...${NC}"
    python3 cli_wireshark_monitor.py --setup-only
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to setup virtual environment${NC}"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Check if GUI file exists
if [ ! -f "enhanced_wireshark_monitor_gui.py" ]; then
    echo -e "${RED}❌ GUI file not found in: $SCRIPT_DIR${NC}"
    echo "Please ensure you're running this from the correct directory."
    read -p "Press Enter to exit..."
    exit 1
fi

# Launch the GUI
echo -e "${GREEN}✅ Starting Enhanced Wireshark Monitor GUI...${NC}"
echo -e "${BLUE}📁 Working Directory: $SCRIPT_DIR${NC}"
echo -e "${BLUE}🔍 Monitoring all network interfaces${NC}"
echo ""

# Run the enhanced GUI
./wireshark_monitor_venv/bin/python3 enhanced_wireshark_monitor_gui.py

# Check exit status
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Wireshark Monitor closed successfully${NC}"
else
    echo -e "${RED}❌ Wireshark Monitor encountered an error${NC}"
    echo "Check the logs in gui_logs/ for details"
fi

echo ""
echo "Press Enter to close this terminal..."
read
