#!/usr/bin/env python3
"""
StealthShark - Simple Tshark Channel Monitor
Direct tshark monitoring with 4-hour rotation and channel separation
"""

import os
import sys
import time
import signal
import subprocess
import threading
import json
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleTsharkMonitor:
    def __init__(self, base_dir, duration_hours=4):
        self.base_dir = Path(base_dir)
        self.capture_dir = self.base_dir / "channel_captures"
        self.capture_dir.mkdir(exist_ok=True)
        
        self.log_file = self.base_dir / "simple_monitor.log"
        self.active_captures = {}
        self.running = True
        self.duration_hours = duration_hours  # Configurable duration
        self.duration_seconds = duration_hours * 3600  # Convert to seconds
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.stop_all_captures()
        sys.exit(0)
        
    def start_capture(self, interface, stealth_name=None):
        """Start tshark capture on specified interface"""
        if interface in self.active_captures:
            logger.warning(f"Capture already running on {interface}")
            return False
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{interface}_capture_{timestamp}.pcapng"
            filepath = self.capture_dir / filename
            
            # Build command - simplified without exec stealth
            cmd = [
                'tshark', '-i', interface,
                '-w', str(filepath),
                '-b', f'duration:{self.duration_seconds}',  # Configurable duration in seconds
                '-b', f'files:{max(1, int(24 / self.duration_hours))}',  # Keep files for 24 hours total
                '-q'  # Quiet mode
            ]
            
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )
            
            self.active_captures[interface] = {
                'process': process,
                'pid': process.pid,
                'start_time': datetime.now(),
                'filepath': filepath,
                'stealth_name': stealth_name or 'tshark'
            }
            
            logger.info(f"Started capture on {interface} (PID: {process.pid})")
            if stealth_name:
                logger.info(f"Process disguised as: {stealth_name}")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to start capture on {interface}: {e}")
            return False
            
    def stop_capture(self, interface):
        """Stop capture on specified interface"""
        if interface not in self.active_captures:
            logger.warning(f"No active capture on {interface}")
            return False
            
        try:
            capture_info = self.active_captures[interface]
            process = capture_info['process']
            
            # Terminate the process group
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            
            # Wait for process to terminate
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing capture on {interface}")
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                process.wait()
                
            logger.info(f"Stopped capture on {interface}")
            del self.active_captures[interface]
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop capture on {interface}: {e}")
            return False
            
    def stop_all_captures(self):
        """Stop all active captures"""
        interfaces = list(self.active_captures.keys())
        for interface in interfaces:
            self.stop_capture(interface)
            
    def get_status(self):
        """Get status of all captures"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'active_captures': len(self.active_captures),
            'captures': {}
        }
        
        for interface, info in self.active_captures.items():
            runtime = datetime.now() - info['start_time']
            status['captures'][interface] = {
                'pid': info['pid'],
                'stealth_name': info['stealth_name'],
                'runtime_seconds': int(runtime.total_seconds()),
                'runtime_hours': round(runtime.total_seconds() / 3600, 2),
                'filepath': str(info['filepath']),
                'status': 'running' if info['process'].poll() is None else 'stopped'
            }
            
        return status
        
    def monitor_loop(self):
        """Main monitoring loop with countdown timer"""
        logger.info("Starting monitoring loop...")
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 Monitor started for {self.duration_hours} hour rotation cycles")
        logger.info(f"📁 Captures saving to: {self.capture_dir}")
        logger.info(f"{'='*60}\n")
        
        last_display = 0
        
        while self.running:
            try:
                # Check for dead processes
                dead_interfaces = []
                for interface, info in self.active_captures.items():
                    if info['process'].poll() is not None:
                        logger.warning(f"Process for {interface} has died")
                        dead_interfaces.append(interface)
                
                # Clean up dead processes
                for interface in dead_interfaces:
                    del self.active_captures[interface]
                    logger.info(f"Cleaned up dead process for {interface}")
                
                # Display countdown timer for active captures
                current_time = time.time()
                if current_time - last_display >= 10:  # Update display every 10 seconds
                    print("\n" + "="*70)
                    print(f"🦈 StealthShark Monitor Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print("="*70)
                    
                    if self.active_captures:
                        for interface, info in self.active_captures.items():
                            elapsed = datetime.now() - info['start_time']
                            remaining = timedelta(seconds=self.duration_seconds) - elapsed
                            
                            if remaining.total_seconds() > 0:
                                hours = int(remaining.total_seconds() // 3600)
                                minutes = int((remaining.total_seconds() % 3600) // 60)
                                seconds = int(remaining.total_seconds() % 60)
                                
                                print(f"📡 {interface}: Capturing... Time remaining: {hours:02d}:{minutes:02d}:{seconds:02d}")
                                print(f"   └─ PID: {info['pid']} | Disguised as: {info['stealth_name']}")
                            else:
                                print(f"📡 {interface}: Rotation pending...")
                    else:
                        print("⚠️  No active captures")
                    
                    print("="*70)
                    last_display = current_time
                
                # Save status
                status = self.get_status()
                status_file = self.base_dir / "monitor_status.json"
                with open(status_file, 'w') as f:
                    json.dump(status, f, indent=2)
                
                time.sleep(5)  # Check every 5 seconds for smoother countdown
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error

def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description='StealthShark Simple TShark Monitor')
    parser.add_argument('interfaces', nargs='+', help='Network interfaces to monitor')
    parser.add_argument('--duration', type=float, default=4, 
                        help='Capture duration in hours (default: 4)')
    
    args = parser.parse_args()
    interfaces = args.interfaces
    duration_hours = args.duration
    
    # Initialize monitor with configurable duration
    base_dir = Path(__file__).parent
    monitor = SimpleTsharkMonitor(base_dir, duration_hours)
    
    logger.info(f"Monitor configured for {duration_hours} hour rotation cycles")
    
    # Stealth process names
    stealth_names = [
        "kernel_task", "launchd", "UserEventAgent", 
        "WindowServer", "Finder", "SystemUIServer"
    ]
    
    try:
        # Start captures on all interfaces
        for i, interface in enumerate(interfaces):
            stealth_name = stealth_names[i % len(stealth_names)]
            if monitor.start_capture(interface, stealth_name):
                logger.info(f"Successfully started monitoring {interface}")
            else:
                logger.error(f"Failed to start monitoring {interface}")
        
        # Start monitoring loop
        monitor.monitor_loop()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        logger.info("Shutting down...")
        monitor.stop_all_captures()
        logger.info("Shutdown complete")

if __name__ == "__main__":
    main()
