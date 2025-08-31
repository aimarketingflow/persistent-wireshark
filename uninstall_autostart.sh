#!/bin/bash

# StealthShark Auto-Start Uninstaller
# Removes StealthShark from Launch Agents

echo "🦈 StealthShark Auto-Start Uninstaller"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Launch Agent configuration
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_NAME="com.stealthshark.monitor.plist"
PLIST_PATH="$LAUNCH_AGENTS_DIR/$PLIST_NAME"

# Check if Launch Agent is installed
if [ ! -f "$PLIST_PATH" ]; then
    echo -e "${YELLOW}StealthShark auto-start is not installed.${NC}"
    exit 0
fi

# Unload the Launch Agent
echo -e "${YELLOW}Stopping StealthShark service...${NC}"
launchctl unload "$PLIST_PATH" 2>/dev/null

# Remove the plist file
echo -e "${YELLOW}Removing Launch Agent...${NC}"
rm -f "$PLIST_PATH"

# Verify removal
if ! launchctl list | grep -q "com.stealthshark.monitor"; then
    echo -e "${GREEN}✅ StealthShark auto-start successfully uninstalled!${NC}"
    echo ""
    echo "StealthShark will no longer start automatically on boot."
    echo "You can still run it manually using:"
    echo "  • ./launch_cli.command"
    echo "  • ./launch_gui.command"
    echo "  • python3 enhanced_memory_monitor.py"
else
    echo -e "${RED}❌ Warning: Service may still be partially installed${NC}"
    echo "Try running: launchctl remove com.stealthshark.monitor"
fi

echo ""
echo "Uninstall complete!"
