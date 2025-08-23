# Persistent Wireshark Monitor - Terminal Guide

## Latest Tested Commands (August 22, 2025)

### Quick Start Commands

```bash
# Navigate to monitor directory
cd /Users/flowgirl/Documents/_Behavioral_Cybersec_Analysis/Amazon-exploit-via-phone/Persistent_Wireshark_Monitor

# Setup virtual environment (first time only)
python3 cli_wireshark_monitor.py --setup-only

# Launch GUI interface
./wireshark_monitor_venv/bin/python3 wireshark_monitor_gui.py

# Start command-line monitoring (1-hour captures)
./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py

# Check current status
./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --status
```

### GUI Application Features

#### 🖥️ **Main Interface**
- **Dark Theme**: Professional cybersecurity interface
- **Split Panel**: Controls on left, monitoring on right
- **Real-time Updates**: Interface stats update every 2 seconds
- **Tabbed Views**: Activity, Logs, and Files tabs

#### ⚙️ **Configuration Options**
- **Capture Duration**: 1 minute to 5 hours via dropdown
- **Check Interval**: 1-30 seconds via slider
- **Capture Directory**: Custom folder selection
- **Interface List**: Real-time interface discovery

#### 📊 **Monitoring Displays**
- **Active Captures Table**: Shows running captures with timing
- **Interface Activity**: Real-time packet/byte counts
- **Log Display**: Comprehensive event logging
- **File Browser**: View and manage PCAP files

### Command Line Options

```bash
# Basic monitoring with custom duration
./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --duration 1800  # 30 minutes

# Fast monitoring (2-second intervals)
./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --interval 2

# Custom storage location
./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --capture-dir /path/to/storage

# Silent mode (no desktop alerts)
./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --no-alerts

# Status check only
./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --status
```

### Testing and Validation

```bash
# Run comprehensive test suite
./wireshark_monitor_venv/bin/python3 test_monitor.py

# Generate network activity for testing
curl -s https://httpbin.org/get > /dev/null
ping -c 5 google.com
```

### Interface Detection Results

**Successfully Detected Interfaces:**
- `en0` (Wi-Fi) - Primary network interface
- `lo0` (Loopback) - Local traffic monitoring
- `awdl0` (Apple Wireless Direct Link)
- `llw0` (Low Latency WLAN)
- `pflog0` (Packet Filter logging)
- `utun0-3` (VPN tunnel interfaces)
- `bridge0`, `ap1`, `en1-5`, `gif0`, `stf0` (Additional interfaces)

### File Organization

```
Persistent_Wireshark_Monitor/
├── persistent_wireshark_monitor.py    # Core monitoring engine
├── wireshark_monitor_gui.py          # PyQt6 GUI application
├── cli_wireshark_monitor.py          # CLI launcher
├── test_monitor.py                   # Test suite
├── requirements_wireshark_monitor.txt # Dependencies
├── wireshark_monitor_readme.md       # Full documentation
├── wireshark_monitor_venv/           # Virtual environment
├── pcap_captures/                    # Default capture storage
│   ├── active/                       # Currently recording
│   ├── completed/                    # Finished captures
│   └── logs/                         # Monitor logs
└── test_captures/                    # Test capture storage
```

### Aliases for Quick Access

Add to your `~/.zshrc`:

```bash
# Wireshark Monitor Aliases
alias wireshark_gui='cd /Users/flowgirl/Documents/_Behavioral_Cybersec_Analysis/Amazon-exploit-via-phone/Persistent_Wireshark_Monitor && ./wireshark_monitor_venv/bin/python3 wireshark_monitor_gui.py'
alias wireshark_start='cd /Users/flowgirl/Documents/_Behavioral_Cybersec_Analysis/Amazon-exploit-via-phone/Persistent_Wireshark_Monitor && ./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py'
alias wireshark_status='cd /Users/flowgirl/Documents/_Behavioral_Cybersec_Analysis/Amazon-exploit-via-phone/Persistent_Wireshark_Monitor && ./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --status'
alias wireshark_test='cd /Users/flowgirl/Documents/_Behavioral_Cybersec_Analysis/Amazon-exploit-via-phone/Persistent_Wireshark_Monitor && ./wireshark_monitor_venv/bin/python3 test_monitor.py'
alias wireshark_5min='cd /Users/flowgirl/Documents/_Behavioral_Cybersec_Analysis/Amazon-exploit-via-phone/Persistent_Wireshark_Monitor && ./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --duration 300'
```

### GUI Usage Instructions

#### Starting the GUI
1. **Launch**: Run `wireshark_gui` alias or full command
2. **Configure**: Set capture duration and check interval
3. **Select Directory**: Choose where to store PCAP files
4. **Start Monitoring**: Click "🚀 Start Monitor" button

#### Monitoring Interface Activity
- **Activity Tab**: View active captures and interface statistics
- **Green Status**: Interface has recent packet activity
- **Real-time Updates**: Stats refresh every 2 seconds
- **Capture Triggers**: Automatic when packet count increases

#### Managing Captures
- **Files Tab**: Browse active and completed captures
- **Open Folder**: Direct access to capture directory
- **Export Logs**: Save monitoring logs to file
- **Auto-cleanup**: Files older than 7 days removed automatically

#### Alert System
- **Desktop Notifications**: macOS alerts for new interface activity
- **Console Alerts**: Real-time log messages in GUI
- **Popup Warnings**: Critical alerts shown in dialog boxes

### Troubleshooting

#### Common Issues and Solutions

1. **GUI Won't Start**
```bash
# Check PyQt6 installation
./wireshark_monitor_venv/bin/python3 -c "import PyQt6; print('PyQt6 OK')"

# Reinstall if needed
./wireshark_monitor_venv/bin/pip3 install --upgrade PyQt6
```

2. **No Packet Captures Created**
```bash
# Check tshark availability
which tshark
tshark --version

# Install Wireshark if missing
brew install wireshark

# Check permissions (may need sudo for some interfaces)
sudo ./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --duration 300
```

3. **Interface Not Detected**
```bash
# List available interfaces
tshark -D
ifconfig

# Refresh interface list in GUI
# Click "🔄 Refresh Interfaces" button
```

4. **Permission Denied Errors**
```bash
# Run with elevated privileges
sudo ./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py

# Or fix tshark permissions (one-time setup)
sudo chgrp admin /usr/local/bin/tshark
sudo chmod 754 /usr/local/bin/tshark
```

### Performance Optimization

#### Resource Usage
- **Memory**: ~50-100MB for GUI + monitoring
- **CPU**: Minimal impact during idle monitoring
- **Disk**: Varies by network activity (1-100MB/hour typical)
- **Network**: No performance impact on monitored interfaces

#### Optimization Settings
```bash
# Low resource mode (longer intervals)
./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --interval 10

# High sensitivity mode (short intervals)
./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --interval 1

# Large capture sessions
./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --duration 18000  # 5 hours
```

### Integration with Existing Tools

#### Compatible with Existing Analysis
- **PCAP Format**: Standard format compatible with Wireshark, tshark
- **File Naming**: Consistent with existing analysis scripts
- **Storage Structure**: Organized for forensic analysis
- **JSON Reports**: Machine-readable status and activity data

#### Analysis Workflow
1. **Monitor**: Persistent capture of network activity
2. **Detect**: Automatic alerts for new interface activity
3. **Capture**: Timed sessions with configurable duration
4. **Analyze**: Use existing exploit analysis tools on PCAP files
5. **Report**: Integrate findings with case documentation

### Security Considerations

#### Data Protection
- **Encrypted Storage**: Consider encrypting capture directory
- **Access Control**: Limit access to PCAP files
- **Retention Policy**: Automatic cleanup after 7 days
- **Legal Compliance**: Ensure monitoring complies with local laws

#### Network Security
- **Passive Monitoring**: No impact on network traffic
- **Interface Isolation**: Monitors without interfering
- **Privilege Separation**: Run with minimal required permissions
- **Audit Trail**: Comprehensive logging of all activities

### Advanced Features

#### Custom Alert Integration
The GUI supports custom alert callbacks for integration with external systems:
- **Slack Notifications**: Send alerts to security channels
- **Email Alerts**: Automated incident notifications
- **SIEM Integration**: Forward alerts to security platforms
- **Custom Scripts**: Trigger automated responses

#### Batch Processing
```bash
# Process multiple capture sessions
for duration in 300 900 1800; do
    ./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --duration $duration &
    sleep 10
done
```

#### Automated Deployment
```bash
# Setup script for new systems
#!/bin/bash
cd /path/to/monitor
python3 cli_wireshark_monitor.py --setup-only
./wireshark_monitor_venv/bin/python3 test_monitor.py
echo "Wireshark Monitor ready for deployment"
```
