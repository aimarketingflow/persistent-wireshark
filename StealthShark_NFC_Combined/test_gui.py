#!/usr/bin/env python3
"""Test the complete StealthShark NFC Combined GUI"""

import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from stealthshark_nfc_combined import StealthSharkNFCCombined

def test_gui():
    """Test the GUI with monitoring functionality"""
    print("=== Testing StealthShark NFC Combined GUI ===\n")
    
    app = QApplication(sys.argv)
    window = StealthSharkNFCCombined()
    
    # Simulate NFC authentication for testing
    print("🔑 Simulating NFC authentication...")
    window.complete_nfc_auth()
    
    # Show the window
    window.show()
    
    # Auto-close after 30 seconds for testing
    QTimer.singleShot(30000, app.quit)
    
    print("🦈 GUI launched - will auto-close in 30 seconds")
    print("📊 Check the StealthShark tab for monitoring activity")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_gui())
