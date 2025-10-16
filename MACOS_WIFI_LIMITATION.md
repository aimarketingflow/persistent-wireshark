# macOS WiFi Scanning Limitation

## Issue Summary
WiFi threat detection and network scanning features have been **removed** from StealthShark due to macOS privacy restrictions.

## Technical Details

### The Problem
Starting with recent versions of macOS (Sequoia and later), Apple implemented system-level privacy protections that redact WiFi SSID names when accessed through command-line tools:

```bash
$ system_profiler SPAirPortDataType
...
Other Local Wi-Fi Networks:
  <redacted>:
    PHY Mode: 802.11ax
    Channel: 157 (5GHz, 80MHz)
    Security: WPA2 Personal
  <redacted>:
    PHY Mode: 802.11g/n
    Channel: 6 (2GHz, 20MHz)
    Security: Open
```

All WiFi network names appear as `<redacted>`, making it impossible to:
- Identify specific networks
- Detect suspicious SSIDs (e.g., "Free WiFi", "Pineapple")
- Provide meaningful threat detection
- Display useful information to users

### What We Tried

1. **system_profiler SPAirPortDataType** - SSIDs redacted ❌
2. **airport command** - No longer exists in modern macOS ❌
3. **networksetup** - Doesn't provide network scanning ❌
4. **CoreWLAN Framework** - Would require Swift/Objective-C rewrite and special entitlements ❌

### Why This Matters

The WiFi Security tab was designed to:
- Scan for nearby WiFi networks
- Detect potential WiFi Pineapple attacks
- Identify evil twin networks
- Alert on suspicious open networks
- Monitor signal strength for proximity attacks

**None of these features work when all network names are redacted.**

## Removed Features

The following have been removed from `multi_interface_shark_gui.py`:

- ✂️ WiFi Security tab
- ✂️ `WiFiThreatDetectorThread` class
- ✂️ `start_wifi_scanning()` method
- ✂️ `stop_wifi_scanning()` method
- ✂️ `update_wifi_networks()` method
- ✂️ `handle_wifi_threat()` method

## Current Functionality

StealthShark now focuses on its core strengths:

### ✅ Working Features
- **Multi-Interface Monitoring** - Monitor ALL network interfaces simultaneously
- **Packet Capture** - Capture traffic to PCAP files
- **Real-time Statistics** - Live traffic rates, packet counts, interface status
- **Capture Management** - Organized PCAP file browsing and management
- **Session Recovery** - Auto-save and crash recovery
- **Dark Theme UI** - Professional monitoring interface

### 📋 Available Tabs
1. **🌐 All Interfaces** - Real-time interface monitoring with traffic stats
2. **📋 Monitor Log** - Activity and event logging
3. **📁 Captures** - PCAP file management and organization

## Alternative Solutions

If you need WiFi threat detection on macOS:

### Option 1: Use Wireshark Directly
```bash
# Capture WiFi traffic (requires monitor mode)
sudo /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport en0 sniff 1
# Then open in Wireshark
```

### Option 2: Third-Party Tools
- **Wireless Diagnostics** (built-in macOS app)
  - Hold Option key and click WiFi icon → "Open Wireless Diagnostics"
  - Shows actual network names (not redacted)
  - Requires GUI interaction, can't be automated

- **WiFi Explorer** (commercial app)
  - Full WiFi scanning capabilities
  - Not affected by command-line restrictions

### Option 3: Linux Alternative
StealthShark's WiFi features would work perfectly on Linux where:
- `iwlist scan` provides full network information
- No SSID redaction
- Better low-level WiFi access

## Future Possibilities

### Potential Solutions (Not Implemented)
1. **Native Swift/Objective-C Extension**
   - Use CoreWLAN framework directly
   - Requires code signing and entitlements
   - Would need to be a separate binary

2. **GUI Automation**
   - Automate Wireless Diagnostics app
   - Fragile and unreliable
   - Not recommended

3. **Linux VM/Container**
   - Run WiFi scanning in Linux environment
   - Complex setup
   - Limited WiFi adapter access from VM

## Recommendation

For network security monitoring on macOS, focus on:
- **Packet-level analysis** (what StealthShark does well)
- **Traffic pattern detection**
- **Protocol analysis**
- **Connection monitoring**

For WiFi-specific security:
- Use built-in Wireless Diagnostics app manually
- Consider commercial tools like WiFi Explorer
- Use Linux for automated WiFi threat detection

## Testing Evidence

Test files demonstrating the issue:
- `test_wifi_scan.py` - Shows redacted output
- `test_wifi_thread.py` - GUI test with redacted networks

Both successfully scan and find 30+ networks, but all show as `<redacted>`.

## Date
Issue identified and documented: October 15, 2025

## Related Files
- `multi_interface_shark_gui.py` - WiFi tab removed
- `WIFI_SECURITY_FIX.md` - Initial fix attempt documentation
- `WIFI_TAB_INSTRUCTIONS.md` - Original usage instructions (now obsolete)
