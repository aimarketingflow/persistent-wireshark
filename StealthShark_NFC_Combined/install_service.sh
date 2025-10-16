#!/bin/bash
# StealthShark NFC Combined Service Installer

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLIST_NAME="com.aimf.stealthshark-nfc"
PLIST_FILE="${SCRIPT_DIR}/${PLIST_NAME}.plist"
LAUNCH_AGENTS_DIR="${HOME}/Library/LaunchAgents"
LOGS_DIR="${SCRIPT_DIR}/logs"

echo "🦈 StealthShark NFC Combined Service Installer"
echo "============================================="

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p "${LOGS_DIR}"

# Check if plist exists
if [ ! -f "${PLIST_FILE}" ]; then
    echo "❌ Error: ${PLIST_FILE} not found!"
    exit 1
fi

# Create LaunchAgents directory if it doesn't exist
mkdir -p "${LAUNCH_AGENTS_DIR}"

# Stop existing service if running
echo "🛑 Stopping existing service (if running)..."
launchctl unload "${LAUNCH_AGENTS_DIR}/${PLIST_NAME}.plist" 2>/dev/null

# Copy plist to LaunchAgents
echo "📋 Installing service configuration..."
cp "${PLIST_FILE}" "${LAUNCH_AGENTS_DIR}/"

# Load the service
echo "🚀 Starting service..."
launchctl load "${LAUNCH_AGENTS_DIR}/${PLIST_NAME}.plist"

# Check status
if launchctl list | grep -q "${PLIST_NAME}"; then
    echo "✅ Service installed and started successfully!"
    echo ""
    echo "📊 Service Status:"
    launchctl list | grep "${PLIST_NAME}"
    echo ""
    echo "📝 Logs will be written to:"
    echo "   - ${LOGS_DIR}/stealthshark-nfc.log"
    echo "   - ${LOGS_DIR}/stealthshark-nfc.error.log"
    echo ""
    echo "🔧 Useful commands:"
    echo "   Stop:    launchctl unload ~/Library/LaunchAgents/${PLIST_NAME}.plist"
    echo "   Start:   launchctl load ~/Library/LaunchAgents/${PLIST_NAME}.plist"
    echo "   Status:  launchctl list | grep ${PLIST_NAME}"
else
    echo "⚠️  Service installed but may not be running. Check logs for details."
fi
