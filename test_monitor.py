#!/usr/bin/env python3
"""
Test Script for Persistent Wireshark Monitor
Generates network activity and verifies monitor detection
"""

import subprocess
import time
import threading
import requests
import socket
import json
from pathlib import Path

class MonitorTester:
    def __init__(self):
        self.test_results = []
        self.monitor_process = None
        
    def generate_network_activity(self):
        """Generate various types of network activity"""
        activities = []
        
        # 1. HTTP requests (en0 activity)
        try:
            print("🌐 Generating HTTP traffic...")
            response = requests.get("https://httpbin.org/get", timeout=5)
            activities.append(f"HTTP GET: {response.status_code}")
        except Exception as e:
            activities.append(f"HTTP GET failed: {e}")
            
        # 2. DNS lookups
        try:
            print("🔍 Generating DNS traffic...")
            socket.gethostbyname("google.com")
            socket.gethostbyname("github.com")
            activities.append("DNS lookups completed")
        except Exception as e:
            activities.append(f"DNS failed: {e}")
            
        # 3. Loopback traffic
        try:
            print("🔄 Generating loopback traffic...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', 0))
            sock.listen(1)
            port = sock.getsockname()[1]
            
            # Connect to self
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('127.0.0.1', port))
            conn, addr = sock.accept()
            
            # Send some data
            client.send(b"test data")
            data = conn.recv(1024)
            
            client.close()
            conn.close()
            sock.close()
            activities.append("Loopback traffic generated")
        except Exception as e:
            activities.append(f"Loopback failed: {e}")
            
        return activities
        
    def start_monitor_test(self, duration=120):
        """Start monitor in test mode for specified duration"""
        print(f"🚀 Starting monitor test for {duration} seconds...")
        
        cmd = [
            "./wireshark_monitor_venv/bin/python3",
            "persistent_wireshark_monitor.py",
            "--duration", str(duration),
            "--interval", "2",
            "--capture-dir", "./test_captures"
        ]
        
        try:
            self.monitor_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            return True
        except Exception as e:
            print(f"❌ Failed to start monitor: {e}")
            return False
            
    def check_captures(self):
        """Check if captures were created"""
        capture_dir = Path("./test_captures")
        if not capture_dir.exists():
            return []
            
        captures = []
        for subdir in ["active", "completed"]:
            subdir_path = capture_dir / subdir
            if subdir_path.exists():
                for pcap_file in subdir_path.glob("*.pcap*"):
                    captures.append(str(pcap_file))
                    
        return captures
        
    def run_comprehensive_test(self):
        """Run comprehensive test of monitor functionality"""
        print("🧪 Starting Comprehensive Wireshark Monitor Test")
        print("=" * 50)
        
        # Start monitor
        if not self.start_monitor_test(duration=60):
            return False
            
        # Wait for monitor to initialize
        print("⏳ Waiting for monitor initialization...")
        time.sleep(5)
        
        # Generate network activity
        print("📡 Generating network activity...")
        activities = self.generate_network_activity()
        
        for activity in activities:
            print(f"  ✓ {activity}")
            
        # Wait for captures to start
        print("⏳ Waiting for captures to be detected...")
        time.sleep(10)
        
        # Check for captures
        captures = self.check_captures()
        print(f"📁 Found {len(captures)} capture files:")
        for capture in captures:
            print(f"  📄 {capture}")
            
        # Check monitor status
        print("📊 Checking monitor status...")
        try:
            status_result = subprocess.run([
                "./wireshark_monitor_venv/bin/python3",
                "cli_wireshark_monitor.py", 
                "--status"
            ], capture_output=True, text=True, timeout=30)
            
            if status_result.returncode == 0:
                print("✅ Monitor status check successful")
                # Parse JSON from output
                lines = status_result.stdout.strip().split('\n')
                for line in lines:
                    if line.startswith('{'):
                        try:
                            status_data = json.loads(line)
                            active_captures = status_data.get('active_captures', 0)
                            monitored_interfaces = len(status_data.get('monitored_interfaces', []))
                            print(f"  📈 Active captures: {active_captures}")
                            print(f"  🔌 Monitored interfaces: {monitored_interfaces}")
                        except:
                            pass
            else:
                print("❌ Monitor status check failed")
                
        except Exception as e:
            print(f"❌ Status check error: {e}")
            
        # Stop monitor
        if self.monitor_process:
            print("🛑 Stopping monitor...")
            self.monitor_process.terminate()
            try:
                self.monitor_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.monitor_process.kill()
                
        # Final results
        print("\n🎯 Test Results Summary:")
        print(f"  Network activities: {len(activities)}")
        print(f"  Capture files created: {len(captures)}")
        print(f"  Monitor process: {'✅ Success' if self.monitor_process else '❌ Failed'}")
        
        return len(captures) > 0

def main():
    tester = MonitorTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 Test PASSED - Monitor is working correctly!")
    else:
        print("\n❌ Test FAILED - Check monitor configuration")
        
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
