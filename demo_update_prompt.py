#!/usr/bin/env python3
"""
Demo script to showcase the StealthShark GUI update prompt feature
"""

import sys
import subprocess
import json
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from wireshark_monitor_gui import UpdateDialog

def simulate_update_available():
    """Simulate an update being available by creating a mock response"""
    mock_update = {
        "update_available": True,
        "current_version": "v1.2.0",
        "latest_version": "v1.3.0",
        "message": "New features: Enhanced memory monitoring, Better error handling"
    }
    return mock_update

def demo_update_dialog():
    """Demonstrate the update dialog"""
    app = QApplication(sys.argv)
    
    # Get mock update info
    update_info = simulate_update_available()
    
    # Create and show the update dialog
    dialog = UpdateDialog(
        current_version=update_info["current_version"],
        latest_version=update_info["latest_version"],
        update_message=update_info["message"]
    )
    
    # Connect the buttons to demo handlers
    def on_install():
        print("\n✅ User clicked 'Install Update'")
        print("   The system would now:")
        print("   1. Back up current settings")
        print("   2. Pull latest changes from GitHub")
        print("   3. Update dependencies")
        print("   4. Restart the application")
        dialog.accept()
    
    def on_remind():
        print("\n⏰ User clicked 'Remind Me Later'")
        print("   Update check will be deferred")
        dialog.reject()
    
    dialog.install_button.clicked.disconnect()  # Remove default handler
    dialog.remind_button.clicked.disconnect()   # Remove default handler
    dialog.install_button.clicked.connect(on_install)
    dialog.remind_button.clicked.connect(on_remind)
    
    print("\n" + "="*70)
    print("🦈 StealthShark GUI Update Prompt Demo")
    print("="*70)
    print("\n📱 Showing update dialog with:")
    print(f"   Current Version: {update_info['current_version']}")
    print(f"   Latest Version: {update_info['latest_version']}")
    print(f"   Update Message: {update_info['message']}")
    print("\nThe dialog features:")
    print("   • Dark theme consistent with StealthShark UI")
    print("   • Clear version information")
    print("   • Install or defer options")
    print("   • Non-intrusive notification style")
    
    result = dialog.exec()
    
    if result:
        print("\n🎉 Update installation would proceed!")
    else:
        print("\n📅 Update deferred for later")
    
    print("\n" + "="*70)
    print("Demo completed!")
    print("="*70)
    
    sys.exit(0)

if __name__ == "__main__":
    demo_update_dialog()
