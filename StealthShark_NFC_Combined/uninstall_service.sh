#!/bin/bash
# StealthShark NFC Combined Service Uninstaller

PLIST_NAME="com.aimf.stealthshark-nfc"
LAUNCH_AGENTS_DIR="${HOME}/Library/LaunchAgents"

echo "🦈 StealthShark NFC Combined Service Uninstaller"
echo "==============================================="

# Check if service is installed
if [ -f "${LAUNCH_AGENTS_DIR}/${PLIST_NAME}.plist" ]; then
    echo "🛑 Stopping service..."
    launchctl unload "${LAUNCH_AGENTS_DIR}/${PLIST_NAME}.plist" 2>/dev/null
    
    echo "🗑️  Removing service configuration..."
    rm "${LAUNCH_AGENTS_DIR}/${PLIST_NAME}.plist"
    
    echo "✅ Service uninstalled successfully!"
else
    echo "ℹ️  Service not installed."
fi

echo ""
echo "📝 Note: Log files have been preserved in ./logs/"
