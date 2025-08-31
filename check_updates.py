#!/usr/bin/env python3
"""
StealthShark Auto-Update Checker
Checks GitHub repository for updates and optionally installs them
"""

import json
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path
import requests
from typing import Dict, Any, Optional

class UpdateChecker:
    """Check and install updates from GitHub"""
    
    def __init__(self):
        self.repo_url = "https://github.com/aimarketingflow/persistent-wireshark"
        self.api_url = "https://api.github.com/repos/aimarketingflow/persistent-wireshark"
        self.settings_file = Path(__file__).parent / "stealthshark_settings.json"
        self.update_log = Path(__file__).parent / "logs" / "updates.log"
        self.update_log.parent.mkdir(exist_ok=True)
        
        # Load settings
        self.settings = self.load_settings()
        
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from JSON file"""
        if self.settings_file.exists():
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_settings(self):
        """Save settings to JSON file"""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)
    
    def get_local_version(self) -> Optional[str]:
        """Get the current local git commit hash"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            print(f"Error getting local version: {e}")
        return None
    
    def get_remote_version(self) -> Optional[Dict[str, Any]]:
        """Get the latest commit from GitHub"""
        try:
            # Try to get latest commit info from GitHub API
            response = requests.get(
                f"{self.api_url}/commits/main",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    'sha': data['sha'],
                    'message': data['commit']['message'].split('\n')[0],
                    'date': data['commit']['committer']['date'],
                    'author': data['commit']['author']['name']
                }
        except requests.exceptions.RequestException as e:
            # Fallback to git ls-remote
            try:
                result = subprocess.run(
                    ['git', 'ls-remote', self.repo_url, 'HEAD'],
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).parent
                )
                if result.returncode == 0:
                    sha = result.stdout.split()[0]
                    return {'sha': sha, 'message': 'Unknown', 'date': 'Unknown'}
            except Exception:
                pass
        except Exception as e:
            print(f"Error checking remote version: {e}")
        return None
    
    def check_for_updates(self, silent=False) -> bool:
        """Check if updates are available"""
        local_version = self.get_local_version()
        remote_info = self.get_remote_version()
        
        if not local_version or not remote_info:
            if not silent:
                print("⚠️  Unable to check for updates")
            return False
        
        remote_version = remote_info['sha']
        
        if local_version[:8] == remote_version[:8]:
            if not silent:
                print("✅ StealthShark is up to date!")
                print(f"   Current version: {local_version[:8]}")
            return False
        else:
            if not silent:
                print("\n🔄 Update available!")
                print(f"   Current version: {local_version[:8]}")
                print(f"   Latest version:  {remote_version[:8]}")
                if remote_info.get('message'):
                    print(f"   Latest commit:   {remote_info['message']}")
            return True
    
    def backup_current_version(self):
        """Create a backup of current configuration before updating"""
        backup_dir = Path(__file__).parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        
        # Backup important files
        files_to_backup = [
            "stealthshark_settings.json",
            "memory_config.json",
            "com.stealthshark.monitor.plist"
        ]
        
        for file in files_to_backup:
            source = Path(__file__).parent / file
            if source.exists():
                dest = backup_dir / backup_name / file
                dest.parent.mkdir(exist_ok=True, parents=True)
                
                import shutil
                shutil.copy2(source, dest)
        
        print(f"✅ Backup created: {backup_dir / backup_name}")
        return backup_dir / backup_name
    
    def install_update(self) -> bool:
        """Install the available update"""
        try:
            print("\n📦 Installing update...")
            
            # Create backup first
            backup_path = self.backup_current_version()
            
            # Stash any local changes
            print("   Stashing local changes...")
            subprocess.run(
                ['git', 'stash'],
                cwd=Path(__file__).parent,
                capture_output=True
            )
            
            # Pull latest changes
            print("   Pulling latest changes from GitHub...")
            result = subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                cwd=Path(__file__).parent,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ Update failed: {result.stderr}")
                
                # Try to restore from stash
                subprocess.run(
                    ['git', 'stash', 'pop'],
                    cwd=Path(__file__).parent,
                    capture_output=True
                )
                return False
            
            # Restore stashed changes if any
            stash_result = subprocess.run(
                ['git', 'stash', 'list'],
                cwd=Path(__file__).parent,
                capture_output=True,
                text=True
            )
            
            if stash_result.stdout:
                print("   Restoring local changes...")
                subprocess.run(
                    ['git', 'stash', 'pop'],
                    cwd=Path(__file__).parent,
                    capture_output=True
                )
            
            # Update dependencies if requirements.txt changed
            req_file = Path(__file__).parent / "requirements.txt"
            if req_file.exists():
                print("   Updating dependencies...")
                subprocess.run(
                    ['pip3', 'install', '-r', 'requirements.txt', '--quiet'],
                    cwd=Path(__file__).parent
                )
            
            # Log the update
            with open(self.update_log, 'a') as f:
                f.write(f"{datetime.now().isoformat()} - Updated successfully\n")
            
            print("\n✅ Update installed successfully!")
            print(f"   Backup saved to: {backup_path}")
            
            # Update last check time
            if 'maintenance' not in self.settings:
                self.settings['maintenance'] = {}
            self.settings['maintenance']['last_update_check'] = datetime.now().isoformat()
            self.save_settings()
            
            return True
            
        except Exception as e:
            print(f"❌ Update failed: {e}")
            return False
    
    def auto_update_check(self) -> bool:
        """Check for updates based on settings preferences"""
        if not self.settings.get('maintenance', {}).get('auto_update_check', False):
            return False
        
        # Check last update time
        last_check = self.settings.get('maintenance', {}).get('last_update_check')
        if last_check:
            last_check_date = datetime.fromisoformat(last_check)
            days_since = (datetime.now() - last_check_date).days
            
            # Check weekly by default
            check_interval = self.settings.get('maintenance', {}).get('update_check_days', 7)
            if days_since < check_interval:
                return False
        
        print("\n🔍 Checking for StealthShark updates...")
        has_updates = self.check_for_updates(silent=False)
        
        # Update last check time
        if 'maintenance' not in self.settings:
            self.settings['maintenance'] = {}
        self.settings['maintenance']['last_update_check'] = datetime.now().isoformat()
        self.save_settings()
        
        return has_updates
    
    def interactive_update(self):
        """Interactive update process"""
        print("\n🦈 StealthShark Update Manager")
        print("=" * 40)
        
        # Check for updates
        if self.check_for_updates():
            print("\nWould you like to install the update?")
            print("Your settings will be backed up automatically.")
            
            response = input("\nInstall update? (y/n) [n]: ").lower()
            if response in ['y', 'yes']:
                if self.install_update():
                    print("\n🎉 Update complete!")
                    print("Please restart StealthShark to use the new version.")
                    
                    # Ask about auto-updates
                    if not self.settings.get('maintenance', {}).get('auto_update_check', False):
                        enable = input("\nEnable automatic update checks? (y/n) [y]: ").lower()
                        if enable != 'n':
                            if 'maintenance' not in self.settings:
                                self.settings['maintenance'] = {}
                            self.settings['maintenance']['auto_update_check'] = True
                            self.save_settings()
                            print("✅ Automatic update checks enabled")
            else:
                print("Update skipped. You can update anytime by running this script.")
        else:
            # Ask about enabling auto-checks if not enabled
            if not self.settings.get('maintenance', {}).get('auto_update_check', False):
                print("\nWould you like to enable automatic update checks?")
                enable = input("Enable auto-checks? (y/n) [y]: ").lower()
                if enable != 'n':
                    if 'maintenance' not in self.settings:
                        self.settings['maintenance'] = {}
                    self.settings['maintenance']['auto_update_check'] = True
                    self.save_settings()
                    print("✅ Automatic update checks enabled")

def main():
    """Main entry point"""
    checker = UpdateChecker()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--check":
            # Just check for updates
            has_updates = checker.check_for_updates()
            sys.exit(0 if not has_updates else 1)
        elif sys.argv[1] == "--auto":
            # Automatic update (no prompts)
            if checker.check_for_updates(silent=True):
                checker.install_update()
        elif sys.argv[1] == "--force":
            # Force update even if up to date
            print("Forcing update...")
            checker.install_update()
        else:
            print("Usage: python3 check_updates.py [--check|--auto|--force]")
    else:
        # Interactive mode
        checker.interactive_update()

if __name__ == "__main__":
    main()
