#!/bin/bash
# Create StealthShark Desktop Shortcut
# Creates a proper macOS desktop shortcut for StealthShark Auto-Launch

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DESKTOP_PATH="$HOME/Desktop"
SHORTCUT_NAME="StealthShark Multi-Interface"

echo "🦈 Creating StealthShark Desktop Shortcut..."
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Creating desktop shortcut at: $DESKTOP_PATH"

# Create AppleScript application
cat > "$DESKTOP_PATH/$SHORTCUT_NAME.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>StealthShark</string>
    <key>CFBundleIdentifier</key>
    <string>com.stealthshark.launcher</string>
    <key>CFBundleName</key>
    <string>StealthShark Multi-Interface</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>
EOF

# Create the directory structure
mkdir -p "$DESKTOP_PATH/$SHORTCUT_NAME.app/Contents/MacOS"

# Create the executable script
cat > "$DESKTOP_PATH/$SHORTCUT_NAME.app/Contents/MacOS/StealthShark" << EOF
#!/bin/bash
cd "$SCRIPT_DIR"
./StealthShark_AutoLaunch.command
EOF

# Make executable
chmod +x "$DESKTOP_PATH/$SHORTCUT_NAME.app/Contents/MacOS/StealthShark"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Desktop shortcut created successfully!"
echo "✅ You can now double-click '$SHORTCUT_NAME.app' on your desktop to launch StealthShark!"
