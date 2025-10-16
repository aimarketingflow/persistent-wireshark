# 🦈 StealthShark Launch Instructions

## ✅ Status: Successfully Tested & Working!

StealthShark has been successfully launched and tested. The Multi-Interface Network Monitor is working correctly and monitoring your network interfaces.

---

## 🚀 Quick Launch Options

### Option 1: Desktop Shortcut (Recommended)
**Double-click the `StealthShark.app` icon on your Desktop**

The desktop shortcut has been created at:
- **Location**: `~/Desktop/StealthShark.app`
- **Function**: Launches the Multi-Interface Shark GUI
- **Python**: Uses `/opt/homebrew/bin/python3.13` with all dependencies

### Option 2: Command Line Launcher
```bash
cd ~/Documents/Stealthshark2
./launch_stealthshark_gui.command
```

### Option 3: Direct Python Launch
```bash
cd ~/Documents/Stealthshark2
/opt/homebrew/bin/python3.13 multi_interface_shark_gui.py
```

### Option 4: Interactive Menu
```bash
cd ~/Documents/Stealthshark2
./StealthShark.command
```
This opens an interactive menu with multiple monitoring options.

---

## 📊 What's Currently Running

The Multi-Interface Shark GUI is actively monitoring:
- **24 network interfaces** discovered
- **Primary interfaces**: en0 (WiFi), lo0 (localhost)
- **Real-time packet capture** and statistics
- **Session state** auto-saved every 30 seconds
- **Monitoring duration**: 6 hours (configurable)

---

## 🔧 Dependencies Installed

All required dependencies have been installed:
- ✅ **PyQt6** (6.9.1) - GUI framework
- ✅ **psutil** (7.1.0) - System monitoring
- ✅ **requests** (2.32.5) - HTTP library
- ✅ **Python 3.13** via Homebrew

---

## 📁 Important Directories

- **Logs**: `~/Documents/Stealthshark2/gui_logs/`
- **Captures**: `~/Documents/Stealthshark2/pcap_captures/`
- **Settings**: `~/Documents/Stealthshark2/stealthshark_settings.json`
- **Session State**: `~/Documents/Stealthshark2/gui_logs/session_state.json`

---

## 🎯 Features Available

1. **Multi-Interface Monitoring** - Monitor all network interfaces simultaneously
2. **Real-time Statistics** - Live packet counts and bandwidth usage
3. **Pattern Recognition** - Automatic detection of network patterns
4. **Session Recovery** - Automatic state restoration after crashes
5. **WiFi Threat Detection** - Scan for suspicious networks
6. **Packet Capture** - Save network traffic to PCAP files

---

## 🛠️ Troubleshooting

### If the GUI doesn't appear:
1. Check if it's already running: `ps aux | grep multi_interface_shark_gui`
2. Kill existing process: `pkill -f multi_interface_shark_gui`
3. Check logs: `tail -f ~/Documents/Stealthshark2/gui_logs/multi_interface_gui_*.log`

### If you get permission errors:
Some features require elevated permissions for packet capture. Run with sudo if needed:
```bash
sudo /opt/homebrew/bin/python3.13 multi_interface_shark_gui.py
```

---

## 📝 Notes

- The application uses **Homebrew Python 3.13** with system-wide packages
- Dependencies were installed with `--break-system-packages` flag
- The desktop shortcut is a proper macOS `.app` bundle
- Logs are automatically created in `gui_logs/` directory
- Session state is preserved between launches

---

## 🔄 Next Steps

To stop the current monitoring session:
1. Close the GUI window, or
2. Use: `pkill -f multi_interface_shark_gui`

To restart:
- Double-click the desktop shortcut, or
- Run any of the launch commands above

---

**Built with ❤️ for network security professionals**

*Last updated: 2025-10-04*
