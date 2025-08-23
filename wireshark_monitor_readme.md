# Persistent Wireshark Monitor

## Overview
Advanced network interface monitoring system that automatically detects traffic on any network interface and triggers timed packet captures. Monitors all available interfaces (en0, lo0, awdl0, llw0, pflog0, utun0-3, etc.) and alerts when new interfaces become active.

## Key Features

### 🔍 **Multi-Interface Monitoring**
- Automatically discovers all network interfaces on macOS
- Monitors default interfaces: `lo0` (loopback) and `en0` (Wi-Fi/Ethernet)
- Detects new interfaces and alerts user immediately
- Tracks packet/byte counts for activity detection

### ⏱️ **Configurable Auto-Capture**
- Capture duration: 1 minute to 5 hours (60-18000 seconds)
- Automatic session restart after capture completion
- File rotation to prevent disk space issues
- Organized storage in `active/` and `completed/` directories

### 🚨 **Alert System**
- macOS desktop notifications for new interface activity
- Console alerts for immediate visibility
- Comprehensive logging of all events
- Status reports with interface activity history

### 📁 **Organized Storage**
```
pcap_captures/
├── active/          # Currently recording captures
├── completed/       # Finished capture files
└── logs/           # Monitor logs and status reports
```

## Installation & Setup

### 1. Navigate to Monitor Directory
```bash
cd /Users/flowgirl/Documents/_Behavioral_Cybersec_Analysis/Amazon-exploit-via-phone/Persistent_Wireshark_Monitor
```

### 2. Setup Virtual Environment
```bash
# Setup venv and dependencies
python3 cli_wireshark_monitor.py --setup-only
```

### 3. Verify Wireshark/tshark Installation
```bash
# Check if tshark is available
tshark --version

# If not installed, install Wireshark (includes tshark)
brew install wireshark
```

## Usage Examples

### Quick Start - Default Monitoring
```bash
# Start monitoring with 1-hour captures
python3 cli_wireshark_monitor.py

# Start monitoring with 30-minute captures
python3 cli_wireshark_monitor.py --duration 1800
```

### Custom Configurations
```bash
# 5-minute captures, check every 2 seconds
python3 cli_wireshark_monitor.py --duration 300 --interval 2

# 2-hour captures, custom storage location
python3 cli_wireshark_monitor.py --duration 7200 --capture-dir /path/to/storage

# Monitor without desktop alerts
python3 cli_wireshark_monitor.py --no-alerts
```

### Status and Monitoring
```bash
# Check current status
python3 cli_wireshark_monitor.py --status

# View active captures
ls -la pcap_captures/active/

# View completed captures
ls -la pcap_captures/completed/
```

## Interface Detection Logic

### Default Monitored Interfaces
- **`lo0`** (Loopback) - Always monitored for local traffic
- **`en0`** (Primary Network) - Wi-Fi or Ethernet interface

### Additional Interfaces (Auto-detected)
- **`awdl0`** - Apple Wireless Direct Link
- **`llw0`** - Low Latency WLAN
- **`pflog0`** - Packet Filter logging
- **`utun0-3`** - VPN tunnel interfaces

### New Interface Alert System
When a new interface appears (e.g., VPN connection, USB tethering):
1. **Immediate Detection** - Interface discovered within 5-50 seconds
2. **Desktop Alert** - macOS notification sent to user
3. **Auto-Capture** - If interface has immediate activity, capture starts
4. **Logging** - All events logged for forensic analysis

## Capture Behavior

### Trigger Conditions
- **Packet Count Increase** - Any increase in packet count triggers capture
- **New Interface Activity** - Immediate capture if new interface has traffic
- **Default Interface Monitoring** - Continuous monitoring of lo0/en0

### Capture Sessions
- **Duration**: User-configurable (1 min - 5 hours)
- **Auto-Restart**: New session starts automatically after completion
- **File Naming**: `{interface}_{timestamp}.pcapng`
- **Rotation**: Max 5 files per interface to prevent disk overflow

### File Management
- **Active Directory**: Currently recording captures
- **Completed Directory**: Finished captures moved here
- **Auto-Cleanup**: Files older than 7 days automatically removed
- **Status Reports**: JSON reports generated every 10 minutes

## Command Line Options

```bash
python3 cli_wireshark_monitor.py [OPTIONS]

Options:
  --duration SECONDS     Capture duration (60-18000, default: 3600)
  --interval SECONDS     Check interval (default: 5)
  --capture-dir PATH     Storage directory (default: ./pcap_captures)
  --no-alerts           Disable desktop notifications
  --status              Show current status and exit
  --setup-only          Only setup virtual environment
```

## Monitoring Output

### Real-Time Console Output
```
2025-08-22 17:25:00 - INFO - Persistent Wireshark Monitor initialized
2025-08-22 17:25:00 - INFO - Discovered interfaces: ['awdl0', 'en0', 'llw0', 'lo0', 'pflog0', 'utun0', 'utun1', 'utun2', 'utun3']
2025-08-22 17:25:05 - INFO - Activity detected on en0: +15 packets, +2048 bytes
2025-08-22 17:25:05 - INFO - Started capture on en0 -> pcap_captures/active/en0_20250822_172505.pcapng
🚨 ALERT: Started packet capture on en0
```

### Status Report Example
```json
{
  "timestamp": "2025-08-22T17:25:00",
  "monitored_interfaces": ["awdl0", "en0", "llw0", "lo0", "pflog0", "utun0"],
  "active_captures": 2,
  "capture_duration_minutes": 60.0,
  "interface_activity": {
    "en0": {
      "total_packets": 1547,
      "total_bytes": 234567,
      "last_activity": "2025-08-22T17:24:55",
      "is_capturing": true
    }
  }
}
```

## Integration with Existing Security Tools

### Correlation with Phone Exploit Analysis
- Uses same monitoring approach as existing phone traffic blocker
- Captures can be analyzed with existing exploit analysis tools
- PCAP files compatible with current forensic workflow

### File Naming Convention
- **Format**: `{interface}_{YYYYMMDD_HHMMSS}.pcapng`
- **Example**: `en0_20250822_172505.pcapng`
- **Compatible**: With existing analysis script naming patterns

## Aliases for Quick Access

Add to your `~/.zshrc`:
```bash
alias start_wireshark_monitor='cd /Users/flowgirl/Documents/_Behavioral_Cybersec_Analysis/Amazon-exploit-via-phone/Persistent_Wireshark_Monitor && python3 cli_wireshark_monitor.py'
alias wireshark_status='cd /Users/flowgirl/Documents/_Behavioral_Cybersec_Analysis/Amazon-exploit-via-phone/Persistent_Wireshark_Monitor && python3 cli_wireshark_monitor.py --status'
alias wireshark_5min='cd /Users/flowgirl/Documents/_Behavioral_Cybersec_Analysis/Amazon-exploit-via-phone/Persistent_Wireshark_Monitor && python3 cli_wireshark_monitor.py --duration 300'
alias wireshark_1hr='cd /Users/flowgirl/Documents/_Behavioral_Cybersec_Analysis/Amazon-exploit-via-phone/Persistent_Wireshark_Monitor && python3 cli_wireshark_monitor.py --duration 3600'
```

## Security Considerations

### Permissions Required
- **tshark/Wireshark**: Requires admin privileges for packet capture
- **Interface Access**: May need to run with `sudo` for some interfaces
- **File System**: Write access to capture directory

### Privacy & Legal
- **Network Traffic**: Captures all network traffic on monitored interfaces
- **Sensitive Data**: PCAP files may contain sensitive information
- **Retention**: Automatic cleanup after 7 days for privacy
- **Legal Compliance**: Ensure monitoring complies with local laws

## Troubleshooting

### Common Issues

1. **Permission Denied**
```bash
# Run with sudo if needed
sudo python3 cli_wireshark_monitor.py
```

2. **tshark Not Found**
```bash
# Install Wireshark (includes tshark)
brew install wireshark
```

3. **Interface Not Detected**
```bash
# Check available interfaces
tshark -D
```

4. **Disk Space Issues**
```bash
# Check capture directory size
du -sh pcap_captures/
```

### Debug Mode
```bash
# Enable verbose logging
python3 persistent_wireshark_monitor.py --interval 1 --capture-dir ./debug_captures
```

## Performance Impact

### Resource Usage
- **CPU**: Minimal impact during monitoring phase
- **Memory**: ~50-100MB for monitoring process
- **Disk**: Varies by network activity (typically 1-100MB per hour)
- **Network**: No impact on network performance

### Optimization
- Automatic file rotation prevents disk overflow
- Configurable check intervals balance responsiveness vs. CPU usage
- Background processing minimizes system impact

## Advanced Usage

### Custom Alert Integration
The monitor can be extended with custom alert functions:
```python
def custom_alert(message):
    # Send to Slack, email, etc.
    pass

monitor = PersistentWiresharkMonitor(alert_callback=custom_alert)
```

### Integration with Security Tools
- PCAP files can be analyzed with existing exploit analysis scripts
- Compatible with Wireshark, tshark, and other network analysis tools
- JSON status reports can be integrated with SIEM systems
