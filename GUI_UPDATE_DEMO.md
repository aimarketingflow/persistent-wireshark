# 🦈 StealthShark GUI Update Prompt Demo

## Overview
StealthShark now features an integrated auto-update system with PyQt6 GUI notifications. This document demonstrates the update flow and shows how the system works.

## Update Check Flow

### 1. Automatic Check on Startup
When the GUI launches (`wireshark_monitor_gui.py`), it automatically checks for updates after 1 second:

```python
# Check for updates 1 second after startup
QTimer.singleShot(1000, self.check_for_updates)
```

### 2. Update Detection
The system runs `check_updates.py --check` in the background to:
- Query GitHub API for latest commits
- Compare local version with remote
- Return update status

### 3. Update Dialog Display
If an update is available, a dark-themed PyQt6 dialog appears showing:

```
╔══════════════════════════════════════════╗
║         🦈 Update Available!             ║
╠══════════════════════════════════════════╣
║                                          ║
║  Current Version: v1.2.0                 ║
║  Latest Version:  v1.3.0                 ║
║                                          ║
║  New features available:                 ║
║  • Enhanced memory monitoring            ║
║  • Better error handling                 ║
║  • Improved capture stability            ║
║                                          ║
║  ┌──────────────┐  ┌─────────────────┐  ║
║  │Install Update│  │Remind Me Later  │  ║
║  └──────────────┘  └─────────────────┘  ║
╚══════════════════════════════════════════╝
```

## Features Implemented

### UpdateDialog Class
- **Location**: `wireshark_monitor_gui.py` lines 26-150
- **Theme**: Dark mode matching StealthShark UI
- **Buttons**: Install Update / Remind Me Later
- **Display**: Version info and update message

### Integration Points
1. **CLI Launcher** (`launch_cli.command`)
   - Runs user registration check
   - Checks for updates before starting monitor

2. **GUI Launcher** (`launch_gui.command`)
   - Runs user registration check
   - GUI auto-checks for updates on startup

3. **Health Monitor** (`health_check.py`)
   - Periodic update checks if auto-update enabled

## Update Installation Process

When user clicks "Install Update":

1. **Backup Creation**
   ```bash
   Creates backup in backups/backup_YYYYMMDD_HHMMSS/
   - stealthshark_settings.json
   - memory_config.json
   - com.stealthshark.monitor.plist
   ```

2. **Git Pull**
   ```bash
   git pull origin main
   ```

3. **Dependency Update**
   ```bash
   pip3 install -r requirements.txt --break-system-packages
   ```

4. **Application Restart**
   - GUI closes and relaunches with new version

## Testing the Feature

### Method 1: Simulate Update Available
```bash
# Reset to older commit
git reset --hard HEAD~5

# Launch GUI - will detect update
./launch_gui.command
```

### Method 2: Force Update Check
```bash
# Check for updates manually
python3 check_updates.py --check

# Force update installation
python3 check_updates.py --force
```

## Configuration

Settings in `stealthshark_settings.json`:
```json
{
  "auto_update": {
    "enabled": true,
    "check_on_startup": true,
    "check_interval_days": 7,
    "last_check": "2025-08-31T15:00:00"
  }
}
```

## Code Implementation

### Update Check Function (wireshark_monitor_gui.py)
```python
def check_for_updates(self):
    """Check for updates using the check_updates script"""
    try:
        result = subprocess.run(
            ['python3', 'check_updates.py', '--check'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout:
            try:
                update_info = json.loads(result.stdout)
                if update_info.get('update_available'):
                    # Show update dialog
                    dialog = UpdateDialog(
                        current_version=update_info.get('current_version', 'Unknown'),
                        latest_version=update_info.get('latest_version', 'Unknown'),
                        update_message=update_info.get('message', '')
                    )
                    
                    if dialog.exec():
                        self.install_update()
```

## Screenshots Simulation

### Normal Operation
```
🦈 StealthShark Network Monitor
================================
Status: Monitoring active
Interfaces: lo0, en0, en1
Duration: 5 hours per rotation
[No update notifications]
```

### With Update Available
```
🦈 StealthShark Network Monitor
================================
🔔 Update notification appears
   automatically after startup
   
[Update Dialog shown above]
```

## Benefits

1. **Non-Intrusive**: Checks happen in background
2. **User Control**: Can defer updates
3. **Safe Updates**: Automatic backups before changes
4. **Privacy Focused**: No user data sent
5. **Seamless Integration**: Matches UI theme

## Summary

The GUI update prompt system provides:
- ✅ Automatic update detection on startup
- ✅ Beautiful dark-themed notification dialog
- ✅ One-click update installation
- ✅ Backup safety measures
- ✅ User control over update timing
- ✅ Integration with CLI and GUI launchers

This ensures users always have access to the latest features and security fixes while maintaining full control over when updates are applied.
