#!/usr/bin/env python3
"""
StealthShark + NFC Combined Application - Core Methods
Supporting methods for the combined application
"""

import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class StealthSharkNFCMethods:
    """Core methods for StealthShark + NFC combined application"""
    
    def create_monitoring_panel(self):
        """Create the monitoring panel with tabs"""
        monitor_widget = QWidget()
        layout = QVBoxLayout(monitor_widget)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # StealthShark Activity Tab
        activity_tab = QWidget()
        activity_layout = QVBoxLayout(activity_tab)
        
        # Active captures table
        captures_group = QGroupBox("Active Packet Captures")
        captures_layout = QVBoxLayout(captures_group)
        
        self.captures_table = QTableWidget()
        self.captures_table.setColumnCount(4)
        self.captures_table.setHorizontalHeaderLabels(["Interface", "Start Time", "Duration", "File"])
        captures_layout.addWidget(self.captures_table)
        
        activity_layout.addWidget(captures_group)
        
        # Interface activity table
        interfaces_group = QGroupBox("Interface Activity")
        interfaces_layout = QVBoxLayout(interfaces_group)
        
        self.interfaces_table = QTableWidget()
        self.interfaces_table.setColumnCount(5)
        self.interfaces_table.setHorizontalHeaderLabels(["Interface", "Packets", "Bytes", "Last Activity", "Status"])
        interfaces_layout.addWidget(self.interfaces_table)
        
        activity_layout.addWidget(interfaces_group)
        
        self.tab_widget.addTab(activity_tab, "🦈 StealthShark")
        
        # WiFi Security Tab
        wifi_tab = QWidget()
        wifi_layout = QVBoxLayout(wifi_tab)
        
        # Current network status
        network_group = QGroupBox("Current Network Status")
        network_layout = QVBoxLayout(network_group)
        
        self.current_ssid_label = QLabel("SSID: Checking...")
        self.current_bssid_label = QLabel("BSSID: Checking...")
        self.security_status_label = QLabel("Security: Checking...")
        
        network_layout.addWidget(self.current_ssid_label)
        network_layout.addWidget(self.current_bssid_label)
        network_layout.addWidget(self.security_status_label)
        
        wifi_layout.addWidget(network_group)
        
        # Detected networks table
        networks_group = QGroupBox("Detected Networks")
        networks_layout = QVBoxLayout(networks_group)
        
        self.networks_table = QTableWidget()
        self.networks_table.setColumnCount(5)
        self.networks_table.setHorizontalHeaderLabels(["SSID", "BSSID", "RSSI", "Security", "Threat"])
        networks_layout.addWidget(self.networks_table)
        
        wifi_layout.addWidget(networks_group)
        
        self.tab_widget.addTab(wifi_tab, "📡 WiFi Security")
        
        # Logs Tab
        logs_tab = QWidget()
        logs_layout = QVBoxLayout(logs_tab)
        
        logs_group = QGroupBox("System Logs")
        logs_group_layout = QVBoxLayout(logs_group)
        
        # Log controls
        log_controls = QHBoxLayout()
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self.clear_logs)
        export_btn = QPushButton("💾 Export")
        export_btn.clicked.connect(self.export_logs)
        log_controls.addWidget(clear_btn)
        log_controls.addWidget(export_btn)
        log_controls.addStretch()
        logs_group_layout.addLayout(log_controls)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        logs_group_layout.addWidget(self.log_text)
        
        logs_layout.addWidget(logs_group)
        self.tab_widget.addTab(logs_tab, "📝 Logs")
        
        layout.addWidget(self.tab_widget)
        
        return monitor_widget
    
    def setup_timers(self):
        """Setup update timers"""
        # UI update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # Update every second
        
        # Network scan timer
        self.network_timer = QTimer()
        self.network_timer.timeout.connect(self.update_network_status)
        self.network_timer.start(10000)  # Update every 10 seconds
        
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)
        print(formatted_message)
        
    def load_registered_tags(self):
        """Load registered NFC tags"""
        try:
            if self.tags_path.exists():
                with open(self.tags_path, 'r') as f:
                    self.registered_tags = json.load(f)
                self.log_message(f"📱 Loaded {len(self.registered_tags)} registered NFC tags")
            else:
                self.registered_tags = []
                self.log_message("📱 No registered NFC tags found")
        except Exception as e:
            self.registered_tags = []
            self.log_message(f"⚠️ Error loading NFC tags: {e}")
    
    def save_registered_tags(self):
        """Save registered NFC tags"""
        try:
            with open(self.tags_path, 'w') as f:
                json.dump(self.registered_tags, f, indent=2)
        except Exception as e:
            self.log_message(f"⚠️ Error saving NFC tags: {e}")
    
    def load_authentication(self):
        """Load authentication state"""
        try:
            if self.auth_profile_path.exists():
                with open(self.auth_profile_path, 'r') as f:
                    auth_data = json.load(f)
                    self.authenticated = auth_data.get('authenticated', False)
                    self.firewall_enabled = auth_data.get('firewall_enabled', False)
                    self.log_message(f"🔐 Authentication state loaded: {'Authenticated' if self.authenticated else 'Not authenticated'}")
        except Exception as e:
            self.log_message(f"⚠️ Error loading authentication: {e}")
    
    def save_authentication(self):
        """Save authentication state"""
        try:
            auth_data = {
                'authenticated': self.authenticated,
                'firewall_enabled': self.firewall_enabled,
                'last_auth': datetime.now().isoformat()
            }
            with open(self.auth_profile_path, 'w') as f:
                json.dump(auth_data, f, indent=2)
        except Exception as e:
            self.log_message(f"⚠️ Error saving authentication: {e}")
    
    def check_auto_authentication(self):
        """Check for auto-authentication on startup"""
        current_bssid = self.get_current_bssid()
        if current_bssid:
            matching_tags = [tag for tag in self.registered_tags 
                           if 'network_binding' in tag and 
                           tag['network_binding']['bssid'] == current_bssid]
            
            if matching_tags:
                self.authenticated = True
                self.firewall_enabled = True
                self.save_authentication()
                self.update_auth_status(True)
                self.log_message(f"🔐 Auto-authenticated via network-bound NFC tag")
    
    def get_current_bssid(self):
        """Get current WiFi BSSID"""
        try:
            result = subprocess.run(['airport', '-I'], capture_output=True, text=True, timeout=5)
            for line in result.stdout.split('\n'):
                if 'BSSID:' in line:
                    return line.split('BSSID:')[1].strip()
        except Exception:
            pass
        return None
    
    def authenticate_nfc(self):
        """Simulate NFC authentication"""
        self.log_message("📱 NFC authentication requested...")
        
        # Simulate NFC tag read
        QTimer.singleShot(2000, self.complete_nfc_auth)
    
    def complete_nfc_auth(self):
        """Complete NFC authentication"""
        self.authenticated = True
        self.save_authentication()
        self.update_auth_status(True)
        self.log_message("✅ NFC authentication successful")
        
        # Enable monitoring controls
        self.start_btn.setEnabled(True)
        self.firewall_btn.setEnabled(True)
        
    def update_auth_status(self, authenticated):
        """Update authentication status display"""
        if authenticated:
            self.auth_status_label.setText("🔓 Authenticated")
            self.auth_status_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14px;")
            self.nfc_auth_btn.setEnabled(False)
            self.logout_btn.setEnabled(True)
        else:
            self.auth_status_label.setText("🔒 Not Authenticated")
            self.auth_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 14px;")
            self.nfc_auth_btn.setEnabled(True)
            self.logout_btn.setEnabled(False)
    
    def logout(self):
        """Logout and disable features"""
        self.authenticated = False
        self.firewall_enabled = False
        self.save_authentication()
        self.update_auth_status(False)
        
        # Stop monitoring if running
        if self.monitor_thread and self.monitor_thread.isRunning():
            self.stop_monitor()
        
        # Disable controls
        self.start_btn.setEnabled(False)
        self.firewall_btn.setEnabled(False)
        
        self.log_message("🚪 Logged out - monitoring disabled")
    
    def toggle_firewall(self):
        """Toggle firewall state"""
        if not self.authenticated:
            self.log_message("⚠️ Authentication required for firewall control")
            return
            
        self.firewall_enabled = not self.firewall_enabled
        self.save_authentication()
        
        if self.firewall_enabled:
            self.firewall_btn.setText("🛡️ Disable Firewall")
            self.firewall_btn.setStyleSheet("background-color: #f44336;")
            self.log_message("🛡️ Firewall enabled")
        else:
            self.firewall_btn.setText("🛡️ Enable Firewall")
            self.firewall_btn.setStyleSheet("background-color: #4CAF50;")
            self.log_message("🛡️ Firewall disabled")
    
    def start_monitor(self):
        """Start the StealthShark monitor"""
        if not self.authenticated:
            self.log_message("⚠️ NFC authentication required to start monitoring")
            QMessageBox.warning(self, "Authentication Required", 
                              "Please authenticate with NFC tag before starting monitor.")
            return
            
        if self.monitor_thread and self.monitor_thread.isRunning():
            return
            
        self.log_message("🚀 Starting StealthShark Monitor...")
        
        # Create and start monitor thread
        from stealthshark_nfc_combined import StealthSharkMonitorThread
        self.monitor_thread = StealthSharkMonitorThread(
            self.capture_dir, self.duration, self.interval
        )
        
        # Connect signals
        self.monitor_thread.alert_signal.connect(self.on_alert)
        self.monitor_thread.batch_alert_signal.connect(self.on_batch_alert)
        
        self.monitor_thread.start()
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Status: Running")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
        # Start network monitoring
        self.start_network_monitoring()
        
    def stop_monitor(self):
        """Stop the monitor"""
        if self.monitor_thread:
            self.log_message("🛑 Stopping StealthShark Monitor...")
            self.monitor_thread.stop()
            self.monitor_thread.wait(5000)
            self.monitor_thread = None
            
        # Stop network monitoring
        self.stop_network_monitoring()
            
        # Update UI
        self.start_btn.setEnabled(self.authenticated)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Status: Stopped")
        self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        
        self.log_message("✅ Monitor stopped")
    
    def start_network_monitoring(self):
        """Start WiFi network monitoring"""
        if self.network_monitor_thread and self.network_monitor_thread.isRunning():
            return
            
        from stealthshark_nfc_combined import NetworkMonitorThread
        self.network_monitor_thread = NetworkMonitorThread(self.legitimate_bssid)
        self.network_monitor_thread.network_update.connect(self.on_network_update)
        self.network_monitor_thread.threat_detected.connect(self.on_threat_detected)
        self.network_monitor_thread.start()
        
        self.log_message("📡 WiFi network monitoring started")
    
    def stop_network_monitoring(self):
        """Stop WiFi network monitoring"""
        if self.network_monitor_thread:
            self.network_monitor_thread.stop()
            self.network_monitor_thread.wait(3000)
            self.network_monitor_thread = None
            self.log_message("📡 WiFi network monitoring stopped")
    
    def on_network_update(self, networks):
        """Handle network updates"""
        self.current_networks = networks
        self.update_networks_table()
        
        # Update current network status
        current_ssid = self.get_current_ssid()
        current_bssid = self.get_current_bssid()
        
        self.current_ssid_label.setText(f"SSID: {current_ssid}")
        self.current_bssid_label.setText(f"BSSID: {current_bssid}")
        
        # Check security status
        if current_bssid == self.legitimate_bssid:
            self.security_status_label.setText("Security: ✅ Legitimate Network")
            self.security_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.security_status_label.setText("Security: ⚠️ Unknown Network")
            self.security_status_label.setStyleSheet("color: #FFA500; font-weight: bold;")
    
    def on_threat_detected(self, threat):
        """Handle threat detection"""
        self.threat_count += 1
        self.threat_label.setText(f"🚨 Threats detected: {self.threat_count}")
        
        threat_msg = f"🚨 THREAT DETECTED: {threat['ssid']} ({threat['bssid']})"
        self.log_message(threat_msg)
        
        # Add to blocked BSSIDs
        self.blocked_bssids.add(threat['bssid'])
    
    def update_networks_table(self):
        """Update the networks table"""
        self.networks_table.setRowCount(len(self.current_networks))
        
        for row, network in enumerate(self.current_networks):
            self.networks_table.setItem(row, 0, QTableWidgetItem(network['ssid']))
            self.networks_table.setItem(row, 1, QTableWidgetItem(network['bssid']))
            self.networks_table.setItem(row, 2, QTableWidgetItem(f"{network['rssi']} dBm"))
            self.networks_table.setItem(row, 3, QTableWidgetItem(network['security']))
            
            # Threat status
            is_threat = network['bssid'] in self.blocked_bssids
            threat_text = "🚨 THREAT" if is_threat else "✅ Safe"
            threat_item = QTableWidgetItem(threat_text)
            
            if is_threat:
                threat_item.setBackground(QColor(244, 67, 54, 100))
            else:
                threat_item.setBackground(QColor(76, 175, 80, 100))
                
            self.networks_table.setItem(row, 4, threat_item)
    
    def scan_networks(self):
        """Scan for available WiFi networks using networksetup"""
        try:
            # Use networksetup for WiFi scanning (more reliable on macOS)
            result = subprocess.run(['networksetup', '-listallhardwareports'], 
                                  capture_output=True, text=True, timeout=10)
            
            # Get WiFi interface name
            wifi_interface = 'en0'  # Default
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for i, line in enumerate(lines):
                    if 'Wi-Fi' in line and i + 1 < len(lines):
                        device_line = lines[i + 1]
                        if 'Device:' in device_line:
                            wifi_interface = device_line.split('Device: ')[1].strip()
                            break
            
            # Scan for networks using system_profiler (more reliable than airport)
            result = subprocess.run(['system_profiler', 'SPAirPortDataType'], 
                                  capture_output=True, text=True, timeout=15)
            
            networks = []
            if result.returncode == 0:
                # Parse system_profiler output for network info
                lines = result.stdout.split('\n')
                current_network = {}
                
                for line in lines:
                    line = line.strip()
                    if 'Networks:' in line:
                        continue
                    elif line and ':' in line and not line.startswith('Interfaces:'):
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == 'SSID':
                            if current_network:
                                networks.append(current_network)
                            current_network = {'ssid': value}
                        elif key == 'BSSID':
                            current_network['bssid'] = value
                        elif key == 'RSSI':
                            try:
                                current_network['rssi'] = int(value.split()[0])
                            except:
                                current_network['rssi'] = -50
                        elif key == 'Security':
                            current_network['security'] = value
                
                if current_network:
                    networks.append(current_network)
            
            # If no networks found, add current network info
            if not networks:
                current_ssid = self.get_current_ssid()
                current_bssid = self.get_current_bssid()
                if current_ssid != "Disconnected":
                    networks.append({
                        'ssid': current_ssid,
                        'bssid': current_bssid or 'Unknown',
                        'rssi': -40,
                        'security': 'WPA2'
                    })
            
            return networks
            
        except Exception as e:
            print(f"Network scan error: {e}")
            return []
    
    def get_current_ssid(self):
        """Get current WiFi SSID"""
        try:
            result = subprocess.run(['networksetup', '-getairportnetwork', 'en0'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                output = result.stdout.strip()
                if "Current Wi-Fi Network:" in output:
                    ssid = output.split("Current Wi-Fi Network: ")[1].strip()
                    if ssid and "not associated" not in ssid.lower():
                        return ssid
            return "Disconnected"
        except Exception:
            return "Unknown"
    
    def update_network_status(self):
        """Update network status display"""
        current_ssid = self.get_current_ssid()
        current_bssid = self.get_current_bssid()
        
        if hasattr(self, 'current_ssid_label'):
            self.current_ssid_label.setText(f"SSID: {current_ssid}")
            self.current_bssid_label.setText(f"BSSID: {current_bssid or 'Unknown'}")
    
    def update_display(self):
        """Update the display"""
        # Placeholder for display updates
        pass
    
    def on_alert(self, message):
        """Handle single alert"""
        self.log_message(f"🚨 {message}")
    
    def on_batch_alert(self, messages):
        """Handle batch alerts"""
        for message in messages:
            self.log_message(f"🦈 {message}")
    
    def clear_logs(self):
        """Clear the log display"""
        self.log_text.clear()
        self.log_message("🗑️ Logs cleared")
    
    def export_logs(self):
        """Export logs to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stealthshark_nfc_logs_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(self.log_text.toPlainText())
            self.log_message(f"💾 Logs exported to {filename}")
        except Exception as e:
            self.log_message(f"⚠️ Export failed: {e}")
    
    def update_duration(self, text):
        """Update capture duration"""
        duration_map = {
            "1 minute (60s)": 60,
            "5 minutes (300s)": 300,
            "15 minutes (900s)": 900,
            "30 minutes (1800s)": 1800,
            "1 hour (3600s)": 3600,
            "2 hours (7200s)": 7200,
            "5 hours (18000s)": 18000
        }
        self.duration = duration_map.get(text, 3600)
        self.log_message(f"⏱️ Capture duration set to {text}")
    
    def update_interval(self, value):
        """Update check interval"""
        self.interval = value
        self.interval_label.setText(f"{value} seconds")
        self.log_message(f"⏱️ Check interval set to {value} seconds")
    
    def select_directory(self):
        """Select capture directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Capture Directory")
        if directory:
            self.capture_dir = Path(directory)
            self.dir_label.setText(str(self.capture_dir))
            self.log_message(f"📁 Capture directory set to {self.capture_dir}")
