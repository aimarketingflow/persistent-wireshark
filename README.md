# LoopbackShark 🦈
**Advanced Localhost Traffic Monitor with Pattern Recognition**

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](https://opensource.org/licenses/GPL-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform: macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)

## 🎯 Overview

LoopbackShark is a specialized network monitoring application designed specifically for capturing, analyzing, and visualizing loopback interface traffic patterns. It provides real-time monitoring of localhost communications with advanced pattern recognition capabilities.

### 🔥 Key Features

- **🎯 Pattern Recognition** - Automatic detection of web servers, databases, APIs
- **📊 Real-time Analysis** - Live monitoring with PyQt6 GUI and dark theme
- **🔍 Application Detection** - Identifies Redis, MySQL, HTTP servers, Node.js, and more
- **📈 Historical Analysis** - Trend analysis from captured data
- **⚙️ Smart Configuration** - Persistent settings with 24-hour default monitoring
- **🖥️ Desktop Integration** - Easy access via command launcher
- **🔌 All Ports Monitoring** - Smart port filtering with toggle functionality
- **📋 Comprehensive Reporting** - JSON and Markdown output formats

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
git clone https://github.com/aimarketingflow/persistent-wireshark.git
cd persistent-wireshark
python3 -m venv venv_loopbackshark
source venv_loopbackshark/bin/activate
pip3 install -r requirements_loopbackshark.txt
```

### Launch Options

**🖥️ GUI Application (Recommended)**
```bash
./LoopbackShark.command
```

**⚡ Command Line Interface**
```bash
python3 cli_loopbackshark.py --duration 3600 --debug
```

**🧪 Test Pattern Recognition**
```bash
python3 test_traffic_generator.py
```

## 📊 Features Overview

### Pattern Recognition Engine
- **Automatic Application Detection**: Identifies common localhost applications
- **Port Analysis**: Recognizes development servers, databases, and APIs  
- **Confidence Scoring**: Advanced pattern matching with reliability metrics
- **Real-time Updates**: Live pattern detection during monitoring

### GUI Dashboard
- **Live Monitor Tab**: Real-time packet capture and analysis
- **Trend Analysis Tab**: Historical traffic patterns and statistics
- **Statistics Tab**: Port usage, application detection metrics
- **Pattern Recognition Tab**: Live application detection with confidence scores

### Smart Configuration
- **Persistent Settings**: Automatically saves capture directory and duration
- **24-Hour Default**: Optimized for continuous development monitoring
- **All Ports Mode**: Monitor all localhost traffic or filter specific ports
- **Auto-detection**: Intelligent path resolution for cross-platform compatibility

## 🔧 Configuration

### Settings File
LoopbackShark automatically creates `loopbackshark_settings.json`:

```json
{
  "capture_directory": "./pcap_captures",
  "monitoring_duration": 86400,
  "port_filter": null,
  "all_ports_enabled": true
}
```

### Pattern Templates
Pre-built pattern recognition templates in `pattern_templates/`:
- `loopback_pattern_templates.json` - Comprehensive application signatures
- `simple_port_patterns.json` - Basic port-to-application mappings

## 📁 Project Structure

```
LoopbackShark/
├── loopbackshark_gui.py           # Main GUI application
├── cli_loopbackshark.py           # Command line interface
├── loopback_monitor.py            # Core monitoring engine
├── pattern_recognition.py         # Advanced pattern detection
├── pattern_analyzer.py            # Historical pattern analysis
├── test_traffic_generator.py      # Testing and validation
├── LoopbackShark.command          # Desktop launcher
├── requirements_loopbackshark.txt # Python dependencies
├── pattern_templates/             # Pre-built patterns
├── pcap_captures/                 # Capture file storage
├── analysis_results/              # Output reports
└── LoopbackShark_Terminal_Guide/  # Comprehensive documentation
```

## 🎮 Usage Examples

### Basic Monitoring
```bash
# Monitor for 1 hour with pattern recognition
python3 cli_loopbackshark.py --duration 3600 --patterns

# Monitor specific ports only
python3 cli_loopbackshark.py --ports 3000,8080,5432

# Debug mode with verbose logging
python3 cli_loopbackshark.py --debug --duration 300
```

### Advanced Features
```bash
# Generate test traffic for validation
python3 test_traffic_generator.py

# Extract patterns from historical data
python3 quick_pattern_extractor.py

# Analyze historical captures
python3 pattern_analyzer.py
```

## 📈 Output Formats

### Analysis Reports
- **JSON Format**: Machine-readable analysis results
- **Markdown Summary**: Human-readable traffic reports
- **Pattern Analysis**: Application detection results with confidence scores

### Sample Output
```json
{
  "session_info": {
    "session_id": "20250908_135520",
    "duration": 3600,
    "packets_analyzed": 1247
  },
  "pattern_recognition": {
    "detected_applications": [
      {"app": "Node.js Server", "port": 3000, "confidence": 0.95},
      {"app": "Redis", "port": 6379, "confidence": 0.88}
    ],
    "detection_rate": 0.73
  }
}
```

## 🔍 Pattern Recognition

LoopbackShark includes advanced pattern recognition for:

**Development Servers:**
- Node.js, Flask, Django development servers
- React, Vue.js dev servers
- Static file servers

**Databases:**
- MySQL, PostgreSQL, MongoDB
- Redis, Memcached
- SQLite connections

**APIs & Services:**
- REST APIs, GraphQL endpoints
- Microservices communication
- Docker container networking

## 🛠️ Development

### Running Tests
```bash
python3 -m pytest tests/
```

### Building Documentation
```bash
cd LoopbackShark_Terminal_Guide/
python3 -m http.server 8000
```

## 📞 Support & Contributing

- **Issues**: [GitHub Issues](https://github.com/aimarketingflow/persistent-wireshark/issues)
- **Documentation**: See `LoopbackShark_Terminal_Guide/` directory
- **Contributing**: Pull requests welcome!

## 📄 License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

---

**Built for developers, by developers** 🚀

*LoopbackShark - Advanced localhost monitoring for modern development workflows.*
