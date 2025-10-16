#!/usr/bin/env python3
"""
Enhanced Wireshark Monitor GUI
Advanced PyQt6-based network monitoring interface with comprehensive features
Based on StealthShark development logs and requirements
"""

import sys
import os
import json
import signal
import psutil
import threading
import time
import subprocess
import traceback
import logging
from datetime import datetime, timedelta
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QTextEdit, QSpinBox, 
                             QCheckBox, QComboBox, QProgressBar, QTabWidget,
                             QGroupBox, QTableWidget, QTableWidgetItem, QListWidget,
                             QSplitter, QGridLayout, QTreeWidget, QTreeWidgetItem,
                             QLineEdit, QFileDialog, QMessageBox, QStatusBar,
                             QMenuBar, QMenu, QSystemTrayIcon, QFrame)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt, QSize
from PyQt6.QtGui import QFont, QBrush, QColor, QPalette, QPixmap, QIcon, QAction

# Import our monitoring components
from persistent_wireshark_monitor import PersistentWiresharkMonitor
import simple_tshark_monitor

class MonitorThread(QThread):
    """Thread-safe network monitor with signals"""
    status_update = pyqtSignal(str)
    interface_update = pyqtSignal(dict)
    capture_update = pyqtSignal(str, str)  # interface, filename
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, capture_dir="./pcap_captures", duration=3600):
        super().__init__()
        self.logger = logging.getLogger("MonitorThread")
        self.capture_dir = capture_dir
        self.duration = duration
        self.running = False
        self.monitor = None
        
    def run(self):
        """Run network monitoring in thread"""
        try:
            self.running = True
            self.status_update.emit("Starting Enhanced Wireshark Monitor...")
            
            # Create monitor instance
            self.monitor = PersistentWiresharkMonitor(
                capture_dir=self.capture_dir,
                capture_duration=self.duration,
                alert_callback=self.handle_alert
            )
            
            self.status_update.emit("Monitor initialized successfully")
            
            # Start monitoring
            self.monitor.start_monitoring()
            
        except Exception as e:
            self.logger.error(f"Monitor thread error: {e}")
            self.error_signal.emit(f"Monitor error: {str(e)}")
        finally:
            self.finished_signal.emit()
    
    def handle_alert(self, message):
        """Handle monitoring alerts"""
        self.status_update.emit(f"ALERT: {message}")
    
    def stop_monitoring(self):
        """Stop monitoring gracefully"""
        self.running = False
        if self.monitor:
            self.monitor.stop_monitoring()

class SystemStatsWidget(QWidget):
    """System statistics display widget"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        layout = QGridLayout()
        
        # CPU Usage
        self.cpu_label = QLabel("CPU Usage:")
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setMaximum(100)
        layout.addWidget(self.cpu_label, 0, 0)
        layout.addWidget(self.cpu_progress, 0, 1)
        
        # Memory Usage
        self.memory_label = QLabel("Memory Usage:")
        self.memory_progress = QProgressBar()
        self.memory_progress.setMaximum(100)
        layout.addWidget(self.memory_label, 1, 0)
        layout.addWidget(self.memory_progress, 1, 1)
        
        # Disk Usage
        self.disk_label = QLabel("Disk Usage:")
        self.disk_progress = QProgressBar()
        self.disk_progress.setMaximum(100)
        layout.addWidget(self.disk_label, 2, 0)
        layout.addWidget(self.disk_progress, 2, 1)
        
        # Network Stats
        self.network_label = QLabel("Network I/O:")
        self.network_text = QLabel("0 KB/s ↑ | 0 KB/s ↓")
        layout.addWidget(self.network_label, 3, 0)
        layout.addWidget(self.network_text, 3, 1)
        
        self.setLayout(layout)
        
    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000)  # Update every 2 seconds
        
    def update_stats(self):
        """Update system statistics"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=None)
            self.cpu_progress.setValue(int(cpu_percent))
            self.cpu_label.setText(f"CPU Usage: {cpu_percent:.1f}%")
            
            # Memory
            memory = psutil.virtual_memory()
            self.memory_progress.setValue(int(memory.percent))
            self.memory_label.setText(f"Memory: {memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB)")
            
            # Disk
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.disk_progress.setValue(int(disk_percent))
            self.disk_label.setText(f"Disk: {disk_percent:.1f}% ({disk.used // (1024**3):.1f}GB)")
            
            # Network
            net_io = psutil.net_io_counters()
            if hasattr(self, 'prev_net_io'):
                bytes_sent = net_io.bytes_sent - self.prev_net_io.bytes_sent
                bytes_recv = net_io.bytes_recv - self.prev_net_io.bytes_recv
                self.network_text.setText(f"{bytes_sent // 1024:.0f} KB/s ↑ | {bytes_recv // 1024:.0f} KB/s ↓")
            self.prev_net_io = net_io
            
        except Exception as e:
            print(f"Stats update error: {e}")

class InterfaceWidget(QWidget):
    """Network interface monitoring widget"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.update_interfaces()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Interface list
        self.interface_table = QTableWidget()
        self.interface_table.setColumnCount(4)
        self.interface_table.setHorizontalHeaderLabels(["Interface", "Status", "IP Address", "Packets"])
        layout.addWidget(QLabel("Network Interfaces:"))
        layout.addWidget(self.interface_table)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Interfaces")
        refresh_btn.clicked.connect(self.update_interfaces)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
        
    def update_interfaces(self):
        """Update interface information"""
        try:
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            io_counters = psutil.net_io_counters(pernic=True)
            
            self.interface_table.setRowCount(len(interfaces))
            
            for row, (iface, addrs) in enumerate(interfaces.items()):
                # Interface name
                self.interface_table.setItem(row, 0, QTableWidgetItem(iface))
                
                # Status
                status = "Up" if stats.get(iface, {}).isup else "Down"
                self.interface_table.setItem(row, 1, QTableWidgetItem(status))
                
                # IP Address
                ip_addr = "N/A"
                for addr in addrs:
                    if addr.family.name == 'AF_INET':
                        ip_addr = addr.address
                        break
                self.interface_table.setItem(row, 2, QTableWidgetItem(ip_addr))
                
                # Packet count
                packets = io_counters.get(iface, {}).packets_sent or 0
                self.interface_table.setItem(row, 3, QTableWidgetItem(str(packets)))
                
        except Exception as e:
            print(f"Interface update error: {e}")

class EnhancedWiresharkGUI(QMainWindow):
    """Main Enhanced Wireshark Monitor GUI"""
    
    def __init__(self):
        super().__init__()
        self.monitor_thread = None
        self.setup_logging()
        self.setup_ui()
        self.setup_system_tray()
        self.apply_dark_theme()
        
    def setup_logging(self):
        """Setup GUI logging"""
        log_dir = Path("./gui_logs")
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"gui_debug_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("EnhancedGUI")
        self.logger.info("GUI logging initialized")
        
    def setup_ui(self):
        """Setup the main user interface"""
        self.setWindowTitle("🦈 StealthShark - Enhanced Network Monitor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left panel - Controls
        left_panel = self.create_control_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel - Monitoring
        right_panel = self.create_monitoring_panel()
        main_layout.addWidget(right_panel, 2)
        
        # Menu bar
        self.create_menu_bar()
        
        # Status bar
        self.statusBar().showMessage("Ready - StealthShark Enhanced Monitor")
        
    def create_control_panel(self):
        """Create the control panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Monitor Controls
        controls_group = QGroupBox("Monitor Controls")
        controls_layout = QVBoxLayout()
        
        # Start/Stop buttons
        self.start_btn = QPushButton("🚀 Start Monitoring")
        self.start_btn.clicked.connect(self.start_monitoring)
        self.stop_btn = QPushButton("⏹️ Stop Monitoring")
        self.stop_btn.clicked.connect(self.stop_monitoring)
        self.stop_btn.setEnabled(False)
        
        controls_layout.addWidget(self.start_btn)
        controls_layout.addWidget(self.stop_btn)
        
        # Duration setting
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration (seconds):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(60, 21600)  # 1 minute to 6 hours
        self.duration_spin.setValue(3600)  # Default 1 hour
        duration_layout.addWidget(self.duration_spin)
        controls_layout.addLayout(duration_layout)
        
        # Capture directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Capture Dir:"))
        self.dir_edit = QLineEdit("./pcap_captures")
        dir_btn = QPushButton("Browse")
        dir_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(dir_btn)
        controls_layout.addLayout(dir_layout)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # System Stats
        stats_group = QGroupBox("System Statistics")
        self.stats_widget = SystemStatsWidget()
        stats_layout = QVBoxLayout()
        stats_layout.addWidget(self.stats_widget)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Interface Info
        interface_group = QGroupBox("Network Interfaces")
        self.interface_widget = InterfaceWidget()
        interface_layout = QVBoxLayout()
        interface_layout.addWidget(self.interface_widget)
        interface_group.setLayout(interface_layout)
        layout.addWidget(interface_group)
        
        panel.setLayout(layout)
        return panel
        
    def create_monitoring_panel(self):
        """Create the monitoring panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Log tab
        log_tab = QWidget()
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 10))
        log_layout.addWidget(self.log_text)
        log_tab.setLayout(log_layout)
        self.tab_widget.addTab(log_tab, "📋 Monitor Log")
        
        # Capture Files tab
        files_tab = QWidget()
        files_layout = QVBoxLayout()
        self.files_list = QListWidget()
        files_layout.addWidget(QLabel("Captured Files:"))
        files_layout.addWidget(self.files_list)
        refresh_files_btn = QPushButton("Refresh Files")
        refresh_files_btn.clicked.connect(self.refresh_capture_files)
        files_layout.addWidget(refresh_files_btn)
        files_tab.setLayout(files_layout)
        self.tab_widget.addTab(files_tab, "📁 Capture Files")
        
        layout.addWidget(self.tab_widget)
        panel.setLayout(layout)
        return panel
        
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open Capture Directory", self)
        open_action.triggered.connect(self.open_capture_directory)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        status_action = QAction("System Status Check", self)
        status_action.triggered.connect(self.run_status_check)
        tools_menu.addAction(status_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About StealthShark", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_system_tray(self):
        """Setup system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            # You could add an icon here
            self.tray_icon.setToolTip("StealthShark Monitor")
            self.tray_icon.show()
            
    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0, 0, 0))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        
        self.setPalette(dark_palette)
        
    def start_monitoring(self):
        """Start network monitoring"""
        try:
            self.log_message("Starting Enhanced Wireshark Monitor...")
            
            # Create directories if needed
            capture_dir = Path(self.dir_edit.text())
            capture_dir.mkdir(parents=True, exist_ok=True)
            (capture_dir / "logs").mkdir(exist_ok=True)
            
            # Start monitor thread
            self.monitor_thread = MonitorThread(
                capture_dir=str(capture_dir),
                duration=self.duration_spin.value()
            )
            
            # Connect signals
            self.monitor_thread.status_update.connect(self.log_message)
            self.monitor_thread.error_signal.connect(self.handle_error)
            self.monitor_thread.finished_signal.connect(self.monitoring_finished)
            
            # Start thread
            self.monitor_thread.start()
            
            # Update UI
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.statusBar().showMessage("Monitoring Active")
            
        except Exception as e:
            self.handle_error(f"Failed to start monitoring: {str(e)}")
            
    def stop_monitoring(self):
        """Stop network monitoring"""
        if self.monitor_thread:
            self.log_message("Stopping monitor...")
            self.monitor_thread.stop_monitoring()
            self.monitor_thread.quit()
            self.monitor_thread.wait()
            
        self.monitoring_finished()
        
    def monitoring_finished(self):
        """Handle monitoring finished"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.statusBar().showMessage("Monitoring Stopped")
        self.log_message("Monitoring finished.")
        
    def log_message(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)
        self.logger.info(message)
        
    def handle_error(self, error_message):
        """Handle error messages"""
        self.log_message(f"ERROR: {error_message}")
        QMessageBox.critical(self, "Error", error_message)
        
    def browse_directory(self):
        """Browse for capture directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Capture Directory")
        if directory:
            self.dir_edit.setText(directory)
            
    def open_capture_directory(self):
        """Open capture directory in file manager"""
        capture_dir = self.dir_edit.text()
        if os.path.exists(capture_dir):
            subprocess.run(["open", capture_dir])
        else:
            QMessageBox.warning(self, "Warning", "Capture directory does not exist")
            
    def refresh_capture_files(self):
        """Refresh the capture files list"""
        self.files_list.clear()
        capture_dir = Path(self.dir_edit.text())
        
        if capture_dir.exists():
            for pcap_file in capture_dir.rglob("*.pcap"):
                self.files_list.addItem(str(pcap_file.relative_to(capture_dir)))
                
    def run_status_check(self):
        """Run system status check"""
        try:
            result = subprocess.run(
                ["python3", "stealthshark_status_check.py"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                QMessageBox.information(self, "Status Check", "All systems operational!")
            else:
                QMessageBox.warning(self, "Status Check", f"Issues detected:\n{result.stderr}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run status check: {str(e)}")
            
    def show_about(self):
        """Show about dialog"""
        about_text = """
        🦈 StealthShark Enhanced Network Monitor
        
        Advanced network monitoring and packet capture system
        with intelligent memory management and automated cleanup.
        
        Features:
        • Real-time network interface monitoring
        • Automated packet capture with rotation
        • System resource monitoring
        • Dark-themed professional interface
        • Comprehensive logging and diagnostics
        
        Built with PyQt6 and Python 3
        """
        QMessageBox.about(self, "About StealthShark", about_text)
        
    def closeEvent(self, event):
        """Handle window close event"""
        if self.monitor_thread and self.monitor_thread.isRunning():
            reply = QMessageBox.question(
                self, "Confirm Exit",
                "Monitoring is active. Stop monitoring and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_monitoring()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("StealthShark Enhanced Monitor")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    window = EnhancedWiresharkGUI()
    window.show()
    
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
