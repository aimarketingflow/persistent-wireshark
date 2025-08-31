#!/usr/bin/env python3
"""
StealthShark Health Check Monitor
Monitors the health of running StealthShark processes and performs recovery actions
"""

import json
import os
import sys
import time
import subprocess
import psutil
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, Any, Optional

class HealthMonitor:
    """Monitor and maintain StealthShark process health"""
    
    def __init__(self):
        self.settings_file = Path(__file__).parent / "stealthshark_settings.json"
        self.log_dir = Path(__file__).parent / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Set up logging
        log_file = self.log_dir / f"health_check_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load settings
        self.settings = self.load_settings()
        self.last_restart = {}
        self.failure_count = {}
        
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from JSON file"""
        if self.settings_file.exists():
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        return {}
    
    def find_stealthshark_processes(self) -> list:
        """Find all running StealthShark processes"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if any(script in cmdline for script in [
                    'simple_tshark_monitor.py',
                    'enhanced_memory_monitor.py',
                    'gui_memory_monitor.py',
                    'persistent_wireshark_monitor.py'
                ]):
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes
    
    def check_process_health(self, proc) -> Dict[str, Any]:
        """Check if a process is healthy"""
        try:
            # Get process info
            with proc.oneshot():
                cpu_percent = proc.cpu_percent(interval=1)
                memory_info = proc.memory_info()
                memory_gb = memory_info.rss / (1024 * 1024 * 1024)
                status = proc.status()
                runtime = time.time() - proc.create_time()
                
            # Check health criteria
            max_memory = self.settings.get('monitoring', {}).get('max_memory_gb', 8)
            is_hung = (status == psutil.STATUS_ZOMBIE or 
                      (cpu_percent < 0.1 and runtime > 300))  # No CPU for 5+ mins
            is_memory_high = memory_gb > max_memory
            
            return {
                'pid': proc.pid,
                'healthy': not (is_hung or is_memory_high),
                'cpu_percent': cpu_percent,
                'memory_gb': memory_gb,
                'status': status,
                'runtime_hours': runtime / 3600,
                'is_hung': is_hung,
                'is_memory_high': is_memory_high
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {'healthy': False, 'error': 'Process not accessible'}
    
    def check_tshark_running(self) -> bool:
        """Check if tshark is actually capturing"""
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'tshark.*-b duration'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Error checking tshark: {e}")
            return False
    
    def check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space"""
        captures_dir = Path(__file__).parent / "captures"
        if not captures_dir.exists():
            captures_dir.mkdir(exist_ok=True)
        
        stat = os.statvfs(captures_dir)
        total_gb = (stat.f_blocks * stat.f_frsize) / (1024 ** 3)
        free_gb = (stat.f_avail * stat.f_frsize) / (1024 ** 3)
        used_gb = total_gb - free_gb
        percent_used = (used_gb / total_gb) * 100 if total_gb > 0 else 0
        
        max_disk = self.settings.get('monitoring', {}).get('max_disk_gb', 50)
        cleanup_threshold = self.settings.get('monitoring', {}).get('cleanup_threshold', 0.8)
        
        return {
            'total_gb': total_gb,
            'free_gb': free_gb,
            'used_gb': used_gb,
            'percent_used': percent_used,
            'needs_cleanup': used_gb > (max_disk * cleanup_threshold),
            'critical': free_gb < 1  # Less than 1GB free
        }
    
    def cleanup_old_captures(self):
        """Clean up old capture files"""
        cleanup_age_days = self.settings.get('maintenance', {}).get('cleanup_age_days', 7)
        captures_dir = Path(__file__).parent / "captures"
        
        if not captures_dir.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=cleanup_age_days)
        deleted_count = 0
        freed_space = 0
        
        for pcap_file in captures_dir.glob("*.pcap*"):
            try:
                if datetime.fromtimestamp(pcap_file.stat().st_mtime) < cutoff_date:
                    file_size = pcap_file.stat().st_size
                    pcap_file.unlink()
                    deleted_count += 1
                    freed_space += file_size
                    self.logger.info(f"Deleted old capture: {pcap_file.name}")
            except Exception as e:
                self.logger.error(f"Error deleting {pcap_file}: {e}")
        
        if deleted_count > 0:
            self.logger.info(f"Cleaned up {deleted_count} files, freed {freed_space / (1024**3):.2f} GB")
    
    def restart_monitor(self):
        """Restart the StealthShark monitor"""
        try:
            # Check if we should restart
            if not self.settings.get('health_check', {}).get('restart_if_hung', True):
                self.logger.warning("Auto-restart disabled in settings")
                return False
            
            # Get monitor command from settings
            monitor_type = self.settings.get('autostart', {}).get('monitor_type', 'enhanced')
            duration = self.settings.get('autostart', {}).get('duration_hours', 4)
            interfaces = ' '.join(self.settings.get('autostart', {}).get('interfaces', ['en0']))
            
            # Build command based on monitor type
            if monitor_type == 'simple':
                cmd = f"python3 simple_tshark_monitor.py {interfaces} --duration {duration}"
            elif monitor_type == 'gui':
                cmd = f"python3 gui_memory_monitor.py --duration {duration}"
            else:
                cmd = f"python3 enhanced_memory_monitor.py --duration {duration}"
            
            # Start the monitor
            working_dir = Path(__file__).parent
            process = subprocess.Popen(
                cmd.split(),
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            self.logger.info(f"Restarted monitor with PID {process.pid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restart monitor: {e}")
            return False
    
    def run_health_check(self):
        """Run a complete health check"""
        self.logger.info("=" * 60)
        self.logger.info("Starting health check...")
        
        issues = []
        
        # Check disk space
        disk_info = self.check_disk_space()
        self.logger.info(f"Disk: {disk_info['free_gb']:.1f}GB free ({100-disk_info['percent_used']:.1f}%)")
        
        if disk_info['critical']:
            issues.append("CRITICAL: Disk space critically low!")
            self.logger.critical("Disk space critically low!")
        elif disk_info['needs_cleanup']:
            self.logger.warning("Disk space high, running cleanup...")
            self.cleanup_old_captures()
        
        # Check StealthShark processes
        processes = self.find_stealthshark_processes()
        
        if not processes:
            issues.append("No StealthShark processes found")
            self.logger.warning("No StealthShark processes found")
            
            # Check if we should auto-restart
            if self.settings.get('autostart', {}).get('enabled', False):
                self.logger.info("Attempting to restart monitor...")
                if self.restart_monitor():
                    self.logger.info("Monitor restarted successfully")
                else:
                    issues.append("Failed to restart monitor")
        else:
            # Check each process
            for proc in processes:
                health = self.check_process_health(proc)
                
                if health.get('healthy'):
                    self.logger.info(
                        f"Process {health.get('pid')} healthy - "
                        f"CPU: {health.get('cpu_percent', 0):.1f}%, "
                        f"Memory: {health.get('memory_gb', 0):.2f}GB, "
                        f"Runtime: {health.get('runtime_hours', 0):.1f}h"
                    )
                else:
                    self.logger.warning(f"Process {health.get('pid')} unhealthy!")
                    
                    if health.get('is_hung'):
                        issues.append(f"Process {health.get('pid')} is hung")
                        self.logger.error(f"Process {health.get('pid')} appears to be hung")
                        
                        # Kill and restart if configured
                        if self.settings.get('health_check', {}).get('restart_if_hung', True):
                            try:
                                proc.terminate()
                                time.sleep(2)
                                if proc.is_running():
                                    proc.kill()
                                self.logger.info(f"Terminated hung process {health.get('pid')}")
                                
                                # Restart
                                if self.restart_monitor():
                                    self.logger.info("Monitor restarted after terminating hung process")
                            except Exception as e:
                                self.logger.error(f"Failed to restart: {e}")
                    
                    if health.get('is_memory_high'):
                        issues.append(f"Process {health.get('pid')} using too much memory")
                        self.logger.warning(
                            f"Process {health.get('pid')} memory usage high: "
                            f"{health.get('memory_gb', 0):.2f}GB"
                        )
        
        # Check if tshark is actually running
        if not self.check_tshark_running():
            issues.append("tshark not capturing")
            self.logger.warning("tshark process not found - captures may have stopped")
        
        # Check for updates (if enabled)
        if self.settings.get('maintenance', {}).get('auto_update_check', False):
            last_check = self.settings.get('maintenance', {}).get('last_update_check')
            check_interval = self.settings.get('maintenance', {}).get('update_check_days', 7)
            
            should_check = True
            if last_check:
                from datetime import datetime
                try:
                    last_check_date = datetime.fromisoformat(last_check)
                    days_since = (datetime.now() - last_check_date).days
                    should_check = days_since >= check_interval
                except:
                    pass
            
            if should_check:
                self.logger.info("Checking for StealthShark updates...")
                try:
                    import subprocess
                    result = subprocess.run(
                        ['python3', 'check_updates.py', '--check'],
                        cwd=Path(__file__).parent,
                        capture_output=True,
                        timeout=10
                    )
                    if result.returncode == 1:  # Updates available
                        self.logger.info("Updates available! Run 'python3 check_updates.py' to update.")
                except Exception as e:
                    self.logger.debug(f"Update check failed: {e}")
        
        # Summary
        if issues:
            self.logger.warning(f"Health check found {len(issues)} issue(s):")
            for issue in issues:
                self.logger.warning(f"  - {issue}")
        else:
            self.logger.info("Health check passed - all systems operational")
        
        return len(issues) == 0
    
    def monitor_loop(self):
        """Main monitoring loop"""
        interval = self.settings.get('health_check', {}).get('interval_minutes', 30)
        
        self.logger.info(f"Starting health monitor (checking every {interval} minutes)")
        
        while True:
            try:
                healthy = self.run_health_check()
                
                # Sleep until next check
                time.sleep(interval * 60)
                
            except KeyboardInterrupt:
                self.logger.info("Health monitor stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in monitor loop: {e}")
                time.sleep(60)  # Wait a minute before retrying

def main():
    """Main entry point"""
    monitor = HealthMonitor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--once":
            # Run single health check
            monitor.run_health_check()
        elif sys.argv[1] == "--cleanup":
            # Just run cleanup
            monitor.cleanup_old_captures()
        else:
            print("Usage: python3 health_check.py [--once|--cleanup]")
    else:
        # Run continuous monitoring
        monitor.monitor_loop()

if __name__ == "__main__":
    main()
