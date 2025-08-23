#!/usr/bin/env python3
"""
Wireshark Monitor GUI
PyQt6-based interface for persistent network monitoring and packet capture
"""

import sys
import json
import threading
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QTextEdit, QTableWidget, 
                            QTableWidgetItem, QProgressBar, QGroupBox, QLineEdit,
                            QCheckBox, QSpinBox, QTabWidget, QMessageBox, QComboBox,
                            QSlider, QFileDialog, QListWidget, QSplitter)
from PyQt6.QtCore import QTimer, QThread, pyqtSignal, Qt, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap, QIcon
import psutil
from persistent_wireshark_monitor import PersistentWiresharkMonitor

class MonitorThread(QThread):
    """Background thread for running the Wireshark monitor"""
    interface_activity = pyqtSignal(str, dict)
    capture_started = pyqtSignal(str, str)
    capture_completed = pyqtSignal(str, str)
    status_update = pyqtSignal(dict)
    alert_signal = pyqtSignal(str)
    
    def __init__(self, capture_dir, duration, interval):
        super().__init__()
        self.capture_dir = capture_dir
        self.duration = duration
        self.interval = interval
        self.monitor = None
        self.running = False
        
    def alert_callback(self, message):
        """Callback for monitor alerts"""
        self.alert_signal.emit(message)
        
    def run(self):
        """Run the monitor in background thread"""
        self.running = True
        self.monitor = PersistentWiresharkMonitor(
            capture_dir=self.capture_dir,
            capture_duration=self.duration,
            check_interval=self.interval,
            alert_callback=self.alert_callback
        )
        
        # Override some methods to emit signals
        original_start_capture = self.monitor.start_capture
        original_monitor_capture = self.monitor.monitor_capture
        
        def enhanced_start_capture(interface):
            result = original_start_capture(interface)
            if interface in self.monitor.active_captures:
                capture_info = self.monitor.active_captures[interface]
                self.capture_started.emit(interface, str(capture_info['capture_file']))
            return result
            
        def enhanced_monitor_capture(interface):
            original_monitor_capture(interface)
            # Emit completion signal when capture finishes
            self.capture_completed.emit(interface, f"Capture on {interface} completed")
            
        self.monitor.start_capture = enhanced_start_capture
        self.monitor.monitor_capture = enhanced_monitor_capture
        
        try:
            self.monitor.run()
        except Exception as e:
            self.alert_signal.emit(f"Monitor error: {e}")
            
    def stop(self):
        """Stop the monitor"""
        self.running = False
        if self.monitor:
            self.monitor.running = False
            self.monitor.shutdown()

class WiresharkMonitorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.monitor_thread = None
        self.capture_dir = Path("./pcap_captures")
        self.duration = 3600  # 1 hour default
        self.interval = 5     # 5 seconds default
        
        self.init_ui()
        self.setup_timers()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Persistent Wireshark Monitor - AIMF LLC")
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: #3c3c3c;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
            QTextEdit, QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                color: #ffffff;
                font-family: 'Courier New', monospace;
            }
            QTableWidget {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                color: #ffffff;
                gridline-color: #555555;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #4CAF50;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit, QSpinBox, QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                color: #ffffff;
                padding: 5px;
                border-radius: 3px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #555555;
                height: 8px;
                background: #1e1e1e;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #555555;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
        
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Controls
        left_panel = self.create_control_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Monitoring
        right_panel = self.create_monitoring_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 800])
        
    def create_control_panel(self):
        """Create the control panel"""
        control_widget = QWidget()
        layout = QVBoxLayout(control_widget)
        
        # Monitor Control Group
        control_group = QGroupBox("Monitor Control")
        control_layout = QVBoxLayout(control_group)
        
        # Start/Stop buttons
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("🚀 Start Monitor")
        self.start_btn.clicked.connect(self.start_monitor)
        self.stop_btn = QPushButton("🛑 Stop Monitor")
        self.stop_btn.clicked.connect(self.stop_monitor)
        self.stop_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        control_layout.addLayout(button_layout)
        
        # Status indicator
        self.status_label = QLabel("Status: Stopped")
        self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        control_layout.addWidget(self.status_label)
        
        layout.addWidget(control_group)
        
        # Configuration Group
        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout(config_group)
        
        # Capture duration
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Capture Duration:"))
        self.duration_combo = QComboBox()
        self.duration_combo.addItems([
            "1 minute (60s)", "5 minutes (300s)", "15 minutes (900s)",
            "30 minutes (1800s)", "1 hour (3600s)", "2 hours (7200s)",
            "5 hours (18000s)"
        ])
        self.duration_combo.setCurrentText("1 hour (3600s)")
        self.duration_combo.currentTextChanged.connect(self.update_duration)
        duration_layout.addWidget(self.duration_combo)
        config_layout.addLayout(duration_layout)
        
        # Check interval
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Check Interval:"))
        self.interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setRange(1, 30)
        self.interval_slider.setValue(5)
        self.interval_slider.valueChanged.connect(self.update_interval)
        self.interval_label = QLabel("5 seconds")
        interval_layout.addWidget(self.interval_slider)
        interval_layout.addWidget(self.interval_label)
        config_layout.addLayout(interval_layout)
        
        # Capture directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Capture Directory:"))
        self.dir_btn = QPushButton("📁 Select")
        self.dir_btn.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.dir_btn)
        config_layout.addLayout(dir_layout)
        
        self.dir_label = QLabel(str(self.capture_dir))
        self.dir_label.setWordWrap(True)
        config_layout.addWidget(self.dir_label)
        
        layout.addWidget(config_group)
        
        # Interface List Group
        interface_group = QGroupBox("Monitored Interfaces")
        interface_layout = QVBoxLayout(interface_group)
        
        self.interface_list = QListWidget()
        self.refresh_interfaces()
        interface_layout.addWidget(self.interface_list)
        
        refresh_btn = QPushButton("🔄 Refresh Interfaces")
        refresh_btn.clicked.connect(self.refresh_interfaces)
        interface_layout.addWidget(refresh_btn)
        
        layout.addWidget(interface_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        return control_widget
        
    def create_monitoring_panel(self):
        """Create the monitoring panel"""
        monitor_widget = QWidget()
        layout = QVBoxLayout(monitor_widget)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Activity Tab
        activity_tab = QWidget()
        activity_layout = QVBoxLayout(activity_tab)
        
        # Active captures table
        captures_group = QGroupBox("Active Captures")
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
        
        self.tab_widget.addTab(activity_tab, "📊 Activity")
        
        # Logs Tab
        logs_tab = QWidget()
        logs_layout = QVBoxLayout(logs_tab)
        
        logs_group = QGroupBox("Monitor Logs")
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
        
        # Files Tab
        files_tab = QWidget()
        files_layout = QVBoxLayout(files_tab)
        
        files_group = QGroupBox("Capture Files")
        files_group_layout = QVBoxLayout(files_group)
        
        # File controls
        file_controls = QHBoxLayout()
        refresh_files_btn = QPushButton("🔄 Refresh")
        refresh_files_btn.clicked.connect(self.refresh_files)
        open_folder_btn = QPushButton("📂 Open Folder")
        open_folder_btn.clicked.connect(self.open_capture_folder)
        file_controls.addWidget(refresh_files_btn)
        file_controls.addWidget(open_folder_btn)
        file_controls.addStretch()
        files_group_layout.addLayout(file_controls)
        
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(4)
        self.files_table.setHorizontalHeaderLabels(["File", "Size", "Created", "Status"])
        files_group_layout.addWidget(self.files_table)
        
        files_layout.addWidget(files_group)
        self.tab_widget.addTab(files_tab, "📁 Files")
        
        layout.addWidget(self.tab_widget)
        
        return monitor_widget
        
    def setup_timers(self):
        """Setup update timers"""
        # Update interface stats every 2 seconds
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_interface_stats)
        self.update_timer.start(2000)
        
        # Refresh files every 10 seconds
        self.files_timer = QTimer()
        self.files_timer.timeout.connect(self.refresh_files)
        self.files_timer.start(10000)
        
    def refresh_interfaces(self):
        """Refresh the interface list"""
        self.interface_list.clear()
        try:
            interfaces = list(psutil.net_if_addrs().keys())
            for interface in sorted(interfaces):
                self.interface_list.addItem(f"🔌 {interface}")
        except Exception as e:
            self.log_message(f"Error refreshing interfaces: {e}")
            
    def update_duration(self, text):
        """Update capture duration from combo box"""
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
        
    def update_interval(self, value):
        """Update check interval from slider"""
        self.interval = value
        self.interval_label.setText(f"{value} seconds")
        
    def select_directory(self):
        """Select capture directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Capture Directory")
        if directory:
            self.capture_dir = Path(directory)
            self.dir_label.setText(str(self.capture_dir))
            
    def start_monitor(self):
        """Start the monitor"""
        if self.monitor_thread and self.monitor_thread.isRunning():
            return
            
        self.log_message("🚀 Starting Wireshark Monitor...")
        self.log_message(f"📁 Capture Directory: {self.capture_dir}")
        self.log_message(f"⏱️ Duration: {self.duration/60:.1f} minutes")
        self.log_message(f"🔄 Check Interval: {self.interval} seconds")
        
        self.monitor_thread = MonitorThread(
            str(self.capture_dir), 
            self.duration, 
            self.interval
        )
        
        # Connect signals
        self.monitor_thread.interface_activity.connect(self.on_interface_activity)
        self.monitor_thread.capture_started.connect(self.on_capture_started)
        self.monitor_thread.capture_completed.connect(self.on_capture_completed)
        self.monitor_thread.status_update.connect(self.on_status_update)
        self.monitor_thread.alert_signal.connect(self.on_alert)
        
        self.monitor_thread.start()
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Status: Running")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
    def stop_monitor(self):
        """Stop the monitor"""
        if self.monitor_thread:
            self.log_message("🛑 Stopping Wireshark Monitor...")
            self.monitor_thread.stop()
            self.monitor_thread.wait(5000)  # Wait up to 5 seconds
            
        # Update UI
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Status: Stopped")
        self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        
    def update_interface_stats(self):
        """Update interface statistics table"""
        if not self.monitor_thread or not self.monitor_thread.isRunning():
            return
            
        try:
            stats = psutil.net_io_counters(pernic=True)
            
            self.interfaces_table.setRowCount(len(stats))
            
            for row, (interface, stat) in enumerate(stats.items()):
                self.interfaces_table.setItem(row, 0, QTableWidgetItem(interface))
                self.interfaces_table.setItem(row, 1, QTableWidgetItem(str(stat.packets_sent + stat.packets_recv)))
                self.interfaces_table.setItem(row, 2, QTableWidgetItem(f"{(stat.bytes_sent + stat.bytes_recv):,}"))
                self.interfaces_table.setItem(row, 3, QTableWidgetItem(datetime.now().strftime("%H:%M:%S")))
                
                # Status based on activity
                if stat.packets_sent + stat.packets_recv > 0:
                    status = "🟢 Active"
                else:
                    status = "⚪ Idle"
                self.interfaces_table.setItem(row, 4, QTableWidgetItem(status))
                
        except Exception as e:
            self.log_message(f"Error updating interface stats: {e}")
            
    def refresh_files(self):
        """Refresh capture files table"""
        files = []
        
        for subdir in ["active", "completed"]:
            subdir_path = self.capture_dir / subdir
            if subdir_path.exists():
                for pcap_file in subdir_path.glob("*.pcap*"):
                    try:
                        stat = pcap_file.stat()
                        files.append({
                            'name': pcap_file.name,
                            'size': stat.st_size,
                            'created': datetime.fromtimestamp(stat.st_ctime),
                            'status': subdir.title()
                        })
                    except:
                        pass
                        
        self.files_table.setRowCount(len(files))
        
        for row, file_info in enumerate(files):
            self.files_table.setItem(row, 0, QTableWidgetItem(file_info['name']))
            self.files_table.setItem(row, 1, QTableWidgetItem(f"{file_info['size']:,} bytes"))
            self.files_table.setItem(row, 2, QTableWidgetItem(file_info['created'].strftime("%Y-%m-%d %H:%M:%S")))
            self.files_table.setItem(row, 3, QTableWidgetItem(file_info['status']))
            
    def open_capture_folder(self):
        """Open capture folder in Finder"""
        try:
            subprocess.run(["open", str(self.capture_dir)], check=True)
        except Exception as e:
            self.log_message(f"Error opening folder: {e}")
            
    def clear_logs(self):
        """Clear the log display"""
        self.log_text.clear()
        
    def export_logs(self):
        """Export logs to file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", 
            f"wireshark_monitor_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt)"
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_text.toPlainText())
                self.log_message(f"📄 Logs exported to: {filename}")
            except Exception as e:
                self.log_message(f"Error exporting logs: {e}")
                
    def log_message(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def on_interface_activity(self, interface, stats):
        """Handle interface activity signal"""
        self.log_message(f"📡 Activity on {interface}: {stats}")
        
    def on_capture_started(self, interface, filename):
        """Handle capture started signal"""
        self.log_message(f"🎬 Started capture on {interface}: {filename}")
        
        # Update captures table
        row = self.captures_table.rowCount()
        self.captures_table.insertRow(row)
        self.captures_table.setItem(row, 0, QTableWidgetItem(interface))
        self.captures_table.setItem(row, 1, QTableWidgetItem(datetime.now().strftime("%H:%M:%S")))
        self.captures_table.setItem(row, 2, QTableWidgetItem(f"{self.duration/60:.1f} min"))
        self.captures_table.setItem(row, 3, QTableWidgetItem(Path(filename).name))
        
    def on_capture_completed(self, interface, message):
        """Handle capture completed signal"""
        self.log_message(f"✅ {message}")
        
    def on_status_update(self, status):
        """Handle status update signal"""
        self.log_message(f"📊 Status: {status}")
        
    def on_alert(self, message):
        """Handle alert signal"""
        self.log_message(f"🚨 ALERT: {message}")
        
        # Show popup notification
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Wireshark Monitor Alert")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        
    def closeEvent(self, event):
        """Handle window close event"""
        if self.monitor_thread and self.monitor_thread.isRunning():
            reply = QMessageBox.question(
                self, 'Confirm Exit',
                'Monitor is still running. Stop monitoring and exit?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_monitor()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Persistent Wireshark Monitor")
    
    # Set application icon if available
    try:
        app.setWindowIcon(QIcon("icon.png"))
    except:
        pass
        
    window = WiresharkMonitorGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
