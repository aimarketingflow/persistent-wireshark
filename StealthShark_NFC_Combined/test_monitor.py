#!/usr/bin/env python3
"""Test the PersistentWiresharkMonitor with tshark"""

import time
import sys
import traceback
from pathlib import Path
from persistent_wireshark_monitor import PersistentWiresharkMonitor

def test_monitor():
    """Test the monitor with actual capture"""
    print("=== Testing PersistentWiresharkMonitor ===\n")
    
    # Create test capture directory
    capture_dir = "./test_monitor_captures"
    Path(capture_dir).mkdir(exist_ok=True)
    
    # Create monitor instance
    print("Creating monitor instance...")
    monitor = PersistentWiresharkMonitor(
        capture_dir=capture_dir,
        capture_duration=10,  # 10 second captures
        check_interval=2,
        alert_callback=lambda msg: print(f"ALERT: {msg}")
    )
    
    print(f"Monitor created with capture_dir: {capture_dir}")
    print(f"Duration: {monitor.capture_duration}s, Interval: {monitor.check_interval}s\n")
    
    # Start monitoring
    print("Starting monitor...")
    monitor.start_monitoring()
    
    # Let it run for 15 seconds
    print("Monitoring for 15 seconds...")
    for i in range(15):
        time.sleep(1)
        print(f"  {i+1}/15s - Active captures: {list(monitor.active_captures.keys())}")
        
        # Check interface stats
        if hasattr(monitor, 'interface_stats'):
            for interface, stats in monitor.interface_stats.items():
                packets = stats.get('packets', 0)
                if packets > 0:
                    print(f"    -> {interface}: {packets} packets")
    
    # Stop monitoring
    print("\nStopping monitor...")
    monitor.stop_monitoring()
    
    # Check for captured files
    print("\nChecking for capture files...")
    capture_path = Path(capture_dir)
    pcap_files = list(capture_path.rglob("*.pcap"))
    
    if pcap_files:
        print(f"✅ Found {len(pcap_files)} capture file(s):")
        for f in pcap_files:
            size = f.stat().st_size
            print(f"  - {f.name} ({size} bytes)")
    else:
        print("❌ No capture files found")
        
    print("\n=== Test Complete ===")
    return len(pcap_files) > 0

if __name__ == "__main__":
    try:
        success = test_monitor()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
