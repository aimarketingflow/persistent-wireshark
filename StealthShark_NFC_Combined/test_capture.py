#!/usr/bin/env python3
"""Test script to verify packet capture functionality"""

import subprocess
import time
import os
from pathlib import Path

def test_tshark():
    """Test if tshark can capture packets"""
    print("Testing tshark capture...")
    
    # Create test capture directory
    capture_dir = Path("./test_captures")
    capture_dir.mkdir(exist_ok=True)
    
    # Test file
    test_file = capture_dir / f"test_{int(time.time())}.pcap"
    
    # Try to capture 10 packets
    cmd = [
        '/usr/local/bin/tshark',
        '-i', 'en0',  # WiFi interface
        '-c', '10',   # Capture 10 packets
        '-w', str(test_file)  # Write to file
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        if test_file.exists():
            size = test_file.stat().st_size
            print(f"✅ Capture file created: {test_file} ({size} bytes)")
            return True
        else:
            print("❌ Capture file not created")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout waiting for capture")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_tcpdump():
    """Test if tcpdump can capture packets"""
    print("\nTesting tcpdump capture...")
    
    # Create test capture directory
    capture_dir = Path("./test_captures")
    capture_dir.mkdir(exist_ok=True)
    
    # Test file
    test_file = capture_dir / f"test_tcpdump_{int(time.time())}.pcap"
    
    # Try to capture 10 packets
    cmd = [
        'sudo', '/usr/sbin/tcpdump',
        '-i', 'en0',  # WiFi interface
        '-c', '10',   # Capture 10 packets
        '-w', str(test_file)  # Write to file
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        if test_file.exists():
            size = test_file.stat().st_size
            print(f"✅ Capture file created: {test_file} ({size} bytes)")
            return True
        else:
            print("❌ Capture file not created")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout waiting for capture")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def list_interfaces():
    """List available network interfaces"""
    print("\nListing network interfaces...")
    
    cmd = ['/usr/local/bin/tshark', '-D']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print("Available interfaces:")
        print(result.stdout)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error listing interfaces: {e}")
        return False

if __name__ == "__main__":
    print("=== Packet Capture Test ===\n")
    
    # List interfaces
    list_interfaces()
    
    # Test tshark
    tshark_ok = test_tshark()
    
    # Test tcpdump (will need sudo)
    # tcpdump_ok = test_tcpdump()
    
    print("\n=== Test Results ===")
    print(f"TShark: {'✅ Working' if tshark_ok else '❌ Not working'}")
    # print(f"TCPDump: {'✅ Working' if tcpdump_ok else '❌ Not working'}")
