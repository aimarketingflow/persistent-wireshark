#!/usr/bin/env python3
"""
StealthShark Settings Configuration Tool
Configure and manage persistent settings for automated monitoring
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

class SettingsManager:
    """Manage StealthShark persistent settings"""
    
    def __init__(self):
        self.settings_file = Path(__file__).parent / "stealthshark_settings.json"
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from JSON file"""
        if self.settings_file.exists():
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        return self.get_default_settings()
    
    def save_settings(self):
        """Save settings to JSON file"""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)
        print(f"✅ Settings saved to {self.settings_file}")
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default settings structure"""
        return {
            "autostart": {
                "enabled": False,
                "monitor_type": "enhanced",
                "duration_hours": 4,
                "interfaces": ["en0"],
                "start_on_boot": True,
                "restart_on_crash": True,
                "max_retries": 5
            },
            "monitoring": {
                "rotation_hours": 4,
                "max_memory_gb": 8,
                "max_disk_gb": 50,
                "cleanup_threshold": 0.8,
                "compression_enabled": True,
                "auto_cleanup": True,
                "capture_filter": "",
                "output_directory": "captures",
                "log_level": "INFO"
            },
            "notifications": {
                "enabled": False,
                "on_error": True,
                "on_disk_full": True,
                "on_memory_high": True
            },
            "maintenance": {
                "auto_update_check": False,
                "cleanup_age_days": 7,
                "compress_after_hours": 24
            },
            "health_check": {
                "enabled": True,
                "interval_minutes": 30,
                "restart_if_hung": True,
                "alert_on_failure": True
            }
        }
    
    def configure_autostart(self):
        """Configure auto-start settings"""
        print("\n🚀 Auto-Start Configuration")
        print("-" * 40)
        
        # Enable/disable autostart
        enabled = input(f"Enable auto-start on boot? (y/n) [{'y' if self.settings['autostart']['enabled'] else 'n'}]: ").lower()
        if enabled in ['y', 'yes', '']:
            self.settings['autostart']['enabled'] = self.settings['autostart'].get('enabled', True)
        elif enabled in ['n', 'no']:
            self.settings['autostart']['enabled'] = False
        
        # Monitor type
        print("\nMonitor Types:")
        print("1. Enhanced Memory Monitor (recommended)")
        print("2. Simple TShark Monitor")
        print("3. GUI Monitor")
        current = {"enhanced": 1, "simple": 2, "gui": 3}.get(self.settings['autostart']['monitor_type'], 1)
        choice = input(f"Select monitor type (1-3) [{current}]: ") or str(current)
        
        monitor_types = {"1": "enhanced", "2": "simple", "3": "gui"}
        self.settings['autostart']['monitor_type'] = monitor_types.get(choice, "enhanced")
        
        # Duration
        current_duration = self.settings['autostart']['duration_hours']
        duration = input(f"Capture rotation duration in hours [{current_duration}]: ")
        if duration:
            try:
                self.settings['autostart']['duration_hours'] = float(duration)
            except ValueError:
                print("⚠️ Invalid duration, keeping current value")
        
        # Interfaces
        current_interfaces = ", ".join(self.settings['autostart']['interfaces'])
        interfaces = input(f"Network interfaces to monitor (comma-separated) [{current_interfaces}]: ")
        if interfaces:
            self.settings['autostart']['interfaces'] = [i.strip() for i in interfaces.split(',')]
    
    def configure_monitoring(self):
        """Configure monitoring settings"""
        print("\n📊 Monitoring Configuration")
        print("-" * 40)
        
        # Memory limit
        current_mem = self.settings['monitoring']['max_memory_gb']
        memory = input(f"Maximum memory usage (GB) [{current_mem}]: ")
        if memory:
            try:
                self.settings['monitoring']['max_memory_gb'] = int(memory)
            except ValueError:
                print("⚠️ Invalid memory value, keeping current")
        
        # Disk limit
        current_disk = self.settings['monitoring']['max_disk_gb']
        disk = input(f"Maximum disk usage (GB) [{current_disk}]: ")
        if disk:
            try:
                self.settings['monitoring']['max_disk_gb'] = int(disk)
            except ValueError:
                print("⚠️ Invalid disk value, keeping current")
        
        # Cleanup threshold
        current_threshold = self.settings['monitoring']['cleanup_threshold']
        threshold = input(f"Cleanup threshold (0.1-0.95) [{current_threshold}]: ")
        if threshold:
            try:
                val = float(threshold)
                if 0.1 <= val <= 0.95:
                    self.settings['monitoring']['cleanup_threshold'] = val
            except ValueError:
                print("⚠️ Invalid threshold, keeping current")
        
        # Compression
        compress = input(f"Enable compression? (y/n) [{'y' if self.settings['monitoring']['compression_enabled'] else 'n'}]: ").lower()
        if compress in ['y', 'yes']:
            self.settings['monitoring']['compression_enabled'] = True
        elif compress in ['n', 'no']:
            self.settings['monitoring']['compression_enabled'] = False
        
        # Capture filter
        current_filter = self.settings['monitoring'].get('capture_filter', '')
        print(f"\nCurrent capture filter: '{current_filter}' (empty = capture all)")
        new_filter = input("Enter BPF filter (or press Enter to keep current): ")
        if new_filter or new_filter == '':
            self.settings['monitoring']['capture_filter'] = new_filter
    
    def configure_maintenance(self):
        """Configure maintenance settings"""
        print("\n🔧 Maintenance Configuration")
        print("-" * 40)
        
        # Cleanup age
        current_age = self.settings['maintenance']['cleanup_age_days']
        age = input(f"Delete captures older than (days) [{current_age}]: ")
        if age:
            try:
                self.settings['maintenance']['cleanup_age_days'] = int(age)
            except ValueError:
                print("⚠️ Invalid age, keeping current")
        
        # Compression age
        current_compress = self.settings['maintenance']['compress_after_hours']
        compress = input(f"Compress captures older than (hours) [{current_compress}]: ")
        if compress:
            try:
                self.settings['maintenance']['compress_after_hours'] = int(compress)
            except ValueError:
                print("⚠️ Invalid hours, keeping current")
    
    def configure_health(self):
        """Configure health check settings"""
        print("\n❤️ Health Check Configuration")
        print("-" * 40)
        
        # Enable health checks
        enabled = input(f"Enable health checks? (y/n) [{'y' if self.settings['health_check']['enabled'] else 'n'}]: ").lower()
        if enabled in ['y', 'yes']:
            self.settings['health_check']['enabled'] = True
        elif enabled in ['n', 'no']:
            self.settings['health_check']['enabled'] = False
        
        if self.settings['health_check']['enabled']:
            # Check interval
            current_interval = self.settings['health_check']['interval_minutes']
            interval = input(f"Health check interval (minutes) [{current_interval}]: ")
            if interval:
                try:
                    self.settings['health_check']['interval_minutes'] = int(interval)
                except ValueError:
                    print("⚠️ Invalid interval, keeping current")
            
            # Auto-restart
            restart = input(f"Auto-restart if hung? (y/n) [{'y' if self.settings['health_check']['restart_if_hung'] else 'n'}]: ").lower()
            if restart in ['y', 'yes']:
                self.settings['health_check']['restart_if_hung'] = True
            elif restart in ['n', 'no']:
                self.settings['health_check']['restart_if_hung'] = False
    
    def show_current_settings(self):
        """Display current settings"""
        print("\n📋 Current Settings")
        print("=" * 50)
        print(json.dumps(self.settings, indent=2))
        print("=" * 50)
    
    def quick_setup(self):
        """Quick setup wizard for first-time configuration"""
        print("\n🚀 StealthShark Quick Setup Wizard")
        print("=" * 50)
        print("This wizard will help you configure StealthShark for automated monitoring.")
        print("Press Enter to accept default values shown in brackets.\n")
        
        # Essential settings only
        # Duration
        duration = input("Capture rotation duration in hours [4]: ") or "4"
        self.settings['autostart']['duration_hours'] = float(duration)
        self.settings['monitoring']['rotation_hours'] = float(duration)
        
        # Monitor type
        print("\nMonitor type:")
        print("1. Enhanced (recommended - memory optimized)")
        print("2. Simple (lightweight)")
        print("3. GUI (visual interface)")
        choice = input("Select [1]: ") or "1"
        monitor_types = {"1": "enhanced", "2": "simple", "3": "gui"}
        self.settings['autostart']['monitor_type'] = monitor_types.get(choice, "enhanced")
        
        # Interfaces
        interfaces = input("Network interfaces (comma-separated) [en0]: ") or "en0"
        self.settings['autostart']['interfaces'] = [i.strip() for i in interfaces.split(',')]
        
        # Auto-start
        autostart = input("Enable auto-start on boot? (y/n) [y]: ").lower() or "y"
        self.settings['autostart']['enabled'] = autostart in ['y', 'yes']
        
        # Save
        self.save_settings()
        
        if self.settings['autostart']['enabled']:
            print("\n✅ Setup complete! Run './install_autostart.sh' to apply auto-start settings.")
        else:
            print("\n✅ Setup complete! Settings saved for manual operation.")
    
    def main_menu(self):
        """Interactive configuration menu"""
        while True:
            print("\n🦈 StealthShark Settings Manager")
            print("=" * 50)
            print("1. Quick Setup (Recommended for first time)")
            print("2. Configure Auto-Start")
            print("3. Configure Monitoring")
            print("4. Configure Maintenance")
            print("5. Configure Health Checks")
            print("6. Show Current Settings")
            print("7. Reset to Defaults")
            print("8. Save and Exit")
            print("9. Exit without Saving")
            
            choice = input("\nSelect option (1-9): ")
            
            if choice == '1':
                self.quick_setup()
            elif choice == '2':
                self.configure_autostart()
            elif choice == '3':
                self.configure_monitoring()
            elif choice == '4':
                self.configure_maintenance()
            elif choice == '5':
                self.configure_health()
            elif choice == '6':
                self.show_current_settings()
            elif choice == '7':
                if input("Reset all settings to defaults? (y/n): ").lower() == 'y':
                    self.settings = self.get_default_settings()
                    print("✅ Settings reset to defaults")
            elif choice == '8':
                self.save_settings()
                print("Settings saved. Exiting...")
                break
            elif choice == '9':
                print("Exiting without saving...")
                break

def main():
    """Main entry point"""
    manager = SettingsManager()
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            manager.quick_setup()
        elif sys.argv[1] == "--show":
            manager.show_current_settings()
        elif sys.argv[1] == "--reset":
            manager.settings = manager.get_default_settings()
            manager.save_settings()
            print("✅ Settings reset to defaults")
        else:
            print("Usage: python3 configure_settings.py [--quick|--show|--reset]")
    else:
        manager.main_menu()

if __name__ == "__main__":
    main()
