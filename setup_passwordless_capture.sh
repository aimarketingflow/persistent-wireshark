#!/bin/bash

# Persistent Wireshark Monitor - Passwordless Capture Setup
# This script configures the system for password-less packet capture

echo "🔧 Setting up passwordless packet capture for Persistent Wireshark Monitor..."

# Method 1: Add tcpdump to sudoers with NOPASSWD
echo "📝 Configuring sudoers for tcpdump..."
SUDOERS_LINE="$USER ALL=(root) NOPASSWD: /usr/sbin/tcpdump"

# Check if the line already exists
if sudo grep -q "$SUDOERS_LINE" /etc/sudoers 2>/dev/null; then
    echo "✅ Sudoers already configured for tcpdump"
else
    echo "Adding tcpdump to sudoers with NOPASSWD..."
    echo "$SUDOERS_LINE" | sudo tee -a /etc/sudoers > /dev/null
    echo "✅ Added tcpdump to sudoers"
fi

# Method 2: Set up ChmodBPF for Wireshark (if installed)
echo "🔍 Checking for ChmodBPF..."
if [ -f "/Library/LaunchDaemons/org.wireshark.ChmodBPF.plist" ]; then
    echo "✅ ChmodBPF already installed"
    # Load the daemon if not already loaded
    if ! sudo launchctl list | grep -q "org.wireshark.ChmodBPF"; then
        echo "🚀 Loading ChmodBPF daemon..."
        sudo launchctl load /Library/LaunchDaemons/org.wireshark.ChmodBPF.plist
    fi
else
    echo "⚠️  ChmodBPF not found. Install with: brew install --cask wireshark-chmodbpf"
fi

# Method 3: Create a wrapper script with setuid (alternative approach)
echo "📄 Creating tcpdump wrapper script..."
WRAPPER_SCRIPT="/usr/local/bin/tcpdump_wrapper"

sudo tee "$WRAPPER_SCRIPT" > /dev/null << 'EOF'
#!/bin/bash
# Tcpdump wrapper for Persistent Wireshark Monitor
exec /usr/sbin/tcpdump "$@"
EOF

sudo chmod +x "$WRAPPER_SCRIPT"
echo "✅ Created tcpdump wrapper at $WRAPPER_SCRIPT"

# Method 4: Check BPF device permissions
echo "🔍 Checking BPF device permissions..."
BPF_DEVICES=$(ls /dev/bpf* 2>/dev/null | head -5)
if [ -n "$BPF_DEVICES" ]; then
    echo "📋 BPF devices found:"
    ls -la /dev/bpf* | head -5
    
    # Check if user can access BPF devices
    if [ -r "/dev/bpf0" ]; then
        echo "✅ User has read access to BPF devices"
    else
        echo "⚠️  User does not have BPF access - ChmodBPF or sudo required"
    fi
else
    echo "⚠️  No BPF devices found"
fi

echo ""
echo "🎯 Setup Summary:"
echo "1. ✅ Sudoers configured for password-less tcpdump"
echo "2. 🔍 ChmodBPF status checked"
echo "3. ✅ Tcpdump wrapper script created"
echo "4. 🔍 BPF device permissions verified"
echo ""
echo "🚀 You can now run packet capture without password prompts!"
echo "   Test with: sudo tcpdump -i lo0 -c 1"
echo ""
