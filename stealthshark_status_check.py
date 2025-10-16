#!/usr/bin/env python3
"""
StealthShark Status Check and Diagnostic Tool
Comprehensive system check for StealthShark components
"""

import sys
import os
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Setup verbose logging as per user requirements
def setup_logging():
    """Setup verbose logging for debugging and tracking"""
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"stealthshark_status_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("StealthShark Status Check initialized")
    logger.info(f"Log file: {log_file}")
    return logger

def check_python_dependencies(logger):
    """Check if all required Python packages are available"""
    logger.info("Checking Python dependencies...")
    
    dependencies = {
        'psutil': 'System and process utilities',
        'PyQt6': 'GUI framework',
        'subprocess': 'Process management (built-in)',
        'threading': 'Threading support (built-in)',
        'pathlib': 'Path utilities (built-in)',
        'json': 'JSON handling (built-in)'
    }
    
    results = {}
    
    for package, description in dependencies.items():
        try:
            __import__(package)
            logger.info(f"✅ {package}: Available - {description}")
            results[package] = True
        except ImportError as e:
            logger.error(f"❌ {package}: Missing - {description} - Error: {e}")
            results[package] = False
    
    return results

def check_system_tools(logger):
    """Check if required system tools are available"""
    logger.info("Checking system tools...")
    
    tools = {
        'tshark': 'Wireshark command-line tool',
        'python3': 'Python 3 interpreter'
    }
    
    results = {}
    
    for tool, description in tools.items():
        try:
            result = subprocess.run([tool, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                logger.info(f"✅ {tool}: Available - {description} - {version}")
                results[tool] = True
            else:
                logger.error(f"❌ {tool}: Error running - {description}")
                results[tool] = False
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error(f"❌ {tool}: Not found - {description} - Error: {e}")
            results[tool] = False
    
    return results

def check_stealthshark_files(logger):
    """Check if StealthShark files are present and accessible"""
    logger.info("Checking StealthShark files...")
    
    required_files = {
        'StealthShark.command': 'Main launcher script',
        'persistent_wireshark_monitor.py': 'Persistent monitoring engine',
        'simple_tshark_monitor.py': 'Simple monitoring tool',
        'test_gui.py': 'GUI testing utility',
        'LoopbackShark/loopbackshark_gui.py': 'LoopbackShark GUI',
        'LoopbackShark/pattern_recognition.py': 'Pattern recognition engine',
        'requirements.txt': 'Python dependencies list'
    }
    
    results = {}
    
    for file_path, description in required_files.items():
        path = Path(file_path)
        if path.exists():
            logger.info(f"✅ {file_path}: Found - {description}")
            results[file_path] = True
        else:
            logger.error(f"❌ {file_path}: Missing - {description}")
            results[file_path] = False
    
    return results

def check_network_interfaces(logger):
    """Check available network interfaces"""
    logger.info("Checking network interfaces...")
    
    try:
        import psutil
        interfaces = psutil.net_if_addrs()
        
        logger.info(f"Found {len(interfaces)} network interfaces:")
        for iface, addrs in interfaces.items():
            logger.info(f"  - {iface}: {len(addrs)} addresses")
            for addr in addrs:
                logger.debug(f"    {addr.family.name}: {addr.address}")
        
        return True
    except Exception as e:
        logger.error(f"Error checking network interfaces: {e}")
        return False

def check_permissions(logger):
    """Check if we have necessary permissions"""
    logger.info("Checking permissions...")
    
    # Check if we can create directories and files
    test_dir = Path("./test_permissions")
    try:
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / "test.txt"
        test_file.write_text("test")
        test_file.unlink()
        test_dir.rmdir()
        logger.info("✅ File system permissions: OK")
        return True
    except Exception as e:
        logger.error(f"❌ File system permissions: Error - {e}")
        return False

def run_component_tests(logger):
    """Run basic tests on StealthShark components"""
    logger.info("Running component tests...")
    
    tests = {
        'persistent_monitor_help': ['python3', 'persistent_wireshark_monitor.py', '--help'],
        'loopbackshark_import': ['python3', '-c', 'import sys; sys.path.append("LoopbackShark"); from pattern_recognition import PatternRecognitionEngine; print("Import successful")']
    }
    
    results = {}
    
    for test_name, command in tests.items():
        try:
            logger.info(f"Running test: {test_name}")
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"✅ {test_name}: PASSED")
                logger.debug(f"Output: {result.stdout[:200]}...")
                results[test_name] = True
            else:
                logger.error(f"❌ {test_name}: FAILED - Return code: {result.returncode}")
                logger.error(f"Error: {result.stderr}")
                results[test_name] = False
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results[test_name] = False
    
    return results

def generate_report(logger, all_results):
    """Generate comprehensive status report"""
    logger.info("Generating status report...")
    
    total_checks = sum(len(results) for results in all_results.values())
    passed_checks = sum(sum(1 for result in results.values() if result) for results in all_results.values())
    
    logger.info("=" * 60)
    logger.info("STEALTHSHARK STATUS REPORT")
    logger.info("=" * 60)
    logger.info(f"Overall Status: {passed_checks}/{total_checks} checks passed ({passed_checks/total_checks*100:.1f}%)")
    logger.info("")
    
    for category, results in all_results.items():
        category_passed = sum(1 for result in results.values() if result)
        category_total = len(results)
        status = "✅ PASS" if category_passed == category_total else "❌ ISSUES"
        
        logger.info(f"{category.upper()}: {status} ({category_passed}/{category_total})")
        
        for item, result in results.items():
            status_icon = "✅" if result else "❌"
            logger.info(f"  {status_icon} {item}")
    
    logger.info("")
    
    if passed_checks == total_checks:
        logger.info("🎉 All systems operational! StealthShark is ready to use.")
        return True
    else:
        logger.warning("⚠️  Some issues detected. Check the log above for details.")
        return False

def main():
    """Main status check function"""
    logger = setup_logging()
    
    logger.info("Starting comprehensive StealthShark status check...")
    
    # Run all checks
    all_results = {
        'python_dependencies': check_python_dependencies(logger),
        'system_tools': check_system_tools(logger),
        'stealthshark_files': check_stealthshark_files(logger),
        'permissions': {'file_system': check_permissions(logger)},
        'network_interfaces': {'interface_detection': check_network_interfaces(logger)},
        'component_tests': run_component_tests(logger)
    }
    
    # Generate report
    success = generate_report(logger, all_results)
    
    logger.info("Status check completed.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
