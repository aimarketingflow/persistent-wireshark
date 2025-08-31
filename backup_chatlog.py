#!/usr/bin/env python3
"""
StealthShark Chat Log Backup
Automatically backs up conversation logs with timestamps
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

def backup_chatlog(conversation_name="stealthshark_hardening"):
    """Create timestamped backup of current conversation"""
    
    # Create chatlogs directory if it doesn't exist
    chatlog_dir = Path(__file__).parent / "StealthShark_chatlogs"
    chatlog_dir.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    backup_filename = f"{conversation_name}_{timestamp}.md"
    backup_path = chatlog_dir / backup_filename
    
    # Create backup content
    content = f"""# StealthShark Hardening Session - {timestamp}

## Session Summary
Enhanced StealthShark with persistent settings and automation features for daily use.

## Features Added

### 1. Persistent Settings Configuration (`stealthshark_settings.json`)
- Stores all configuration preferences
- Auto-start settings (duration, monitor type, interfaces)
- Monitoring limits (memory, disk, cleanup thresholds)
- Health check intervals and recovery options
- Maintenance schedules

### 2. Settings Manager (`configure_settings.py`)
- Interactive CLI for configuration
- Quick setup wizard for first-time users
- Load/save persistent settings
- Command-line options:
  - `python3 configure_settings.py` - Interactive menu
  - `python3 configure_settings.py --quick` - Quick setup wizard
  - `python3 configure_settings.py --show` - Display current settings
  - `python3 configure_settings.py --reset` - Reset to defaults

### 3. Enhanced Auto-Start Installer
- Automatically loads saved settings
- Falls back to manual configuration if no settings exist
- Prompts to use saved settings or configure new ones

### 4. Health Check Monitor (`health_check.py`)
- Monitors process health
- Checks disk space and performs cleanup
- Detects hung processes and restarts them
- Verifies tshark is capturing
- Command-line options:
  - `python3 health_check.py` - Continuous monitoring
  - `python3 health_check.py --once` - Single health check
  - `python3 health_check.py --cleanup` - Manual cleanup

## Usage Workflow

1. **First-Time Setup:**
   ```bash
   python3 configure_settings.py --quick
   ```

2. **Install Auto-Start with Saved Settings:**
   ```bash
   ./install_autostart.sh
   ```

3. **Monitor Health (Optional):**
   ```bash
   python3 health_check.py
   ```

## Key Configuration Options

- **Duration**: Set capture rotation period (1-24 hours)
- **Monitor Type**: Enhanced (recommended), Simple, or GUI
- **Interfaces**: Network interfaces to monitor
- **Memory Limit**: Maximum RAM usage before cleanup
- **Disk Limit**: Maximum disk usage for captures
- **Cleanup Age**: Delete captures older than X days
- **Health Checks**: Auto-restart hung processes

## Files Created/Modified
- `stealthshark_settings.json` - Persistent configuration
- `configure_settings.py` - Settings management tool
- `health_check.py` - Health monitoring and recovery
- `backup_chatlog.py` - Chat log backup utility
- `install_autostart.sh` - Updated to use saved settings

## Testing Commands
```bash
# Configure settings
python3 configure_settings.py --quick

# View current settings
python3 configure_settings.py --show

# Test health check
python3 health_check.py --once

# Install with saved settings
./install_autostart.sh
```

## Next Steps
- Test auto-start on actual boot
- Monitor logs for any issues
- Adjust settings based on system performance
- Consider adding email/Slack notifications
"""
    
    # Write backup file
    with open(backup_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Chat log backed up to: {backup_path}")
    return backup_path

if __name__ == "__main__":
    backup_chatlog()
