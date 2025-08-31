#!/usr/bin/env python3
"""
Comprehensive GUI Test Suite
Tests the enhanced Wireshark Monitor GUI functionality
"""

import subprocess
import time
import threading
import sys
import os
from pathlib import Path

class GUITester:
    def __init__(self):
        self.test_results = []
        self.gui_process = None
        
    def test_gui_startup(self):
        """Test GUI startup without crashes"""
        print("🧪 Testing GUI startup...")
        
        try:
            # Start GUI in background
            cmd = [
                "./wireshark_monitor_venv/bin/python3",
                "enhanced_wireshark_monitor_gui.py"
            ]
            
            self.gui_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for startup
            time.sleep(3)
            
            # Check if process is still running
            if self.gui_process.poll() is None:
                print("✅ GUI started successfully")
                self.test_results.append("GUI startup: PASS")
                return True
            else:
                stdout, stderr = self.gui_process.communicate()
                print(f"❌ GUI crashed during startup")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                self.test_results.append("GUI startup: FAIL")
                return False
                
        except Exception as e:
            print(f"❌ GUI startup test failed: {e}")
            self.test_results.append(f"GUI startup: ERROR - {e}")
            return False
            
    def test_gui_stability(self, duration=10):
        """Test GUI stability over time"""
        print(f"🧪 Testing GUI stability for {duration} seconds...")
        
        if not self.gui_process or self.gui_process.poll() is not None:
            print("❌ GUI not running, cannot test stability")
            self.test_results.append("GUI stability: FAIL - Not running")
            return False
            
        start_time = time.time()
        
        while time.time() - start_time < duration:
            if self.gui_process.poll() is not None:
                stdout, stderr = self.gui_process.communicate()
                print(f"❌ GUI crashed during stability test")
                print(f"STDERR: {stderr}")
                self.test_results.append("GUI stability: FAIL - Crashed")
                return False
                
            time.sleep(1)
            
        print("✅ GUI remained stable")
        self.test_results.append("GUI stability: PASS")
        return True
        
    def test_log_files(self):
        """Test log file creation"""
        print("🧪 Testing log file creation...")
        
        log_dir = Path("./gui_logs")
        if log_dir.exists():
            log_files = list(log_dir.glob("gui_debug_*.log"))
            if log_files:
                latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
                print(f"✅ Log file created: {latest_log}")
                
                # Check log content
                with open(latest_log, 'r') as f:
                    content = f.read()
                    if "GUI logging initialized" in content:
                        print("✅ Log content looks good")
                        self.test_results.append("Log files: PASS")
                        return True
                    else:
                        print("❌ Log content incomplete")
                        self.test_results.append("Log files: FAIL - Incomplete")
                        return False
            else:
                print("❌ No log files found")
                self.test_results.append("Log files: FAIL - Not created")
                return False
        else:
            print("❌ Log directory not created")
            self.test_results.append("Log files: FAIL - No directory")
            return False
            
    def test_dependencies(self):
        """Test all required dependencies"""
        print("🧪 Testing dependencies...")
        
        dependencies = ["PyQt6", "psutil", "requests"]
        all_good = True
        
        for dep in dependencies:
            try:
                result = subprocess.run([
                    "./wireshark_monitor_venv/bin/python3",
                    "-c", f"import {dep}; print('{dep} OK')"
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print(f"✅ {dep} available")
                else:
                    print(f"❌ {dep} not available: {result.stderr}")
                    all_good = False
                    
            except Exception as e:
                print(f"❌ Error testing {dep}: {e}")
                all_good = False
                
        if all_good:
            self.test_results.append("Dependencies: PASS")
        else:
            self.test_results.append("Dependencies: FAIL")
            
        return all_good
        
    def test_interface_detection(self):
        """Test interface detection functionality"""
        print("🧪 Testing interface detection...")
        
        try:
            result = subprocess.run([
                "./wireshark_monitor_venv/bin/python3",
                "-c", """
import psutil
interfaces = list(psutil.net_if_addrs().keys())
print(f"Found {len(interfaces)} interfaces: {interfaces}")
"""
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and "Found" in result.stdout:
                print(f"✅ Interface detection working: {result.stdout.strip()}")
                self.test_results.append("Interface detection: PASS")
                return True
            else:
                print(f"❌ Interface detection failed: {result.stderr}")
                self.test_results.append("Interface detection: FAIL")
                return False
                
        except Exception as e:
            print(f"❌ Interface detection test error: {e}")
            self.test_results.append(f"Interface detection: ERROR - {e}")
            return False
            
    def cleanup(self):
        """Clean up test processes"""
        if self.gui_process and self.gui_process.poll() is None:
            print("🧹 Cleaning up GUI process...")
            self.gui_process.terminate()
            try:
                self.gui_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.gui_process.kill()
                
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🧪 Starting Comprehensive GUI Test Suite")
        print("=" * 50)
        
        tests = [
            ("Dependencies", self.test_dependencies),
            ("Interface Detection", self.test_interface_detection),
            ("GUI Startup", self.test_gui_startup),
            ("GUI Stability", lambda: self.test_gui_stability(10)),
            ("Log Files", self.test_log_files)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n--- {test_name} Test ---")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                print(f"❌ {test_name} test crashed: {e}")
                self.test_results.append(f"{test_name}: CRASH - {e}")
                
        # Cleanup
        self.cleanup()
        
        # Results
        print("\n" + "=" * 50)
        print("🎯 Test Results Summary:")
        print(f"  Tests passed: {passed}/{total}")
        print(f"  Success rate: {passed/total*100:.1f}%")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✅" if "PASS" in result else "❌"
            print(f"  {status} {result}")
            
        return passed == total

def main():
    tester = GUITester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 All tests PASSED - GUI is ready!")
    else:
        print("\n❌ Some tests FAILED - Check issues above")
        
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
