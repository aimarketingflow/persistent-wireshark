#!/bin/bash

# StealthShark Auto-Start Installer
# Installs StealthShark as a Launch Agent to start automatically on Mac boot

echo "🦈 StealthShark Auto-Start Installer"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the current user
CURRENT_USER=$(whoami)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Launch Agent directory
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_NAME="com.stealthshark.monitor.plist"
PLIST_SOURCE="$SCRIPT_DIR/$PLIST_NAME"
PLIST_DEST="$LAUNCH_AGENTS_DIR/$PLIST_NAME"
SETTINGS_FILE="$SCRIPT_DIR/stealthshark_settings.json"

# Create logs directory if it doesn't exist
echo -e "${YELLOW}Creating logs directory...${NC}"
mkdir -p "$SCRIPT_DIR/logs"

# Check if plist source exists
if [ ! -f "$PLIST_SOURCE" ]; then
    echo -e "${RED}Error: $PLIST_SOURCE not found!${NC}"
    exit 1
fi

# Create LaunchAgents directory if it doesn't exist
if [ ! -d "$LAUNCH_AGENTS_DIR" ]; then
    echo -e "${YELLOW}Creating LaunchAgents directory...${NC}"
    mkdir -p "$LAUNCH_AGENTS_DIR"
fi

# Check if settings file exists
if [ -f "$SETTINGS_FILE" ]; then
    echo -e "${GREEN}Loading settings from stealthshark_settings.json...${NC}"
    
    # Extract settings using Python
    duration=$(python3 -c "import json; f=open('$SETTINGS_FILE'); d=json.load(f); print(d['autostart']['duration_hours']); f.close()" 2>/dev/null || echo "4")
    monitor_type=$(python3 -c "import json; f=open('$SETTINGS_FILE'); d=json.load(f); print(d['autostart']['monitor_type']); f.close()" 2>/dev/null || echo "enhanced")
    interfaces=$(python3 -c "import json; f=open('$SETTINGS_FILE'); d=json.load(f); print(' '.join(d['autostart']['interfaces'])); f.close()" 2>/dev/null || echo "en0")
    
    echo "  Duration: $duration hours"
    echo "  Monitor: $monitor_type"
    echo "  Interfaces: $interfaces"
    echo ""
    
    # Set monitor command based on saved settings
    case $monitor_type in
        "simple")
            monitor_cmd="python3 simple_tshark_monitor.py $interfaces --duration $duration"
            ;;
        "gui")
            monitor_cmd="python3 gui_memory_monitor.py --duration $duration"
            ;;
        *)
            monitor_cmd="python3 enhanced_memory_monitor.py --duration $duration --interfaces $interfaces"
            ;;
    esac
    
    # Ask if user wants to use saved settings
    read -p "Use saved settings? (y/n) [y]: " use_saved
    if [ "$use_saved" != "n" ] && [ "$use_saved" != "N" ]; then
        echo -e "${GREEN}Using saved settings${NC}"
    else
        # Fall back to manual configuration
        echo ""
        read -p "Enter default capture duration in hours (default: 4): " duration
        if [ -z "$duration" ]; then
            duration="4"
        fi
        
        echo ""
        echo "Select monitoring mode:"
        echo "1. Enhanced Memory Monitor (recommended)"
        echo "2. Simple TShark Monitor"
        echo "3. GUI Monitor (PyQt6)"
        read -p "Select option (1-3) [default: 1]: " mode
        
        case $mode in
            2)
                monitor_cmd="python3 simple_tshark_monitor.py en0 --duration $duration"
                ;;
            3)
                monitor_cmd="python3 gui_memory_monitor.py --duration $duration"
                ;;
            *)
                monitor_cmd="python3 enhanced_memory_monitor.py --duration $duration"
                ;;
        esac
    fi
else
    echo -e "${YELLOW}No saved settings found. Run 'python3 configure_settings.py' to create them.${NC}"
    
    # Ask for duration preference
    echo ""
    read -p "Enter default capture duration in hours (default: 4): " duration
    if [ -z "$duration" ]; then
        duration="4"
    fi
    
    # Ask for monitoring mode
    echo ""
    echo "Select monitoring mode:"
    echo "1. Enhanced Memory Monitor (recommended)"
    echo "2. Simple TShark Monitor"
    echo "3. GUI Monitor (PyQt6)"
    read -p "Select option (1-3) [default: 1]: " mode
    
    case $mode in
        2)
            monitor_cmd="python3 simple_tshark_monitor.py en0 --duration $duration"
            ;;
        3)
            monitor_cmd="python3 gui_memory_monitor.py --duration $duration"
            ;;
        *)
            monitor_cmd="python3 enhanced_memory_monitor.py --duration $duration"
            ;;
    esac
fi

# Update the plist file with user preferences
echo -e "${YELLOW}Configuring auto-start with $duration hour rotation...${NC}"

# Create temporary plist with user settings
cat > "$SCRIPT_DIR/com.stealthshark.monitor.temp.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.stealthshark.monitor</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd $SCRIPT_DIR && source venv/bin/activate 2>/dev/null || (python3 -m venv venv && source venv/bin/activate && pip3 install -r requirements.txt); $monitor_cmd</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <dict>
        <key>Crashed</key>
        <true/>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    
    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/logs/stealthshark.log</string>
    
    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/logs/stealthshark_error.log</string>
    
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin</string>
        <key>PYTHONPATH</key>
        <string>$SCRIPT_DIR</string>
    </dict>
    
    <key>ThrottleInterval</key>
    <integer>30</integer>
    
    <key>Nice</key>
    <integer>10</integer>
</dict>
</plist>
EOF

# Check if already installed
if [ -f "$PLIST_DEST" ]; then
    echo -e "${YELLOW}Unloading existing Launch Agent...${NC}"
    launchctl unload "$PLIST_DEST" 2>/dev/null
fi

# Copy the plist file
echo -e "${YELLOW}Installing Launch Agent...${NC}"
cp "$SCRIPT_DIR/com.stealthshark.monitor.temp.plist" "$PLIST_DEST"

# Set correct permissions
chmod 644 "$PLIST_DEST"

# Load the Launch Agent
echo -e "${YELLOW}Loading Launch Agent...${NC}"
launchctl load "$PLIST_DEST"

# Verify installation
if launchctl list | grep -q "com.stealthshark.monitor"; then
    echo -e "${GREEN}✅ StealthShark auto-start successfully installed!${NC}"
    echo ""
    echo "StealthShark will now:"
    echo "  • Start automatically when your Mac boots"
    echo "  • Run with $duration hour capture rotation"
    echo "  • Restart if it crashes"
    echo "  • Log output to: $SCRIPT_DIR/logs/"
    echo ""
    echo "To check status: launchctl list | grep stealthshark"
    echo "To uninstall: ./uninstall_autostart.sh"
else
    echo -e "${RED}❌ Failed to install auto-start${NC}"
    echo "Please check the error log: $SCRIPT_DIR/logs/stealthshark_error.log"
    exit 1
fi

# Clean up temp file
rm -f "$SCRIPT_DIR/com.stealthshark.monitor.temp.plist"

echo ""
echo "Installation complete!"
