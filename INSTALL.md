# StealthShark Installation Guide

## Prerequisites

### System Requirements
- **macOS 10.15+** or **Linux** (Ubuntu 18.04+)
- **Python 3.8+**
- **Wireshark/TShark** installed
- **Network interface access** (may require admin setup)

### Install Wireshark/TShark

#### macOS (Homebrew)
```bash
brew install wireshark
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install tshark wireshark-common
```

## Quick Start

### Option 1: Desktop Launchers (Recommended)
1. **Download** or clone StealthShark to your desired location
2. **Double-click** `launch_gui.command` for GUI interface
3. **Double-click** `launch_cli.command` for command-line interface

The launchers will automatically:
- Create a Python virtual environment
- Install all dependencies
- Launch the appropriate interface

### Option 2: Manual Installation
```bash
# Clone or download StealthShark
cd /path/to/StealthShark

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run StealthShark
python3 enhanced_memory_monitor.py        # Enhanced monitor
python3 gui_memory_monitor.py             # GUI interface
python3 simple_tshark_monitor.py en0      # Simple monitor
```

## Network Permissions Setup

### macOS BPF Permissions
For unprivileged packet capture on macOS:

1. **Create BPF access group:**
```bash
sudo dseditgroup -o create -q access_bpf
sudo dseditgroup -o edit -a $(whoami) -t user access_bpf
```

2. **Create startup script** (`/Library/StartupItems/ChmodBPF/ChmodBPF`):
```bash
#!/bin/bash
chgrp access_bpf /dev/bpf*
chmod g+rw /dev/bpf*
```

3. **Make executable and reboot:**
```bash
sudo chmod +x /Library/StartupItems/ChmodBPF/ChmodBPF
sudo reboot
```

### Linux Capabilities
```bash
# Allow non-root packet capture
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap
```

## Configuration

### Default Settings
StealthShark uses sensible defaults but can be customized:

- **Memory limit:** 8 GB
- **Disk limit:** 50 GB  
- **Cleanup threshold:** 80%
- **Check interval:** 30 seconds
- **File rotation:** 4 hours per file

### Custom Configuration
Create `config.json` in the StealthShark directory:
```json
{
    "max_memory_gb": 16,
    "max_disk_gb": 100,
    "cleanup_threshold": 0.85,
    "check_interval_seconds": 60,
    "interfaces": ["en0", "en1", "awdl0"],
    "stealth_mode": true,
    "compress_old_files": true
}
```

## Usage Examples

### Basic Monitoring
```bash
# Monitor default interface with GUI
python3 gui_memory_monitor.py

# Monitor specific interfaces
python3 simple_tshark_monitor.py en0 en1

# Enhanced monitoring with memory management
python3 enhanced_memory_monitor.py
```

### Stealth Mode
```bash
# Processes will be disguised as system processes
python3 enhanced_memory_monitor.py --stealth
```

### Background Operation
```bash
# Run in background with logging
nohup python3 enhanced_memory_monitor.py > monitor.log 2>&1 &
```

## Troubleshooting

### Common Issues

**Permission Denied:**
- Ensure BPF permissions are set up (macOS)
- Check user has network capture capabilities (Linux)
- Try running with `sudo` for initial testing

**Interface Not Found:**
```bash
# List available interfaces
tshark -D

# Use correct interface name
python3 simple_tshark_monitor.py en0  # Not eth0 on macOS
```

**PyQt6 GUI Issues:**
```bash
# Install PyQt6 separately if needed
pip install PyQt6

# Use CLI version if GUI has problems
python3 enhanced_memory_monitor.py
```

**High Memory Usage:**
- Reduce memory limits in configuration
- Enable automatic cleanup
- Use file compression

### Log Files
- **GUI logs:** Check system tray notifications
- **CLI logs:** `monitor.log` in StealthShark directory  
- **System logs:** `/var/log/system.log` (macOS) or `/var/log/syslog` (Linux)

## Security Considerations

### Stealth Operation
- Process names are disguised as system processes
- Capture files stored locally with configurable retention
- No network communication by default
- Minimal system footprint

### Data Protection
- Capture files contain network traffic data
- Ensure appropriate file permissions
- Consider encryption for sensitive environments
- Regular cleanup of old capture files

## Performance Tuning

### Memory Optimization
- Adjust `max_memory_gb` based on system RAM
- Enable automatic cleanup at 80% threshold
- Use file compression for long-term storage

### Disk Management
- Set appropriate `max_disk_gb` limits
- Enable automatic file rotation
- Monitor disk usage regularly

### Network Interfaces
- Monitor only necessary interfaces
- Use specific BPF filters to reduce capture volume
- Consider interface bonding for high-traffic environments

## Support

For issues, questions, or contributions:
- Check the main README.md for project overview
- Review log files for error details
- Ensure all prerequisites are properly installed
- Test with simple interface monitoring first

## Next Steps

After installation:
1. **Test basic functionality** with simple monitor
2. **Configure network permissions** for your environment  
3. **Customize settings** in config.json
4. **Set up monitoring** on your target interfaces
5. **Enable stealth mode** for production use
