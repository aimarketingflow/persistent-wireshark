#!/usr/bin/env python3
"""
CLI Launcher for Persistent Wireshark Monitor
Sets up virtual environment and launches the monitoring system
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

def setup_venv():
    """Create and setup virtual environment"""
    venv_path = Path("wireshark_monitor_venv")
    
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        
    # Get python path in venv
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python"
    else:
        python_path = venv_path / "bin" / "python3"
        
    # Install requirements
    print("Installing dependencies...")
    subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(python_path), "-m", "pip", "install", "psutil"], check=True)
    
    return python_path

def main():
    parser = argparse.ArgumentParser(description='Persistent Wireshark Monitor CLI Launcher')
    parser.add_argument('--setup-only', action='store_true',
                       help='Only setup virtual environment, do not run monitor')
    parser.add_argument('--duration', type=int, default=3600,
                       help='Capture duration in seconds (60-18000)')
    parser.add_argument('--interval', type=int, default=5,
                       help='Check interval in seconds')
    parser.add_argument('--capture-dir', default='./pcap_captures',
                       help='Directory to store PCAP files')
    parser.add_argument('--no-alerts', action='store_true',
                       help='Disable alert notifications')
    parser.add_argument('--status', action='store_true',
                       help='Show current status and exit')
    
    args = parser.parse_args()
    
    # Setup virtual environment
    python_path = setup_venv()
    
    if args.setup_only:
        print("Virtual environment setup complete!")
        return
        
    # Build command for monitor
    cmd = [
        str(python_path),
        "persistent_wireshark_monitor.py",
        "--duration", str(args.duration),
        "--interval", str(args.interval),
        "--capture-dir", args.capture_dir
    ]
    
    if args.no_alerts:
        cmd.append("--no-alerts")
        
    if args.status:
        cmd.append("--status")
        
    print(f"Launching Wireshark Monitor...")
    print(f"Duration: {args.duration/60:.1f} minutes per capture")
    print(f"Check interval: {args.interval} seconds")
    print(f"Capture directory: {args.capture_dir}")
    
    # Run the monitor
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nMonitor stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Monitor failed with exit code {e.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
