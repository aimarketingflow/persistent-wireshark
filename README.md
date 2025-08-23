# Persistent Wireshark Monitor

A robust network monitoring tool that automatically detects active network interfaces and captures packets using Wireshark/tshark. **Specifically designed to resist network overload attacks** that hackers use to disrupt packet capture and forensic analysis.

## 🛡️ Security Purpose

This tool was created to address a critical cybersecurity vulnerability: **hackers often overload networks to interrupt your computer's ability to save Wireshark captures**. Our persistent monitoring system ensures continuous packet capture even under attack conditions.

**[Read Full Security Disclosure](SECURITY_DISCLOSURE.md)**

## 🚀 Features

### Multi-Interface Monitoring
- **Auto-Discovery**: Detects all available network interfaces (en0, lo0, awdl0, llw0, pflog0, utun0-3, etc.)
- **Real-Time Monitoring**: Tracks packet/byte counts across all interfaces
- **New Interface Alerts**: Immediate notifications when new interfaces appear
- **Selective Monitoring**: Focus on specific interfaces or monitor all

### Configurable Auto-Capture
- **Duration Control**: Set capture duration from 30 seconds to 6 hours
- **Auto-Restart**: Continuous monitoring with automatic session restart (default enabled)
- **Emergency Save**: Automatic data preservation on crashes or force quit
- **File Rotation**: Prevents disk space issues with automatic cleanup
- **Custom Intervals**: Configurable check intervals (1-30 seconds)

### Professional GUI
- **Dark Theme**: Cybersecurity-focused interface design
- **Real-Time Updates**: Interface statistics refresh every 5 seconds
- **Comprehensive Logging**: Debug logs with export functionality
- **Alert System**: Desktop notifications for critical events

### Command Line Interface
- **CLI Launcher**: Full command-line control with virtual environment setup
- **Batch Processing**: Scriptable for automated deployments
- **Status Monitoring**: Real-time status checks and reporting
- **Flexible Configuration**: All parameters configurable via command line

## 📋 Requirements

- **macOS**: Tested on macOS with Apple Silicon and Intel
- **Python 3.8+**: Modern Python with virtual environment support
- **Wireshark/tshark**: For packet capture functionality
- **Admin Privileges**: Required for packet capture on some interfaces

## 🛠 Installation

### 1. Clone Repository
```bash
git clone https://github.com/aimarketingflow/persistent-wireshark.git
cd persistent-wireshark
```

### 2. Setup Virtual Environment
```bash
# Automatic setup with dependencies
python3 cli_wireshark_monitor.py --setup-only
```

### 3. Install Wireshark (if not present)
```bash
# Using Homebrew
brew install wireshark

# Or download from https://www.wireshark.org/
```

### 4. Verify Installation
```bash
# Run comprehensive test suite
./wireshark_monitor_venv/bin/python3 test_gui.py
```

## 🚀 Quick Start

### GUI Application (Recommended)
```bash
# Launch enhanced GUI with comprehensive logging
./wireshark_monitor_venv/bin/python3 enhanced_wireshark_monitor_gui.py
```

### Command Line Monitoring
```bash
# Start monitoring with 1-hour captures
./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py

# Custom duration and interval
./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --duration 1800 --interval 2

# Check current status
./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --status
```

## 📊 Usage Examples

### Basic Monitoring
```bash
# Monitor all interfaces with 30-minute captures
./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --duration 1800

# High-frequency monitoring (2-second checks)
./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --interval 2

# Custom storage location
./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --capture-dir /path/to/storage
```

### GUI Features
1. **Start Monitoring**: Configure duration (1min-5hrs) and click "🚀 Start Monitor"
2. **View Activity**: Real-time interface statistics in the Status tab
3. **Monitor Logs**: Comprehensive event logging in the Logs tab
4. **Manage Files**: Browse and export captures in the Files tab
5. **Export Data**: Save logs and status reports for analysis

### Testing and Validation
```bash
# Run full test suite
./wireshark_monitor_venv/bin/python3 test_gui.py

# Test network activity generation
./wireshark_monitor_venv/bin/python3 test_monitor.py
```

## 🔧 Configuration

### Command Line Options
```bash
--duration SECONDS     # Capture duration (60-18000, default: 3600)
--interval SECONDS     # Check interval (default: 5)
--capture-dir PATH     # Storage directory (default: ./pcap_captures)
--no-alerts           # Disable desktop notifications
--status              # Show current status and exit
--setup-only          # Only setup virtual environment
```

### GUI Configuration
- **Capture Duration**: Dropdown selection from 1 minute to 5 hours
- **Check Interval**: Slider control from 1-30 seconds
- **Storage Location**: Directory picker for custom capture folders
- **Interface Selection**: View and refresh available interfaces

## 📁 File Structure

```
persistent-wireshark/
├── persistent_wireshark_monitor.py    # Core monitoring engine
├── enhanced_wireshark_monitor_gui.py  # Enhanced GUI with logging
├── cli_wireshark_monitor.py          # CLI launcher
├── test_gui.py                       # GUI test suite
├── test_monitor.py                   # Network activity tests
├── requirements_wireshark_monitor.txt # Dependencies
├── wireshark_monitor_readme.md       # Detailed documentation
├── pcap_captures/                    # Default capture storage
│   ├── active/                       # Currently recording
│   ├── completed/                    # Finished captures
│   └── logs/                         # Monitor logs
├── gui_logs/                         # GUI debug logs
└── Wireshark_Monitor_Terminal_Guide/ # Terminal reference
```

## 🔍 Interface Detection

The monitor automatically detects and can monitor:

- **en0** - Primary Wi-Fi/Ethernet interface
- **lo0** - Loopback interface for local traffic
- **awdl0** - Apple Wireless Direct Link
- **llw0** - Low Latency WLAN
- **pflog0** - Packet Filter logging interface
- **utun0-3** - VPN tunnel interfaces
- **bridge0** - Network bridge interface
- **ap1** - Access Point interface

## 🚨 Alert System

### Desktop Notifications
- New interface activity detected
- Capture sessions started/completed
- Critical errors and warnings
- System status changes

### Logging Levels
- **INFO**: Normal operations and status updates
- **WARNING**: Non-critical issues and alerts
- **ERROR**: Capture failures and system errors
- **DEBUG**: Detailed troubleshooting information

## 🛡️ Security Considerations

### Permissions
- **Packet Capture**: Requires admin privileges for some interfaces
- **File Access**: Write permissions needed for capture directory
- **Network Monitoring**: Passive monitoring with no traffic impact

### Privacy
- **Data Protection**: PCAP files contain network traffic data
- **Retention Policy**: Automatic cleanup after 7 days
- **Access Control**: Secure capture file storage recommended
- **Legal Compliance**: Ensure monitoring complies with local laws

## 🔧 Troubleshooting

### Common Issues

**GUI Won't Start**
```bash
# Check PyQt6 installation
./wireshark_monitor_venv/bin/python3 -c "import PyQt6; print('PyQt6 OK')"

# Reinstall if needed
./wireshark_monitor_venv/bin/pip3 install --upgrade PyQt6
```

**No Packet Captures**
```bash
# Check tshark availability
which tshark
tshark --version

# Install Wireshark if missing
brew install wireshark

# Check permissions
sudo ./wireshark_monitor_venv/bin/python3 cli_wireshark_monitor.py --duration 300
```

**Interface Not Detected**
```bash
# List available interfaces
tshark -D
ifconfig

# Refresh in GUI or restart application
```

### Debug Mode
```bash
# Enable verbose logging
./wireshark_monitor_venv/bin/python3 enhanced_wireshark_monitor_gui.py

# Check debug logs
tail -f gui_logs/gui_debug_*.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏢 About AIMF LLC

Developed by AIMF LLC for cybersecurity analysis and network monitoring applications. Part of a comprehensive suite of security tools for threat detection and incident response.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/aimarketingflow/persistent-wireshark/issues)
- **Documentation**: See `wireshark_monitor_readme.md` for detailed usage
- **Terminal Guide**: See `Wireshark_Monitor_Terminal_Guide/` for command reference

## 🔄 Version History

- **v1.0.0** - Initial release with GUI and CLI interfaces
- **v1.1.0** - Enhanced error handling and comprehensive logging
- **v1.2.0** - Thread-safe operations and stability improvements

---

**⚠️ Important**: This tool is designed for legitimate network monitoring and cybersecurity analysis. Ensure you have proper authorization before monitoring network traffic.
