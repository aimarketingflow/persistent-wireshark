#!/usr/bin/env python3
"""
StealthShark - Enhanced TShark Memory Monitor
Advanced memory management and monitoring for stealth network capture operations
"""

import os
import sys
import time
import json
import psutil
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import threading
import signal
import shutil

class MemoryOptimizedTSharkMonitor:
    def __init__(self, base_dir=None, duration_hours=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.capture_dir = self.base_dir / "channel_captures"
        self.log_file = self.base_dir / "enhanced_memory_monitor.log"
        self.config_file = self.base_dir / "memory_config.json"
        self.status_file = self.base_dir / "memory_status.json"
        
        # Memory management settings
        self.max_memory_usage = 2 * 1024 * 1024 * 1024  # 2GB default
        self.max_disk_usage = 50 * 1024 * 1024 * 1024   # 50GB default
        self.cleanup_threshold = 0.8  # Cleanup at 80% capacity
        self.rotation_hours = duration_hours if duration_hours else 4  # Allow override
        self.max_files_per_interface = 24
        
        # Process tracking
        self.active_captures = {}
        self.stealth_processes = {}
        self.monitoring_active = False
        
        # Setup logging with memory-efficient configuration
        self.setup_logging()
        self.load_config()
        
    def setup_logging(self):
        """Setup memory-efficient logging with rotation"""
        from logging.handlers import RotatingFileHandler
        
        # Create logs directory
        log_dir = self.base_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Configure rotating file handler (max 10MB, 5 files)
        handler = RotatingFileHandler(
            log_dir / "stealthshark.log",
            maxBytes=10*1024*1024,
            backupCount=5
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        self.logger = logging.getLogger('StealthShark')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)
        
        # Console handler for immediate feedback
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
    def load_config(self):
        """Load configuration from file or create defaults"""
        default_config = {
            "max_memory_gb": 2,
            "max_disk_gb": 50,
            "cleanup_threshold": 0.8,
            "rotation_hours": 4,
            "interfaces": ["en0", "en1", "awdl0"],
            "stealth_names": [
                "kernel_task", "launchd", "UserEventAgent", 
                "WindowServer", "Finder", "SystemUIServer"
            ],
            "compression_enabled": True,
            "auto_cleanup": True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}, using defaults")
                config = default_config
        else:
            config = default_config
            
        # Apply configuration
        self.max_memory_usage = config["max_memory_gb"] * 1024 * 1024 * 1024
        self.max_disk_usage = config["max_disk_gb"] * 1024 * 1024 * 1024
        self.cleanup_threshold = config["cleanup_threshold"]
        # Only update rotation_hours if not already set via constructor
        if not hasattr(self, 'rotation_hours') or self.rotation_hours == 4:
            self.rotation_hours = config["rotation_hours"]
        self.interfaces = config["interfaces"]
        self.stealth_names = config["stealth_names"]
        self.compression_enabled = config["compression_enabled"]
        self.auto_cleanup = config["auto_cleanup"]
        
        # Save config back to ensure all defaults are present
        self.save_config()
        
    def save_config(self):
        """Save current configuration to file"""
        config = {
            "max_memory_gb": self.max_memory_usage // (1024 * 1024 * 1024),
            "max_disk_gb": self.max_disk_usage // (1024 * 1024 * 1024),
            "cleanup_threshold": self.cleanup_threshold,
            "rotation_hours": self.rotation_hours,
            "interfaces": getattr(self, 'interfaces', ["en0", "en1", "awdl0"]),
            "stealth_names": getattr(self, 'stealth_names', ["kernel_task", "launchd"]),
            "compression_enabled": getattr(self, 'compression_enabled', True),
            "auto_cleanup": getattr(self, 'auto_cleanup', True)
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            
    def get_system_status(self):
        """Get comprehensive system status"""
        try:
            # Memory information
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(str(self.base_dir))
            
            # Process information
            tshark_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'create_time', 'cmdline']):
                try:
                    if 'tshark' in proc.info['name'].lower() or 'dumpcap' in proc.info['name'].lower():
                        runtime = time.time() - proc.info['create_time']
                        memory_mb = proc.info['memory_info'].rss / (1024 * 1024)
                        
                        # Extract interface from command line
                        interface = "unknown"
                        if proc.info['cmdline']:
                            for i, arg in enumerate(proc.info['cmdline']):
                                if arg == '-i' and i + 1 < len(proc.info['cmdline']):
                                    interface = proc.info['cmdline'][i + 1]
                                    break
                        
                        tshark_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'interface': interface,
                            'memory_mb': round(memory_mb, 2),
                            'runtime_hours': round(runtime / 3600, 2),
                            'status': 'running'
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Capture directory size
            capture_size = 0
            capture_files = 0
            if self.capture_dir.exists():
                for file_path in self.capture_dir.rglob('*'):
                    if file_path.is_file():
                        capture_size += file_path.stat().st_size
                        capture_files += 1
            
            status = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'memory_total_gb': round(memory.total / (1024**3), 2),
                    'memory_used_gb': round(memory.used / (1024**3), 2),
                    'memory_percent': memory.percent,
                    'disk_total_gb': round(disk.total / (1024**3), 2),
                    'disk_used_gb': round(disk.used / (1024**3), 2),
                    'disk_percent': round((disk.used / disk.total) * 100, 2)
                },
                'captures': {
                    'active_processes': len(tshark_processes),
                    'total_size_gb': round(capture_size / (1024**3), 2),
                    'total_files': capture_files,
                    'processes': tshark_processes
                },
                'thresholds': {
                    'max_memory_gb': round(self.max_memory_usage / (1024**3), 2),
                    'max_disk_gb': round(self.max_disk_usage / (1024**3), 2),
                    'cleanup_threshold': self.cleanup_threshold
                }
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return None
            
    def start_stealth_capture(self, interface, stealth_name=None):
        """Start a stealth TShark capture process"""
        try:
            if not stealth_name:
                stealth_name = self.stealth_names[len(self.active_captures) % len(self.stealth_names)]
            
            # Create capture directory
            self.capture_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{interface}_capture_{timestamp}.pcapng"
            filepath = self.capture_dir / filename
            
            # Build tshark command with stealth process name
            cmd = [
                'exec', '-a', stealth_name,
                'tshark', '-i', interface,
                '-w', str(filepath),
                '-b', f'duration:{self.rotation_hours * 3600}',  # Rotate every N hours
                '-b', f'files:{max(1, int(24 / self.rotation_hours))}',  # Keep files for 24 hours total
                '-q'  # Quiet mode
            ]
            
            # Start the process
            process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.active_captures[interface] = {
                'process': process,
                'pid': process.pid,
                'stealth_name': stealth_name,
                'start_time': datetime.now(),
                'filepath': filepath,
                'interface': interface
            }
            
            self.logger.info(f"Started stealth capture on {interface} as '{stealth_name}' (PID: {process.pid})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start stealth capture on {interface}: {e}")
            return False
            
    def stop_capture(self, interface):
        """Stop capture for specific interface"""
        if interface in self.active_captures:
            try:
                process = self.active_captures[interface]['process']
                process.terminate()
                process.wait(timeout=10)
                
                self.logger.info(f"Stopped capture on {interface}")
                del self.active_captures[interface]
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to stop capture on {interface}: {e}")
                return False
        return False
        
    def cleanup_old_files(self, force=False):
        """Intelligent cleanup of old capture files"""
        if not self.capture_dir.exists():
            return
            
        try:
            current_usage = sum(f.stat().st_size for f in self.capture_dir.rglob('*') if f.is_file())
            usage_ratio = current_usage / self.max_disk_usage
            
            if not force and usage_ratio < self.cleanup_threshold:
                return
                
            self.logger.info(f"Starting cleanup - current usage: {usage_ratio:.1%}")
            
            # Get all capture files sorted by modification time
            files = []
            for file_path in self.capture_dir.rglob('*.pcapng'):
                if file_path.is_file():
                    files.append((file_path.stat().st_mtime, file_path))
            
            files.sort()  # Oldest first
            
            # Remove oldest files until under threshold
            target_size = self.max_disk_usage * (self.cleanup_threshold - 0.1)  # 10% buffer
            removed_count = 0
            freed_space = 0
            
            for mtime, file_path in files:
                if current_usage <= target_size:
                    break
                    
                try:
                    file_size = file_path.stat().st_size
                    
                    # Compress before deletion if enabled
                    if self.compression_enabled and not file_path.name.endswith('.gz'):
                        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
                        subprocess.run(['gzip', str(file_path)], check=True)
                        self.logger.info(f"Compressed {file_path.name}")
                        current_usage -= file_size - compressed_path.stat().st_size
                    else:
                        file_path.unlink()
                        current_usage -= file_size
                        freed_space += file_size
                        removed_count += 1
                        
                except Exception as e:
                    self.logger.warning(f"Failed to process {file_path}: {e}")
                    
            if removed_count > 0:
                self.logger.info(f"Cleanup complete: removed {removed_count} files, freed {freed_space / (1024**3):.2f} GB")
                
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            
    def start_monitoring(self, interfaces=None):
        """Start monitoring on specified interfaces"""
        if not interfaces:
            interfaces = getattr(self, 'interfaces', ['en0', 'en1', 'awdl0'])
            
        self.monitoring_active = True
        
        # Start captures on all interfaces
        for interface in interfaces:
            if self.start_stealth_capture(interface):
                self.logger.info(f"Monitoring started on {interface}")
            else:
                self.logger.error(f"Failed to start monitoring on {interface}")
                
        # Start background monitoring thread
        monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitor_thread.start()
        
        self.logger.info("StealthShark monitoring system started")
        
    def _monitoring_loop(self):
        """Background monitoring loop with countdown timer"""
        last_display = 0
        print(f"\n{'='*60}")
        print(f"📊 Monitor started for {self.rotation_hours} hour rotation cycles")
        print(f"📁 Captures saving to: {self.capture_dir}")
        print(f"{'='*60}\n")
        
        while self.monitoring_active:
            try:
                # Display countdown timer
                current_time = time.time()
                if current_time - last_display >= 10:  # Update every 10 seconds
                    print("\n" + "="*70)
                    print(f"🦈 StealthShark Monitor Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print("="*70)
                    
                    if self.active_captures:
                        for interface, info in self.active_captures.items():
                            elapsed = datetime.now() - info['start_time']
                            remaining_seconds = (self.rotation_hours * 3600) - elapsed.total_seconds()
                            
                            if remaining_seconds > 0:
                                hours = int(remaining_seconds // 3600)
                                minutes = int((remaining_seconds % 3600) // 60)
                                seconds = int(remaining_seconds % 60)
                                
                                print(f"📡 {interface}: Capturing... Time remaining: {hours:02d}:{minutes:02d}:{seconds:02d}")
                                print(f"   └─ PID: {info['pid']} | Disguised as: {info['stealth_name']}")
                            else:
                                print(f"📡 {interface}: Rotation pending...")
                    else:
                        print("⚠️  No active captures")
                    
                    # Memory status
                    mem_usage = psutil.virtual_memory().percent
                    disk_usage = psutil.disk_usage(str(self.capture_dir)).percent if self.capture_dir.exists() else 0
                    print(f"\n💾 Memory: {mem_usage:.1f}% | Disk: {disk_usage:.1f}%")
                    print("="*70)
                    last_display = current_time
                
                # Update status
                status = self.get_system_status()
                if status:
                    with open(self.status_file, 'w') as f:
                        json.dump(status, f, indent=2)
                
                # Auto cleanup if enabled
                if getattr(self, 'auto_cleanup', True):
                    self.cleanup_old_files()
                
                # Check for dead processes and restart
                self._check_and_restart_processes()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(60)  # Wait longer on error
                
    def _check_and_restart_processes(self):
        """Check for dead processes and restart them"""
        dead_interfaces = []
        
        for interface, capture_info in self.active_captures.items():
            process = capture_info['process']
            if process.poll() is not None:  # Process has died
                self.logger.warning(f"Process for {interface} has died, restarting...")
                dead_interfaces.append(interface)
                
        # Restart dead processes
        for interface in dead_interfaces:
            del self.active_captures[interface]
            self.start_stealth_capture(interface)
            
    def stop_monitoring(self):
        """Stop all monitoring"""
        self.monitoring_active = False
        
        # Stop all active captures
        for interface in list(self.active_captures.keys()):
            self.stop_capture(interface)
            
        self.logger.info("StealthShark monitoring stopped")

def main():
    """Main entry point for standalone execution"""
    import argparse
    parser = argparse.ArgumentParser(description='StealthShark Enhanced Memory Monitor')
    parser.add_argument('--duration', type=float, default=None,
                        help='Capture duration in hours (default: from config or 4)')
    parser.add_argument('--interfaces', nargs='+', default=None,
                        help='Network interfaces to monitor (default: from config)')
    
    args = parser.parse_args()
    monitor = MemoryOptimizedTSharkMonitor(duration_hours=args.duration)
    
    try:
        # Start monitoring
        interfaces = args.interfaces if args.interfaces else None
        monitor.start_monitoring(interfaces)
        
        if args.duration:
            print(f"Monitor configured for {args.duration} hour rotation cycles")
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down StealthShark...")
        monitor.stop_monitoring()
        print("StealthShark stopped.")

if __name__ == "__main__":
    main()
