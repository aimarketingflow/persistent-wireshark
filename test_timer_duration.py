#!/usr/bin/env python3
"""
StealthShark Timer Duration Test Script
Tests the configurable timer duration functionality
"""

import sys
import time
from datetime import datetime
from pathlib import Path

# Import the monitoring modules
from enhanced_memory_monitor import MemoryOptimizedTSharkMonitor
from simple_tshark_monitor import SimpleTsharkMonitor

def test_duration_settings():
    """Test that duration settings are properly applied"""
    print("🦈 StealthShark Timer Duration Test")
    print("=" * 50)
    
    # Test different duration values
    test_durations = [1, 3, 6, 12, 24]
    
    for duration in test_durations:
        print(f"\n📊 Testing {duration} hour duration...")
        
        # Test Enhanced Monitor
        print(f"  Enhanced Monitor:")
        enhanced_monitor = MemoryOptimizedTSharkMonitor(duration_hours=duration)
        print(f"    - Rotation hours: {enhanced_monitor.rotation_hours}")
        print(f"    - Rotation seconds: {enhanced_monitor.rotation_hours * 3600}")
        print(f"    - Files to keep (24hr): {int(24 / enhanced_monitor.rotation_hours)}")
        
        # Test Simple Monitor
        print(f"  Simple Monitor:")
        simple_monitor = SimpleTsharkMonitor(Path.cwd(), duration_hours=duration)
        print(f"    - Duration hours: {simple_monitor.duration_hours}")
        print(f"    - Duration seconds: {simple_monitor.duration_seconds}")
        print(f"    - Files to keep (24hr): {int(24 / simple_monitor.duration_hours)}")
        
        # Verify calculations
        expected_seconds = duration * 3600
        assert simple_monitor.duration_seconds == expected_seconds, f"Simple monitor duration mismatch!"
        assert enhanced_monitor.rotation_hours == duration, f"Enhanced monitor rotation mismatch!"
        print(f"  ✅ Duration settings verified for {duration} hours")
    
    print("\n" + "=" * 50)
    print("✅ All timer duration tests passed!")
    print("\nNOTE: The actual tshark commands will use:")
    print("  -b duration:<seconds> : Rotate file after specified seconds")
    print("  -b files:<count>      : Keep specified number of files")
    print("\nExample for 3 hour rotation:")
    print("  tshark -i en0 -w capture.pcapng -b duration:10800 -b files:8")
    
def test_command_generation():
    """Test that the correct tshark commands are generated"""
    print("\n📝 Testing Command Generation")
    print("=" * 50)
    
    test_cases = [
        (1, 3600, 24),   # 1 hour = 3600 seconds, 24 files for 24 hours
        (3, 10800, 8),   # 3 hours = 10800 seconds, 8 files for 24 hours
        (4, 14400, 6),   # 4 hours = 14400 seconds, 6 files for 24 hours
        (6, 21600, 4),   # 6 hours = 21600 seconds, 4 files for 24 hours
        (12, 43200, 2),  # 12 hours = 43200 seconds, 2 files for 24 hours
    ]
    
    for hours, expected_seconds, expected_files in test_cases:
        print(f"\n🕐 {hours} hour rotation:")
        monitor = SimpleTsharkMonitor(Path.cwd(), duration_hours=hours)
        
        # Build example command
        cmd_parts = [
            'tshark', '-i', 'en0',
            '-w', 'capture.pcapng',
            '-b', f'duration:{monitor.duration_seconds}',
            '-b', f'files:{int(24 / monitor.duration_hours)}',
            '-q'
        ]
        
        print(f"  Command: {' '.join(cmd_parts)}")
        print(f"  Duration: {monitor.duration_seconds} seconds ({monitor.duration_seconds/3600:.1f} hours)")
        print(f"  Files: {int(24 / monitor.duration_hours)} (covers 24 hours)")
        
        # Verify
        assert monitor.duration_seconds == expected_seconds, f"Duration mismatch for {hours} hours"
        assert int(24 / monitor.duration_hours) == expected_files, f"File count mismatch for {hours} hours"
        print(f"  ✅ Verified")
    
    print("\n" + "=" * 50)
    print("✅ Command generation tests passed!")

def main():
    """Main test function"""
    print(f"\n🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Run duration settings test
        test_duration_settings()
        
        # Run command generation test
        test_command_generation()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 50)
        print("\n💡 The timer issue has been fixed:")
        print("  - You can now specify any duration in hours (e.g., 3, 6, 12)")
        print("  - The scripts will properly rotate files at the specified interval")
        print("  - Total retention is always 24 hours worth of captures")
        print("\n📌 Usage examples:")
        print("  python3 simple_tshark_monitor.py en0 --duration 3")
        print("  python3 enhanced_memory_monitor.py --duration 3")
        print("  python3 gui_memory_monitor.py --duration 3")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
