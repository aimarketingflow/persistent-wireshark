#!/bin/bash
# StealthShark Network Monitor Auto-Launcher
# Auto-launches Multi-Interface Shark GUI (Option 3)
# Created: 2025-09-28

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🦈 StealthShark Network Monitor - Auto Launch"
echo "=============================================="
echo ""
echo "🚀 Auto-launching Multi-Interface Shark GUI (ALL interfaces)..."
echo ""

# Add verbose logging as per user requirements
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting StealthShark Multi-Interface GUI..."
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Working directory: $SCRIPT_DIR"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Executing: python3 multi_interface_shark_gui.py"

# Launch option 3 directly
python3 multi_interface_shark_gui.py

# Log completion
echo "[$(date '+%Y-%m-%d %H:%M:%S')] StealthShark session ended."
