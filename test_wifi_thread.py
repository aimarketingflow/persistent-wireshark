#!/usr/bin/env python3
"""
Test the WiFiThreatDetectorThread in isolation
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QListWidget, QLabel
from PyQt6.QtCore import QThread, pyqtSignal
import subprocess
import re
import time
from datetime import datetime

class WiFiThreatDetectorThread(QThread):
    """Thread for WiFi threat detection and pineapple scanning"""
    threat_detected = pyqtSignal(dict)
    wifi_networks = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.scan_interval = 10  # seconds
        
    def run(self):
        """Main threat detection loop"""
        self.running = True
        print("WiFi thread started!")
        while self.running:
            try:
                print(f"Scanning at {datetime.now()}")
                networks = self.scan_wifi_networks()
                print(f"Found {len(networks)} networks")
                self.wifi_networks.emit(networks)
                
                # Check for threats
                for network in networks:
                    if self.is_potential_threat(network):
                        print(f"THREAT: {network['ssid']}")
                        self.threat_detected.emit(network)
                
                time.sleep(self.scan_interval)
            except Exception as e:
                print(f"WiFi scan error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(30)  # Wait longer on error
    
    def scan_wifi_networks(self):
        """Scan for WiFi networks using system_profiler"""
        try:
            result = subprocess.run(
                ['system_profiler', 'SPAirPortDataType'],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            networks = []
            current_network = None
            in_other_networks = False
            
            for line in result.stdout.split('\n'):
                # Check if we're in the "Other Local Wi-Fi Networks" section
                if 'Other Local Wi-Fi Networks:' in line:
                    in_other_networks = True
                    continue
                
                # Stop if we hit another section
                if in_other_networks and line and not line.startswith(' '):
                    break
                
                if in_other_networks:
                    # Check for network name (SSID) - it's indented and ends with ':'
                    if line.strip() and line.strip().endswith(':') and '  ' in line[:20]:
                        # Save previous network if exists
                        if current_network and current_network.get('ssid'):
                            networks.append(current_network)
                        
                        # Start new network
                        ssid = line.strip().rstrip(':')
                        current_network = {
                            'ssid': ssid,
                            'channel': 'Unknown',
                            'security': 'Unknown',
                            'rssi': -100,
                            'bssid': 'Unknown',
                            'timestamp': datetime.now().isoformat()
                        }
                    
                    # Parse network properties
                    elif current_network:
                        if 'Channel:' in line:
                            # Extract channel info: "Channel: 157 (5GHz, 80MHz)"
                            match = re.search(r'Channel:\s+(\d+)\s+\(([^)]+)\)', line)
                            if match:
                                current_network['channel'] = f"{match.group(1)} ({match.group(2)})"
                        
                        elif 'Security:' in line:
                            security = line.split('Security:')[1].strip()
                            current_network['security'] = security if security else 'Open'
                        
                        elif 'Signal / Noise:' in line:
                            # Extract signal: "Signal / Noise: -39 dBm / -92 dBm"
                            match = re.search(r'Signal / Noise:\s+(-?\d+)\s+dBm', line)
                            if match:
                                current_network['rssi'] = int(match.group(1))
            
            # Add last network
            if current_network and current_network.get('ssid'):
                networks.append(current_network)
            
            return networks
            
        except Exception as e:
            print(f"Network scan error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def is_potential_threat(self, network):
        """Basic threat detection logic"""
        # Check for suspicious patterns
        suspicious_ssids = ['Free WiFi', 'Public', 'Guest', 'Open', 'Pineapple', 'xfinitywifi']
        
        # Check for open networks with suspicious names
        if network['security'] in ['Open', 'None', 'Unknown'] and any(sus.lower() in network['ssid'].lower() for sus in suspicious_ssids):
            return True
            
        # Check for very strong signal (potential evil twin)
        if network['rssi'] > -30:
            return True
            
        return False
    
    def stop_detection(self):
        """Stop threat detection"""
        self.running = False


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WiFi Thread Test")
        self.setGeometry(100, 100, 800, 600)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)
        
        self.status_label = QLabel("Status: Not started")
        layout.addWidget(self.status_label)
        
        self.start_btn = QPushButton("Start WiFi Scanning")
        self.start_btn.clicked.connect(self.start_scan)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop WiFi Scanning")
        self.stop_btn.clicked.connect(self.stop_scan)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        self.network_list = QListWidget()
        layout.addWidget(self.network_list)
        
        self.wifi_thread = None
        
    def start_scan(self):
        print("Starting WiFi scan...")
        self.status_label.setText("Status: Starting...")
        
        self.wifi_thread = WiFiThreatDetectorThread()
        self.wifi_thread.wifi_networks.connect(self.update_networks)
        self.wifi_thread.threat_detected.connect(self.handle_threat)
        self.wifi_thread.start()
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Status: Scanning...")
        
    def stop_scan(self):
        if self.wifi_thread:
            self.wifi_thread.stop_detection()
            self.wifi_thread.quit()
            self.wifi_thread.wait()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Status: Stopped")
        
    def update_networks(self, networks):
        print(f"GUI received {len(networks)} networks")
        self.network_list.clear()
        self.status_label.setText(f"Status: Found {len(networks)} networks")
        
        for network in networks:
            if network['security'] in ['Open', 'None', 'Unknown']:
                icon = "🔓"
            elif 'WPA' in network['security']:
                icon = "🔒"
            else:
                icon = "❓"
            
            text = f"{icon} {network['ssid']} | Ch: {network['channel']} | {network['rssi']}dBm | {network['security']}"
            self.network_list.addItem(text)
    
    def handle_threat(self, threat):
        print(f"THREAT DETECTED: {threat['ssid']}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
