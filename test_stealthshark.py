#!/usr/bin/env python3
"""
StealthShark Test Suite
Comprehensive testing for all StealthShark components
"""

import sys
import os
import time
import tempfile
import subprocess
from pathlib import Path
import json

def test_imports():
    """Test all module imports"""
    print("🧪 Testing imports...")
    
    try:
        from enhanced_memory_monitor import MemoryOptimizedTSharkMonitor
        print("✅ Enhanced memory monitor import successful")
    except Exception as e:
        print(f"❌ Enhanced monitor import failed: {e}")
        return False
    
    try:
        from simple_tshark_monitor import SimpleTsharkMonitor
        print("✅ Simple monitor import successful")
    except Exception as e:
        print(f"❌ Simple monitor import failed: {e}")
        return False
    
    try:
        import PyQt6
        print("✅ PyQt6 available for GUI")
    except ImportError:
        print("⚠️  PyQt6 not available - GUI will not work")
    
    return True

def test_system_requirements():
    """Test system requirements"""
    print("\n🔧 Testing system requirements...")
    
    # Test Python version
    if sys.version_info >= (3, 8):
        print(f"✅ Python {sys.version.split()[0]} (>= 3.8)")
    else:
        print(f"❌ Python {sys.version.split()[0]} (< 3.8 required)")
        return False
    
    # Test tshark availability
    try:
        result = subprocess.run(['tshark', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ TShark available: {version_line}")
        else:
            print("❌ TShark not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ TShark not found or not responding")
        return False
    
    # Test network interfaces
    try:
        result = subprocess.run(['tshark', '-D'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            interfaces = [line for line in result.stdout.split('\n') if line.strip()]
            print(f"✅ Network interfaces available: {len(interfaces)}")
            for interface in interfaces[:3]:  # Show first 3
                print(f"   {interface}")
        else:
            print("⚠️  Could not list network interfaces")
    except subprocess.TimeoutExpired:
        print("⚠️  Interface listing timed out")
    
    return True

def test_enhanced_monitor():
    """Test enhanced memory monitor functionality"""
    print("\n🦈 Testing Enhanced Memory Monitor...")
    
    try:
        from enhanced_memory_monitor import MemoryOptimizedTSharkMonitor
        
        # Test initialization
        monitor = MemoryOptimizedTSharkMonitor()
        print("✅ Monitor initialization successful")
        
        # Test system status
        status = monitor.get_system_status()
        if status and 'system' in status:
            print("✅ System status retrieval successful")
            print(f"   Memory: {status['system']['memory_percent']:.1f}%")
            print(f"   Disk: {status['system']['disk_percent']:.1f}%")
            print(f"   Active processes: {status['captures']['active_processes']}")
        else:
            print("❌ System status retrieval failed")
            return False
        
        # Test configuration loading
        if hasattr(monitor, 'config'):
            print("✅ Configuration system working")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced monitor test failed: {e}")
        return False

def test_simple_monitor():
    """Test simple monitor functionality"""
    print("\n🎯 Testing Simple Monitor...")
    
    try:
        from simple_tshark_monitor import SimpleTsharkMonitor
        
        # Test with temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            monitor = SimpleTsharkMonitor(tmpdir)
            print("✅ Simple monitor initialization successful")
            
            # Test status method
            status = monitor.get_status()
            if status and 'timestamp' in status:
                print("✅ Status method working")
                print(f"   Active captures: {status['active_captures']}")
            else:
                print("❌ Status method failed")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Simple monitor test failed: {e}")
        return False

def test_gui_components():
    """Test GUI components (without launching)"""
    print("\n🖥️  Testing GUI Components...")
    
    try:
        import PyQt6
        from PyQt6.QtWidgets import QApplication
        
        # Test if we can create QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        print("✅ PyQt6 application framework working")
        
        # Test GUI module import
        try:
            from gui_memory_monitor import TSharkMonitorGUI
            print("✅ GUI module import successful")
        except Exception as e:
            print(f"❌ GUI module import failed: {e}")
            return False
        
        return True
        
    except ImportError:
        print("⚠️  PyQt6 not available - skipping GUI tests")
        return True
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

def test_file_structure():
    """Test file structure and permissions"""
    print("\n📁 Testing File Structure...")
    
    base_dir = Path(__file__).parent
    required_files = [
        'README.md',
        'INSTALL.md', 
        'requirements.txt',
        'setup.py',
        'enhanced_memory_monitor.py',
        'simple_tshark_monitor.py',
        'gui_memory_monitor.py',
        'launch_cli.command',
        'launch_gui.command'
    ]
    
    missing_files = []
    for file in required_files:
        file_path = base_dir / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (missing)")
            missing_files.append(file)
    
    # Test launcher permissions
    for launcher in ['launch_cli.command', 'launch_gui.command']:
        launcher_path = base_dir / launcher
        if launcher_path.exists():
            if os.access(launcher_path, os.X_OK):
                print(f"✅ {launcher} (executable)")
            else:
                print(f"⚠️  {launcher} (not executable)")
    
    return len(missing_files) == 0

def test_configuration():
    """Test configuration system"""
    print("\n⚙️  Testing Configuration...")
    
    try:
        # Test config file creation
        config_path = Path(__file__).parent / 'test_config.json'
        test_config = {
            "max_memory_gb": 8,
            "max_disk_gb": 50,
            "cleanup_threshold": 0.8,
            "check_interval_seconds": 30
        }
        
        with open(config_path, 'w') as f:
            json.dump(test_config, f, indent=2)
        
        # Test config loading
        with open(config_path, 'r') as f:
            loaded_config = json.load(f)
        
        if loaded_config == test_config:
            print("✅ Configuration file handling working")
        else:
            print("❌ Configuration file handling failed")
            return False
        
        # Cleanup
        config_path.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def run_diagnostic_mode():
    """Run diagnostic mode test"""
    print("\n🔍 Running Diagnostic Mode...")
    
    try:
        from enhanced_memory_monitor import MemoryOptimizedTSharkMonitor
        
        print("Creating monitor instance...")
        monitor = MemoryOptimizedTSharkMonitor()
        
        print("Getting system status...")
        status = monitor.get_system_status()
        
        print("\n📊 System Diagnostic Results:")
        print(f"Memory Total: {status['system']['memory_total_gb']:.1f} GB")
        print(f"Memory Used: {status['system']['memory_used_gb']:.1f} GB")
        print(f"Memory Usage: {status['system']['memory_percent']:.1f}%")
        print(f"Disk Total: {status['system']['disk_total_gb']:.1f} GB") 
        print(f"Disk Used: {status['system']['disk_used_gb']:.1f} GB")
        print(f"Disk Usage: {status['system']['disk_percent']:.1f}%")
        
        # Check thresholds
        if status['system']['memory_percent'] > 90:
            print("⚠️  HIGH MEMORY USAGE WARNING")
        if status['system']['disk_percent'] > 85:
            print("⚠️  HIGH DISK USAGE WARNING")
        
        return True
        
    except Exception as e:
        print(f"❌ Diagnostic mode failed: {e}")
        return False

def main():
    """Main test runner"""
    print("🦈 StealthShark Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("System Requirements", test_system_requirements),
        ("Enhanced Monitor", test_enhanced_monitor),
        ("Simple Monitor", test_simple_monitor),
        ("GUI Components", test_gui_components),
        ("File Structure", test_file_structure),
        ("Configuration", test_configuration),
        ("Diagnostic Mode", run_diagnostic_mode)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"🏁 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! StealthShark is ready for use.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
