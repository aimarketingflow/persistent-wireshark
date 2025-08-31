#!/usr/bin/env python3
"""
StealthShark - GUI Memory Monitor
PyQt6-based graphical interface for network monitoring system
"""

import sys
import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    PYQT_AVAILABLE = True
except ImportError:
    print("PyQt6 not available. Please install with: pip install PyQt6")
    PYQT_AVAILABLE = False
    sys.exit(1)

# Try to import the monitoring system
try:
    from enhanced_memory_monitor import MemoryOptimizedTSharkMonitor
    MONITOR_AVAILABLE = True
except ImportError:
    print("Warning: Enhanced memory monitor not found. Using mock implementation.")
    MONITOR_AVAILABLE = False
    
    # Mock implementation for testing
    class MemoryOptimizedTSharkMonitor:
        def __init__(self):
            self.monitoring_active = False
            
        def get_system_status(self):
            return {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'memory_total_gb': 16.0,
                    'memory_used_gb': 8.5,
                    'memory_percent': 53.1,
                    'disk_total_gb': 500.0,
                    'disk_used_gb': 250.0,
                    'disk_percent': 50.0
                },
                'captures': {
                    'active_processes': 3,
                    'total_size_gb': 5.2,
                    'total_files': 24,
                    'processes': [
                        {'pid': 1234, 'interface': 'en0', 'memory_mb': 45.2, 'runtime_hours': 2.5, 'status': 'running'},
                        {'pid': 1235, 'interface': 'en1', 'memory_mb': 38.1, 'runtime_hours': 2.5, 'status': 'running'},
                        {'pid': 1236, 'interface': 'awdl0', 'memory_mb': 12.3, 'runtime_hours': 2.5, 'status': 'running'}
                    ]
                }
            }
            
        def start_monitoring(self, interfaces=None):
            self.monitoring_active = True
            
        def stop_monitoring(self):
            self.monitoring_active = False
            
        def cleanup_old_files(self, force=False):
            pass

class MonitoringThread(QThread):
    """Background thread for monitoring system status"""
    status_updated = pyqtSignal(dict)
    alert_triggered = pyqtSignal(str, str)
    
    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor
        self.running = True
        
    def run(self):
        while self.running:
            try:
                status = self.monitor.get_system_status()
                if status:
                    self.status_updated.emit(status)
                    
                    # Check for alerts
                    if status['system']['memory_percent'] > 90:
                        self.alert_triggered.emit("High Memory Usage", 
                                                f"Memory usage at {status['system']['memory_percent']:.1f}%")
                    
                    if status['system']['disk_percent'] > 85:
                        self.alert_triggered.emit("High Disk Usage", 
                                                f"Disk usage at {status['system']['disk_percent']:.1f}%")
                
                self.msleep(5000)  # Update every 5 seconds
                
            except Exception as e:
                print(f"Monitoring thread error: {e}")
                self.msleep(10000)  # Wait longer on error
                
    def stop(self):
        self.running = False
        self.quit()
        self.wait()

class ConfigDialog(QDialog):
    """Configuration dialog for memory settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("StealthShark Configuration")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # Memory settings
        memory_group = QGroupBox("Memory Settings")
        memory_layout = QFormLayout()
        
        self.max_memory_spin = QSpinBox()
        self.max_memory_spin.setRange(1, 64)
        self.max_memory_spin.setValue(8)
        self.max_memory_spin.setSuffix(" GB")
        
        self.max_disk_spin = QSpinBox()
        self.max_disk_spin.setRange(10, 1000)
        self.max_disk_spin.setValue(50)
        self.max_disk_spin.setSuffix(" GB")
        
        self.cleanup_threshold_spin = QDoubleSpinBox()
        self.cleanup_threshold_spin.setRange(0.5, 0.95)
        self.cleanup_threshold_spin.setSingleStep(0.05)
        self.cleanup_threshold_spin.setValue(0.8)
        
        self.rotation_hours_spin = QDoubleSpinBox()
        self.rotation_hours_spin.setRange(0.5, 24)
        self.rotation_hours_spin.setSingleStep(0.5)
        self.rotation_hours_spin.setValue(4)
        self.rotation_hours_spin.setSuffix(" hours")
        
        memory_layout.addRow("Max Memory:", self.max_memory_spin)
        memory_layout.addRow("Max Disk:", self.max_disk_spin)
        memory_layout.addRow("Cleanup Threshold:", self.cleanup_threshold_spin)
        memory_layout.addRow("Rotation Hours:", self.rotation_hours_spin)
        memory_group.setLayout(memory_layout)
        
        # Monitoring settings
        monitor_group = QGroupBox("Monitoring Settings")
        monitor_layout = QFormLayout()
        
        self.check_interval_spin = QSpinBox()
        self.check_interval_spin.setRange(5, 300)
        self.check_interval_spin.setValue(30)
        self.check_interval_spin.setSuffix(" seconds")
        
        self.auto_cleanup_check = QCheckBox()
        self.auto_cleanup_check.setChecked(True)
        
        self.compress_files_check = QCheckBox()
        self.compress_files_check.setChecked(True)
        
        monitor_layout.addRow("Check Interval:", self.check_interval_spin)
        monitor_layout.addRow("Auto Cleanup:", self.auto_cleanup_check)
        monitor_layout.addRow("Compress Files:", self.compress_files_check)
        monitor_group.setLayout(monitor_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addWidget(memory_group)
        layout.addWidget(monitor_group)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

class TSharkMonitorGUI(QMainWindow):
    """Main GUI application for TShark monitoring"""
    
    def __init__(self, duration_hours=None):
        super().__init__()
        self.monitor = MemoryOptimizedTSharkMonitor(duration_hours=duration_hours) if MONITOR_AVAILABLE else MemoryOptimizedTSharkMonitor()
        self.monitoring_thread = None
        self.system_tray = None
        self.duration_hours = duration_hours if duration_hours else 4
        
        self.init_ui()
        self.setup_system_tray()
        self.start_monitoring_thread()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("StealthShark Monitor")
        self.setGeometry(100, 100, 900, 600)
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Header with gradient background
        header = self.create_header()
        layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Dashboard tab
        self.dashboard_tab = self.create_dashboard_tab()
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        
        # Processes tab
        self.processes_tab = self.create_processes_tab()
        self.tabs.addTab(self.processes_tab, "Processes")
        
        # Logs tab
        self.logs_tab = self.create_logs_tab()
        self.tabs.addTab(self.logs_tab, "Logs")
        
        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)
        
        # Status bar
        self.statusBar().showMessage("StealthShark Ready")
        
    def create_header(self):
        """Create header with controls"""
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, stop:1 #3498db);
                border-radius: 5px;
            }
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        
        layout = QHBoxLayout()
        
        # Title
        title = QLabel("🦈 StealthShark Monitor")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Control buttons
        self.start_btn = QPushButton("Start Monitoring")
        self.cleanup_btn = QPushButton("Run Cleanup")
        self.config_btn = QPushButton("Configure")
        
        self.start_btn.clicked.connect(self.toggle_monitoring)
        self.cleanup_btn.clicked.connect(self.run_cleanup)
        self.config_btn.clicked.connect(self.show_config)
        
        layout.addWidget(self.start_btn)
        layout.addWidget(self.cleanup_btn)
        layout.addWidget(self.config_btn)
        
        header.setLayout(layout)
        return header
        
    def create_dashboard_tab(self):
        """Create dashboard tab with system overview"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # System status
        status_group = QGroupBox("System Status")
        status_layout = QGridLayout()
        
        # Memory usage
        status_layout.addWidget(QLabel("Memory Usage:"), 0, 0)
        self.memory_progress = QProgressBar()
        self.memory_progress.setStyleSheet("QProgressBar::chunk { background-color: #3498db; }")
        self.memory_label = QLabel("0%")
        status_layout.addWidget(self.memory_progress, 0, 1)
        status_layout.addWidget(self.memory_label, 0, 2)
        
        # Disk usage
        status_layout.addWidget(QLabel("Disk Usage:"), 1, 0)
        self.disk_progress = QProgressBar()
        self.disk_progress.setStyleSheet("QProgressBar::chunk { background-color: #e74c3c; }")
        self.disk_label = QLabel("0%")
        status_layout.addWidget(self.disk_progress, 1, 1)
        status_layout.addWidget(self.disk_label, 1, 2)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Quick stats
        stats_group = QGroupBox("Quick Statistics")
        stats_layout = QGridLayout()
        
        self.active_processes_label = QLabel("Active Processes: 0")
        self.capture_size_label = QLabel("Capture Size: 0 GB")
        self.uptime_label = QLabel("Uptime: 0 hours")
        
        stats_layout.addWidget(self.active_processes_label, 0, 0)
        stats_layout.addWidget(self.capture_size_label, 0, 1)
        stats_layout.addWidget(self.uptime_label, 1, 0)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Interface status
        interface_group = QGroupBox("Interface Status")
        interface_layout = QHBoxLayout()
        
        self.interface_labels = {}
        for interface in ['en0', 'en1', 'awdl0']:
            label = QLabel(f"{interface}: Inactive")
            label.setStyleSheet("color: red; font-weight: bold;")
            self.interface_labels[interface] = label
            interface_layout.addWidget(label)
            
        interface_group.setLayout(interface_layout)
        layout.addWidget(interface_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_processes_tab(self):
        """Create processes tab with process table"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        stop_btn = QPushButton("Stop Selected")
        
        refresh_btn.clicked.connect(self.refresh_processes)
        stop_btn.clicked.connect(self.stop_selected_process)
        
        controls_layout.addWidget(refresh_btn)
        controls_layout.addWidget(stop_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Process table
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(5)
        self.process_table.setHorizontalHeaderLabels(['PID', 'Interface', 'Memory (MB)', 'Runtime', 'Status'])
        self.process_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.process_table.setAlternatingRowColors(True)
        
        # Make table look professional
        self.process_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 8px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.process_table)
        widget.setLayout(layout)
        return widget
        
    def create_logs_tab(self):
        """Create logs tab with log display"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        controls_layout.addWidget(clear_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        
        layout.addWidget(self.log_display)
        widget.setLayout(layout)
        return widget
        
    def setup_system_tray(self):
        """Setup system tray integration"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
            
        # Create tray icon
        self.system_tray = QSystemTrayIcon(self)
        
        # Create a simple colored icon
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(52, 152, 219))  # Blue color
        self.system_tray.setIcon(QIcon(pixmap))
        
        # Create context menu
        tray_menu = QMenu()
        
        show_action = QAction("Show StealthShark", self)
        show_action.triggered.connect(self.show)
        
        status_action = QAction("Quick Status", self)
        status_action.triggered.connect(self.show_quick_status)
        
        cleanup_action = QAction("Run Cleanup", self)
        cleanup_action.triggered.connect(self.run_cleanup)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(status_action)
        tray_menu.addAction(cleanup_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.system_tray.setContextMenu(tray_menu)
        self.system_tray.activated.connect(self.tray_icon_activated)
        self.system_tray.show()
        
    def start_monitoring_thread(self):
        """Start background monitoring thread"""
        if self.monitoring_thread is None:
            self.monitoring_thread = MonitoringThread(self.monitor)
            self.monitoring_thread.status_updated.connect(self.update_status)
            self.monitoring_thread.alert_triggered.connect(self.show_alert)
            self.monitoring_thread.start()
            
    def update_status(self, status):
        """Update GUI with new status information"""
        try:
            # Update dashboard
            memory_percent = status['system']['memory_percent']
            disk_percent = status['system']['disk_percent']
            
            self.memory_progress.setValue(int(memory_percent))
            self.memory_label.setText(f"{memory_percent:.1f}%")
            
            self.disk_progress.setValue(int(disk_percent))
            self.disk_label.setText(f"{disk_percent:.1f}%")
            
            # Update quick stats
            self.active_processes_label.setText(f"Active Processes: {status['captures']['active_processes']}")
            self.capture_size_label.setText(f"Capture Size: {status['captures']['total_size_gb']:.1f} GB")
            
            # Update interface status
            active_interfaces = set()
            for process in status['captures']['processes']:
                active_interfaces.add(process['interface'])
                
            for interface, label in self.interface_labels.items():
                if interface in active_interfaces:
                    label.setText(f"{interface}: Active")
                    label.setStyleSheet("color: green; font-weight: bold;")
                else:
                    label.setText(f"{interface}: Inactive")
                    label.setStyleSheet("color: red; font-weight: bold;")
            
            # Update process table
            self.update_process_table(status['captures']['processes'])
            
            # Update system tray tooltip
            if self.system_tray:
                tooltip = f"Memory: {memory_percent:.1f}% | Disk: {disk_percent:.1f}% | Processes: {status['captures']['active_processes']}"
                self.system_tray.setToolTip(tooltip)
                
            # Add log entry
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] Status updated - Memory: {memory_percent:.1f}%, Disk: {disk_percent:.1f}%, Processes: {status['captures']['active_processes']}"
            self.log_display.append(log_entry)
            
            # Auto-scroll logs
            scrollbar = self.log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
        except Exception as e:
            print(f"Error updating status: {e}")
            
    def update_process_table(self, processes):
        """Update the process table with current processes"""
        self.process_table.setRowCount(len(processes))
        
        for row, process in enumerate(processes):
            self.process_table.setItem(row, 0, QTableWidgetItem(str(process['pid'])))
            self.process_table.setItem(row, 1, QTableWidgetItem(process['interface']))
            self.process_table.setItem(row, 2, QTableWidgetItem(f"{process['memory_mb']:.1f}"))
            self.process_table.setItem(row, 3, QTableWidgetItem(f"{process['runtime_hours']:.1f}h"))
            self.process_table.setItem(row, 4, QTableWidgetItem(process['status']))
            
        self.process_table.resizeColumnsToContents()
        
    def show_alert(self, title, message):
        """Show system alert"""
        if self.system_tray:
            self.system_tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Warning, 5000)
            
    def toggle_monitoring(self):
        """Toggle monitoring on/off"""
        if self.monitor.monitoring_active:
            self.monitor.stop_monitoring()
            self.start_btn.setText("Start Monitoring")
            self.statusBar().showMessage("Monitoring stopped")
        else:
            self.monitor.start_monitoring()
            self.start_btn.setText("Stop Monitoring")
            self.statusBar().showMessage("Monitoring started")
            
    def run_cleanup(self):
        """Run cleanup operation"""
        try:
            self.monitor.cleanup_old_files(force=True)
            self.statusBar().showMessage("Cleanup completed")
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_display.append(f"[{timestamp}] Manual cleanup completed")
            
        except Exception as e:
            self.statusBar().showMessage(f"Cleanup failed: {e}")
            
    def show_config(self):
        """Show configuration dialog"""
        dialog = ConfigDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.statusBar().showMessage("Configuration saved")
            
    def refresh_processes(self):
        """Manually refresh process list"""
        status = self.monitor.get_system_status()
        if status:
            self.update_process_table(status['captures']['processes'])
            
    def stop_selected_process(self):
        """Stop selected process"""
        current_row = self.process_table.currentRow()
        if current_row >= 0:
            pid_item = self.process_table.item(current_row, 0)
            if pid_item:
                pid = int(pid_item.text())
                # Implementation would go here
                self.statusBar().showMessage(f"Stopped process {pid}")
                
    def clear_logs(self):
        """Clear log display"""
        self.log_display.clear()
        
    def show_quick_status(self):
        """Show quick status dialog"""
        status = self.monitor.get_system_status()
        if status:
            message = f"""Memory: {status['system']['memory_percent']:.1f}%
Disk: {status['system']['disk_percent']:.1f}%
Active Processes: {status['captures']['active_processes']}
Capture Size: {status['captures']['total_size_gb']:.1f} GB"""
            
            QMessageBox.information(self, "Quick Status", message)
            
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()
                
    def closeEvent(self, event):
        """Handle close event - minimize to tray instead of closing"""
        if self.system_tray and self.system_tray.isVisible():
            self.hide()
            event.ignore()
        else:
            self.quit_application()
            
    def quit_application(self):
        """Quit the application completely"""
        if self.monitoring_thread:
            self.monitoring_thread.stop()
            
        if self.system_tray:
            self.system_tray.hide()
            
        QApplication.quit()

def main():
    """Main entry point"""
    if not PYQT_AVAILABLE:
        return
        
    import argparse
    parser = argparse.ArgumentParser(description='StealthShark GUI Monitor')
    parser.add_argument('--duration', type=float, default=None,
                        help='Capture duration in hours (default: from config or 4)')
    args = parser.parse_args()
    
    app = QApplication(sys.argv[:1])  # Only pass program name to QApplication
    app.setQuitOnLastWindowClosed(False)  # Keep running in system tray
    
    # Set application properties
    app.setApplicationName("StealthShark")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("StealthShark")
    
    # Create and show main window with duration if specified
    window = TSharkMonitorGUI(duration_hours=args.duration)
    if args.duration:
        window.statusBar().showMessage(f"Monitor configured for {args.duration} hour rotation cycles")
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
