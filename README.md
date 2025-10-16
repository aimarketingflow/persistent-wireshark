# MobileShield - StealthShark 🦈
**Advanced Network Monitoring & Packet Capture System**

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](https://opensource.org/licenses/GPL-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform: macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)

## 🎯 Overview

StealthShark is a sophisticated network monitoring system designed for cybersecurity professionals, network administrators, and security researchers. It provides continuous, stealth packet capture with intelligent memory management and automated cleanup capabilities.

### 🔥 Key Features

- **🕵️ Stealth Operation**: Disguised processes with fake system names
- **🧠 Intelligent Memory Management**: Automated cleanup and resource optimization
- **📊 Real-time Monitoring**: Live dashboard with system metrics
- **🔄 Auto-rotation**: Time-based capture file rotation
- **⚡ Multi-interface Support**: Simultaneous monitoring across network interfaces
- **🛡️ Crash Recovery**: Watchdog processes ensure continuous operation
- **📱 Multiple Interfaces**: CLI, GUI, and Web dashboard options

## 🚀 Quick Start

### Prerequisites

```bash
# Install Wireshark (includes tshark)
brew install wireshark

# Configure BPF permissions for unprivileged capture
sudo /usr/local/bin/wireshark-chmodbpf
```

### Installation

```bash
git clone https://github.com/yourusername/StealthShark.git
cd StealthShark
python3 -m venv stealthshark_env
source stealthshark_env/bin/activate
pip3 install -r requirements.txt
```

### Launch Options

**🖥️ GUI Application (Recommended)**
```bash
./launch_gui_monitor.command
```

**⚡ Quick Status Check**
```bash
./quick_status_check.command
```

**🔧 Full CLI System**
```bash
./launch_enhanced_memory_monitor.command
```

**🧹 Cleanup Operations**
```bash
./cleanup_captures.command
```

### 🚀 Auto-Start on Mac Boot

Configure StealthShark to start automatically when your Mac boots:

**Install Auto-Start**
```bash
./install_autostart.sh
```

The installer will prompt you for:
- **Duration**: Default capture rotation period (in hours)
- **Mode**: Enhanced Monitor (recommended), Simple Monitor, or GUI

**Uninstall Auto-Start**
```bash
./uninstall_autostart.sh
```

**Check Status**
```bash
launchctl list | grep stealthshark
```

**Manual Control**
```bash
# Stop the service
launchctl unload ~/Library/LaunchAgents/com.stealthshark.monitor.plist

# Start the service
launchctl load ~/Library/LaunchAgents/com.stealthshark.monitor.plist
```

Logs are saved to: `logs/stealthshark.log` and `logs/stealthshark_error.log`

## 🏗️ Architecture

### Core Components

- **`enhanced_memory_monitor.py`** - Main monitoring engine with memory optimization
- **`gui_memory_monitor.py`** - PyQt6-based graphical interface
- **`simple_tshark_monitor.py`** - Lightweight capture daemon
- **Desktop Launchers** - One-click execution scripts

### System Design

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GUI Monitor   │    │  Memory Manager  │    │ TShark Captures │
│   (PyQt6)       │◄──►│  (Intelligent)   │◄──►│  (Stealth)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  System Tray    │    │   Watchdog       │    │  File Rotation  │
│  Integration    │    │   Processes      │    │  & Cleanup      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📊 Features Deep Dive

### 🕵️ Stealth Capabilities
- Process name obfuscation using `exec -a`
- Disguised as system processes (`kernel_task`, `launchd`, etc.)
- Minimal system footprint
- Silent operation with configurable logging

### 🧠 Memory Intelligence
- **Adaptive Thresholds**: Dynamic memory limits based on system capacity
- **Predictive Cleanup**: Proactive file management before limits are reached
- **Compression**: Automatic GZIP compression of older captures
- **Smart Rotation**: Time and size-based file rotation strategies

### 📈 Monitoring Dashboard
- Real-time memory and disk usage visualization
- Active process monitoring with detailed statistics
- Network interface status indicators
- Historical performance metrics

## 🛠️ Configuration

### Memory Settings
```python
# Default configuration in enhanced_memory_monitor.py
MAX_MEMORY_GB = 8          # Maximum memory usage
MAX_DISK_GB = 50           # Maximum disk usage
CLEANUP_THRESHOLD = 0.8    # Cleanup trigger (80%)
ROTATION_HOURS = 4         # File rotation interval
```

### Network Interfaces
```python
# Monitored interfaces (auto-detected)
INTERFACES = ['en0', 'en1', 'awdl0']  # WiFi, Ethernet, AirDrop
```

## 🔒 Security Considerations

### Permissions
- Requires BPF (Berkeley Packet Filter) access
- No root privileges needed after initial setup
- Secure file permissions on capture data

### Data Protection
- Local storage only (no cloud transmission)
- Configurable data retention policies
- Encrypted storage options available

### ⚠️ Known Limitations

**WiFi Network Scanning (macOS Sequoia+)**
- WiFi threat detection features have been **removed** due to macOS privacy restrictions
- macOS now redacts WiFi SSID names in command-line tools (`<redacted>`)
- This prevents WiFi Pineapple detection and evil twin network identification
- See [MACOS_WIFI_LIMITATION.md](MACOS_WIFI_LIMITATION.md) for technical details and alternatives
- Core packet capture and network monitoring features are **not affected**

## 📱 Interface Options

### 1. GUI Application (PyQt6)
- **Real-time dashboard** with progress bars
- **Process management** table
- **System tray** integration
- **Configuration dialogs**

### 2. Command Line Interface
- **Interactive menus** for all operations
- **Detailed logging** and status reports
- **Scriptable** for automation

### 3. Web Dashboard
- **Browser-based** monitoring
- **Remote access** capabilities
- **API endpoints** for integration

## 🧪 Use Cases

### Cybersecurity Research
- **Threat Detection**: Continuous monitoring for suspicious network activity
- **Incident Response**: Automated evidence collection
- **Malware Analysis**: Network behavior analysis

### Network Administration
- **Performance Monitoring**: Bandwidth and latency tracking
- **Troubleshooting**: Detailed packet-level diagnostics
- **Compliance**: Automated logging for regulatory requirements

### Security Operations
- **24/7 Monitoring**: Unattended operation with alerting
- **Forensic Collection**: Timestamped evidence preservation
- **Threat Hunting**: Historical data analysis

## 📊 Performance Metrics

- **Memory Efficiency**: < 100MB RAM usage during normal operation
- **CPU Impact**: < 5% CPU utilization on modern systems
- **Storage Optimization**: 60-80% compression ratio on captured data
- **Reliability**: 99.9% uptime with watchdog recovery

## 🔧 Advanced Configuration

### Custom Capture Filters
```bash
# Example: Monitor only HTTP/HTTPS traffic
tshark -i en0 -f "port 80 or port 443"

# Example: Focus on specific IP ranges
tshark -i en0 -f "net 192.168.1.0/24"
```

### Integration Examples
```python
# Python API usage
from enhanced_memory_monitor import MemoryOptimizedTSharkMonitor

monitor = MemoryOptimizedTSharkMonitor()
monitor.start_monitoring(['en0', 'en1'])
status = monitor.get_system_status()
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/yourusername/StealthShark.git
cd StealthShark
python3 -m venv dev_env
source dev_env/bin/activate
pip3 install -r requirements-dev.txt
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Wireshark Foundation** - For the excellent tshark tool
- **PyQt Project** - For the robust GUI framework
- **Security Community** - For continuous feedback and improvements

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/StealthShark/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/StealthShark/discussions)
- **Security**: Report vulnerabilities via email

---

## 🦈 **LoopbackShark - Advanced Localhost Monitoring**

**NEW**: StealthShark now includes LoopbackShark, a specialized localhost traffic analyzer with:

- **🎯 Pattern Recognition** - Automatic detection of web servers, databases, APIs
- **📊 Real-time Analysis** - Live monitoring with PyQt6 GUI
- **🔍 Application Detection** - Identifies Redis, MySQL, HTTP servers, and more
- **📈 Historical Analysis** - Trend analysis from captured data
- **⚙️ Smart Configuration** - Persistent settings with 24-hour default monitoring
- **🖥️ Desktop Launcher** - Easy access via `LoopbackShark.command`

### **🚀 Launch Options**

**StealthShark Network Monitor:**
```bash
./StealthShark.command
```

**LoopbackShark Localhost Monitor:**
```bash
./LoopbackShark.command
```

---

**Built with ❤️ for the cybersecurity community**

*StealthShark + LoopbackShark - Complete network visibility for security professionals.*

## 🎯 **MobileShield Platform**

**MobileShield** is a comprehensive mobile security platform that brings enterprise-grade network analysis, RF spectrum monitoring, and advanced threat detection to mobile devices. This platform integrates multiple security tools including StealthShark into a cohesive ecosystem designed for professional mobile security research and analysis.

### **🔥 Platform Features**
- **📱 MobileWireshark** - Wireshark-like packet analysis for Android
- **📡 Live RF Capture** - Real-time HackRF One integration for spectrum analysis
- **🦈 StealthShark** - Advanced network monitoring and packet capture
- **🔍 LoopbackShark** - Specialized localhost traffic analysis with pattern recognition
- **🔵 Advanced Bluetooth Shielding** - Device management and 2FA authentication
- **📊 Professional UI** - Dark-themed, responsive interface
- **🔒 Enterprise Security** - Compliance-ready security features

---

## 🏗️ **Project Architecture**

```
MobileShield/
├── MobileShieldAndroid/           # Main Android application
│   ├── MobileWireshark/          # React Native mobile app
│   ├── AndroidSimulator/         # Development simulator with live RF
│   ├── SDR_Hardware_Detection/   # HackRF One integration
│   └── UTM_Android_VM/          # Android VM for testing
├── PhoneRootBot/                 # Phone rooting and analysis tools
├── PineappleExpress/            # WiFi Pineapple integration
├── RaygunX/                     # Advanced penetration testing
└── WindsurfOfflineAccessEvidence/ # Offline access analysis
```

---

## 🚀 **Current Status**

### ✅ **Completed Features**
- **Live HackRF One RF Capture** - Real-time spectrum analysis (800-6000 MHz)
- **Live Phone Network Monitoring** - Packet capture from specific phone IPs
- **Memory-Optimized Android Simulator** - Stable performance with live data
- **Professional UI Components** - Dark theme with real-time visualization
- **Dual Live Capture** - RF + Network packet analysis simultaneously
- **Threat Detection Engine** - Pattern analysis for suspicious activities

### 🔄 **In Development**
- **React Native Mobile App** - Native Android application
- **Bluetooth 2FA System** - MAC address-based authentication
- **Hardware Integration** - Phone case security device concept
- **Enterprise Dashboard** - Web-based management interface

---

## 🛠️ **Technical Stack**

### **Mobile Application**
- **React Native** with TypeScript
- **PyQt6** for simulator GUI
- **Scapy** for network packet analysis
- **HackRF One SDK** for RF capture
- **SQLite** for local data storage

### **Backend & Analysis**
- **Python 3** with asyncio
- **NumPy/Matplotlib** for signal processing
- **Machine Learning** for threat detection
- **RESTful APIs** for data exchange

### **Hardware Integration**
- **HackRF One** - Software Defined Radio
- **Android Devices** - Target platform
- **Custom Hardware** - Future phone case integration

---

## 📋 **Installation & Setup**

### **Prerequisites**
```bash
# macOS requirements
brew install python3 hackrf
pip3 install PyQt6 scapy matplotlib numpy

# Android development
# Install Android Studio and SDK
# Enable USB debugging on target device
```

### **Quick Start**
```bash
# Clone repository
git clone https://github.com/AIMF-LLC/MobileShield.git
cd MobileShield

# Set up Android simulator with live RF capture
cd MobileShieldAndroid/AndroidSimulator
python3 -m venv AndroidSimulator_venv
source AndroidSimulator_venv/bin/activate
pip3 install -r requirements.txt

# Launch with live HackRF One integration
sudo ./launch_live_rf.sh
```

### **Mobile App Development**
```bash
# Set up React Native environment
cd MobileShieldAndroid/MobileWireshark
npm install
npx react-native run-android
```

---

## 🔧 **Configuration**

### **HackRF One Setup**
- Connect HackRF One via USB
- Install HackRF drivers and tools
- Run with sudo permissions for hardware access
- Configure frequency range: 800-6000 MHz

### **Network Monitoring**
- Set target phone IP address
- Configure network interface (default: en0)
- Enable packet capture permissions
- Set up threat detection rules

---

## 📊 **Usage Examples**

### **Live RF Spectrum Analysis**
```python
# Monitor phone RF emissions
from live_rf_capture import LiveRFIntegration

rf_capture = LiveRFIntegration(
    signal_callback=handle_rf_signal,
    activity_callback=handle_phone_activity
)
rf_capture.start_live_capture()
```

### **Network Packet Monitoring**
```python
# Capture phone network traffic
from live_network_capture import LiveNetworkIntegration

network_capture = LiveNetworkIntegration(
    phone_ip="10.215.173.1",
    packet_callback=handle_network_packet
)
network_capture.start_live_monitoring()
```

---

## 🔒 **Security Features**

### **Threat Detection**
- **Suspicious Port Analysis** - Detect unusual network connections
- **RF Pattern Recognition** - Identify malicious RF activities
- **Data Exfiltration Detection** - Monitor large data transfers
- **Real-time Alerting** - Immediate threat notifications

### **Privacy Protection**
- **Local Data Processing** - No cloud dependencies
- **Encrypted Storage** - Secure local data storage
- **Access Control** - Role-based permissions
- **Audit Logging** - Comprehensive activity tracking

---

## 🧪 **Testing & Validation**

### **Hardware Testing**
- **HackRF One Validation** - RF capture functionality
- **Phone Integration** - Network monitoring accuracy
- **Performance Testing** - Memory usage optimization
- **Stability Testing** - Long-running capture sessions

### **Security Testing**
- **Penetration Testing** - Vulnerability assessment
- **Threat Simulation** - Malware detection testing
- **Performance Impact** - Device resource usage
- **Privacy Validation** - Data handling compliance

---

## 📈 **Roadmap**

### **Phase 1: Core Platform** ✅
- [x] Live RF capture integration
- [x] Network packet monitoring
- [x] Android simulator development
- [x] Basic threat detection

### **Phase 2: Mobile App** 🔄
- [ ] React Native application
- [ ] Bluetooth 2FA system
- [ ] Enterprise dashboard
- [ ] Cloud integration

### **Phase 3: Hardware** 🔮
- [ ] Phone case security device
- [ ] NFC integration
- [ ] Wireless charging interface
- [ ] Proprietary security protocols

---

## 🤝 **Contributing**

### **Development Guidelines**
- Follow Python PEP 8 style guide
- Use TypeScript for React Native components
- Implement comprehensive error handling
- Write unit tests for all features
- Document all public APIs

### **Security Guidelines**
- Never commit API keys or secrets
- Use secure coding practices
- Validate all user inputs
- Implement proper access controls
- Follow OWASP mobile security guidelines

---

## 📄 **License**

**Proprietary Software - AIMF LLC**

This software contains proprietary technology and trade secrets. Unauthorized reproduction, distribution, or reverse engineering is strictly prohibited.

---

## 📞 **Support & Contact**

**AIMF LLC - Advanced Intelligence & Mobile Forensics**
- **Technical Support**: [Contact Information]
- **Documentation**: [Documentation Portal]
- **Issue Tracking**: GitHub Issues
- **Security Reports**: [Security Contact]

---

## 🔄 **Version History**

### **v1.0.0** - Current Development
- Live HackRF One RF capture integration
- Phone network monitoring (IP-based)
- Memory-optimized Android simulator
- Dual live capture (RF + Network)
- Professional dark-themed UI
- Real-time threat detection engine

---

**Built with ❤️ by AIMF LLC - Securing the Mobile Future**
>>>>>>> 659e5f2b1a93d5e4621f6f8c9567432aaa22cf14
