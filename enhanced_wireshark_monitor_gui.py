#!/usr/bin/env python3
"""
Enhanced Wireshark Monitor GUI with Comprehensive Logging
PyQt6-based interface for persistent network monitoring and packet capture
Includes extensive error handling and debugging capabilities
"""

import sys
import os
import json
import signal
import psutil
import glob
import threading
import time
import subprocess
import traceback
import logging
import atexit
from datetime import datetime, timedelta
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QTextEdit, QTableWidget, 
                            QTableWidgetItem, QProgressBar, QGroupBox, QLineEdit,
                            QCheckBox, QSlider, QFileDialog, QListWidget, QSplitter,
                            QMessageBox, QComboBox, QTabWidget)
from PyQt6.QtCore import QTimer, QThread, pyqtSignal, Qt, QSize, QObject
from PyQt6.QtGui import QFont, QColor, QPalette, QPixmap, QIcon
import psutil

# Setup logging before any other imports
def setup_gui_logging():
    """Setup comprehensive logging for GUI debugging"""
    log_dir = Path("./gui_logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"gui_debug_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("WiresharkGUI")
    logger.info("GUI logging initialized")
    return logger

# Initialize logging
gui_logger = setup_gui_logging()

class SafeMonitorThread(QThread):
    """Thread-safe monitor with comprehensive error handling"""
    interface_activity = pyqtSignal(str, dict)
    capture_started = pyqtSignal(str, str)
    capture_completed = pyqtSignal(str, str)
    status_update = pyqtSignal(dict)
    alert_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, capture_dir, duration, interval):
        super().__init__()
        self.logger = logging.getLogger("MonitorThread")
        self.capture_dir = capture_dir
        self.duration = duration
        self.interval = interval
        self.monitor_process = None
        self.running = False
        
        self.logger.info(f"MonitorThread initialized: dir={capture_dir}, duration={duration}, interval={interval}")
        
    def alert_callback(self, message):
        """Thread-safe alert callback"""
        try:
            self.logger.info(f"Alert callback: {message}")
            self.alert_signal.emit(message)
        except Exception as e:
            self.logger.error(f"Alert callback error: {e}")
            
    def run(self):
        """Run monitor using subprocess instead of threading"""
        try:
            self.running = True
            self.logger.info("Starting monitor thread")
            
            # Use subprocess to avoid threading issues
            cmd = [
                "./wireshark_monitor_venv/bin/python3",
                "persistent_wireshark_monitor.py",
                "--duration", str(self.duration),
                "--interval", str(self.interval),
                "--capture-dir", str(self.capture_dir)
            ]
            
            self.logger.info(f"Starting monitor subprocess: {' '.join(cmd)}")
            
            self.monitor_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor the subprocess output
            while self.running and self.monitor_process.poll() is None:
                try:
                    # Read output line by line
                    output = self.monitor_process.stdout.readline()
                    if output:
                        self.logger.debug(f"Monitor output: {output.strip()}")
                        
                        # Parse for specific events
                        if "Activity detected" in output:
                            self.alert_signal.emit(f"Network activity detected")
                        elif "Started capture" in output:
                            self.capture_started.emit("interface", "filename")
                        elif "completed" in output:
                            self.capture_completed.emit("interface", "completed")
                            
                    time.sleep(0.1)
                    
                except Exception as e:
                    self.logger.error(f"Error reading monitor output: {e}")
                    break
                    
            self.logger.info("Monitor thread finished")
            
        except Exception as e:
            self.logger.error(f"Monitor thread error: {e}")
            self.logger.error(traceback.format_exc())
            self.error_signal.emit(f"Monitor error: {e}")
            
    def stop(self):
        """Stop the monitor safely"""
        try:
            self.logger.info("Stopping monitor thread")
            self.running = False
            
            if self.monitor_process and self.monitor_process.poll() is None:
                self.logger.info("Terminating monitor subprocess")
                self.monitor_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.monitor_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.logger.warning("Monitor subprocess didn't terminate, killing")
                    self.monitor_process.kill()
                    
        except Exception as e:
            self.logger.error(f"Error stopping monitor: {e}")

class EnhancedWiresharkMonitorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("WiresharkGUI")
        self.logger.info("Initializing Enhanced Wireshark Monitor GUI v2")
        
        try:
            self.monitor_thread = None
            self.capture_dir = Path("./pcap_captures")
            self.duration = 30  # 30 seconds default for testing
            self.interval = 5     # 5 seconds default
            
            # Timer tracking
            self.start_time = None
            self.timer_update = None
            
            # Auto-restart settings
            self.auto_restart_enabled = True
            
            # Persistent logging
            self.setup_persistent_logging()
            
            # Setup exit handlers for auto-save
            self.setup_exit_handlers()
            
            self.logger.info(f"Initial config: dir={self.capture_dir}, duration={self.duration}, interval={self.interval}")
            
            self.init_ui()
            self.setup_timers()
            
            self.logger.info("GUI initialization completed successfully")
            
        except Exception as e:
            self.logger.error(f"GUI initialization error: {e}")
            self.logger.error(traceback.format_exc())
            self.show_error_dialog("Initialization Error", f"Failed to initialize GUI: {e}")
            
    def setup_persistent_logging(self):
        """Setup persistent logging to dedicated folder"""
        try:
            # Create persistent logs directory
            persistent_log_dir = Path("./persistent_logs")
            persistent_log_dir.mkdir(exist_ok=True)
            
            # Create session-specific log file
            session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.session_log_file = persistent_log_dir / f"wireshark_session_{session_timestamp}.log"
            
            # Setup file handler for persistent logging
            file_handler = logging.FileHandler(self.session_log_file)
            file_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            
            # Add to logger
            self.logger.addHandler(file_handler)
            self.logger.info(f"Persistent logging initialized: {self.session_log_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to setup persistent logging: {e}")
            
    def setup_exit_handlers(self):
        """Setup handlers for graceful exit and auto-save"""
        try:
            import atexit
            import signal
            
            # Register exit handler
            atexit.register(self.emergency_save_and_cleanup)
            
            # Register signal handlers for crashes
            signal.signal(signal.SIGTERM, self.signal_handler)
            signal.signal(signal.SIGINT, self.signal_handler)
            
            self.logger.info("Exit handlers registered for auto-save protection")
            
        except Exception as e:
            self.logger.error(f"Failed to setup exit handlers: {e}")
            
    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        self.logger.info(f"Received signal {signum}, initiating emergency save...")
        self.emergency_save_and_cleanup()
        sys.exit(0)
        
    def emergency_save_and_cleanup(self):
        """Emergency save function called on exit/crash"""
        try:
            self.logger.info("🚨 EMERGENCY SAVE: Preserving capture data...")
            
            # Stop any active monitoring
            if self.monitor_thread:
                self.safe_stop_monitor()
                
            # Save current session state
            session_state = {
                'timestamp': datetime.now().isoformat(),
                'duration': self.duration,
                'interval': self.interval,
                'auto_restart': self.auto_restart_enabled,
                'capture_dir': str(self.capture_dir)
            }
            
            # Save to emergency file
            emergency_file = Path('./emergency_session_state.json')
            with open(emergency_file, 'w') as f:
                json.dump(session_state, f, indent=2)
                
            self.logger.info(f"✅ Emergency save completed: {emergency_file}")
            
        except Exception as e:
            print(f"Emergency save failed: {e}")
            
    def show_error_dialog(self, title, message):
        """Show error dialog with logging"""
        try:
            self.logger.error(f"Error dialog: {title} - {message}")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle(title)
            msg.setText(message)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
        except Exception as e:
            self.logger.error(f"Error showing error dialog: {e}")
            print(f"CRITICAL ERROR: {title} - {message}")
            
    def init_ui(self):
        """Initialize the user interface with error handling"""
        try:
            self.logger.info("Starting UI initialization")
            
            self.setWindowTitle("Enhanced Wireshark Monitor - AIMF LLC")
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
            
            self.logger.info("UI initialization completed")
            
        except Exception as e:
            self.logger.error(f"UI initialization error: {e}")
            self.logger.error(traceback.format_exc())
            raise
            
    def create_control_panel(self):
        """Create the control panel with error handling"""
        try:
            self.logger.info("Creating control panel")
            
            control_widget = QWidget()
            layout = QVBoxLayout(control_widget)
            
            # Monitor Control Group
            control_group = QGroupBox("Monitor Control")
            control_layout = QVBoxLayout(control_group)
            
            # Start/Stop buttons
            button_layout = QHBoxLayout()
            self.start_btn = QPushButton("🚀 Start Monitor")
            self.start_btn.clicked.connect(self.safe_start_monitor)
            self.stop_btn = QPushButton("🛑 Stop Monitor")
            self.stop_btn.clicked.connect(self.safe_stop_monitor)
            self.stop_btn.setEnabled(False)
            
            button_layout.addWidget(self.start_btn)
            button_layout.addWidget(self.stop_btn)
            control_layout.addLayout(button_layout)
            
            # Status indicator
            self.status_label = QLabel("Status: Stopped")
            self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            control_layout.addWidget(self.status_label)
            
            # Progress bar and timer
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            control_layout.addWidget(self.progress_bar)
            
            self.timer_label = QLabel("Timer: Not started")
            self.timer_label.setStyleSheet("color: #ffffff; font-family: monospace;")
            control_layout.addWidget(self.timer_label)
            
            layout.addWidget(control_group)
            
            # Configuration Group
            config_group = QGroupBox("Configuration")
            config_layout = QVBoxLayout(config_group)
            
            # Capture duration
            duration_layout = QHBoxLayout()
            duration_layout.addWidget(QLabel("Capture Duration:"))
            self.duration_combo = QComboBox()
            self.duration_combo.addItems([
                "30 seconds (30s)", "1 minute (60s)", "5 minutes (300s)", "10 minutes (600s)",
                "20 minutes (1200s)", "30 minutes (1800s)", "1 hour (3600s)", 
                "2 hours (7200s)", "3 hours (10800s)", "4 hours (14400s)", 
                "5 hours (18000s)", "6 hours (21600s)"
            ])
            self.duration_combo.setCurrentText("30 seconds (30s)")
            self.duration_combo.currentTextChanged.connect(self.safe_update_duration)
            duration_layout.addWidget(self.duration_combo)
            config_layout.addLayout(duration_layout)
            
            # Check interval
            interval_layout = QHBoxLayout()
            interval_layout.addWidget(QLabel("Check Interval:"))
            self.interval_slider = QSlider(Qt.Orientation.Horizontal)
            self.interval_slider.setRange(1, 30)
            self.interval_slider.setValue(5)
            self.interval_slider.valueChanged.connect(self.safe_update_interval)
            self.interval_label = QLabel("5 seconds")
            interval_layout.addWidget(self.interval_slider)
            interval_layout.addWidget(self.interval_label)
            config_layout.addLayout(interval_layout)
            
            # Capture directory
            dir_layout = QHBoxLayout()
            dir_layout.addWidget(QLabel("Capture Directory:"))
            self.dir_btn = QPushButton("📁 Select")
            self.dir_btn.clicked.connect(self.safe_select_directory)
            dir_layout.addWidget(self.dir_btn)
            config_layout.addLayout(dir_layout)
            
            self.dir_label = QLabel(str(self.capture_dir))
            self.dir_label.setWordWrap(True)
            config_layout.addWidget(self.dir_label)
            
            # Auto-restart option
            self.auto_restart_checkbox = QCheckBox("Auto-restart after completion (recommended for continuous monitoring)")
            self.auto_restart_checkbox.setChecked(True)  # Default enabled
            self.auto_restart_checkbox.setStyleSheet("color: #ffffff; font-size: 12px;")
            self.auto_restart_checkbox.stateChanged.connect(self.update_auto_restart)
            config_layout.addWidget(self.auto_restart_checkbox)
            
            layout.addWidget(config_group)
            
            # Interface List Group
            interface_group = QGroupBox("Monitored Interfaces")
            interface_layout = QVBoxLayout(interface_group)
            
            self.interface_list = QListWidget()
            self.safe_refresh_interfaces()
            interface_layout.addWidget(self.interface_list)
            
            refresh_btn = QPushButton("🔄 Refresh Interfaces")
            refresh_btn.clicked.connect(self.safe_refresh_interfaces)
            interface_layout.addWidget(refresh_btn)
            
            layout.addWidget(interface_group)
            
            # Add stretch to push everything to top
            layout.addStretch()
            
            self.logger.info("Control panel created successfully")
            return control_widget
            
        except Exception as e:
            self.logger.error(f"Error creating control panel: {e}")
            self.logger.error(traceback.format_exc())
            raise
            
    def create_monitoring_panel(self):
        """Create the monitoring panel with error handling"""
        try:
            self.logger.info("Creating monitoring panel")
            
            monitor_widget = QWidget()
            layout = QVBoxLayout(monitor_widget)
            
            # Tab widget for different views
            self.tab_widget = QTabWidget()
            
            # Logs Tab (simplified for debugging)
            logs_tab = QWidget()
            logs_layout = QVBoxLayout(logs_tab)
            
            logs_group = QGroupBox("Monitor Logs")
            logs_group_layout = QVBoxLayout(logs_group)
            
            # Log controls
            log_controls = QHBoxLayout()
            clear_btn = QPushButton("🗑️ Clear")
            clear_btn.clicked.connect(self.safe_clear_logs)
            export_btn = QPushButton("💾 Export")
            export_btn.clicked.connect(self.safe_export_logs)
            log_controls.addWidget(clear_btn)
            log_controls.addWidget(export_btn)
            log_controls.addStretch()
            logs_group_layout.addLayout(log_controls)
            
            self.log_text = QTextEdit()
            self.log_text.setReadOnly(True)
            logs_group_layout.addWidget(self.log_text)
            
            logs_layout.addWidget(logs_group)
            self.tab_widget.addTab(logs_tab, "📝 Logs")
            
            # Interface Status Tab
            status_tab = QWidget()
            status_layout = QVBoxLayout(status_tab)
            
            status_group = QGroupBox("Interface Status")
            status_group_layout = QVBoxLayout(status_group)
            
            self.interfaces_table = QTableWidget()
            self.interfaces_table.setColumnCount(4)
            self.interfaces_table.setHorizontalHeaderLabels(["Interface", "Packets", "Bytes", "Status"])
            status_group_layout.addWidget(self.interfaces_table)
            
            status_layout.addWidget(status_group)
            self.tab_widget.addTab(status_tab, "📊 Status")
            
            layout.addWidget(self.tab_widget)
            
            self.logger.info("Monitoring panel created successfully")
            return monitor_widget
            
        except Exception as e:
            self.logger.error(f"Error creating monitoring panel: {e}")
            self.logger.error(traceback.format_exc())
            raise
            
    def setup_timers(self):
        """Setup update timers with error handling"""
        try:
            self.logger.info("Setting up timers")
            
            # Update interface stats every 5 seconds
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.safe_update_interface_stats)
            self.update_timer.start(5000)
            
            # Timer for progress tracking
            self.timer_update = QTimer()
            self.timer_update.timeout.connect(self.update_progress_timer)
            
            self.logger.info("Timers setup completed")
            
        except Exception as e:
            self.logger.error(f"Error setting up timers: {e}")
            
    def update_progress_timer(self):
        """Update progress bar and timer display"""
        try:
            if not self.start_time:
                return
                
            elapsed = datetime.now() - self.start_time
            elapsed_seconds = int(elapsed.total_seconds())
            remaining_seconds = max(0, self.duration - elapsed_seconds)
            
            # Update progress bar
            progress = min(100, (elapsed_seconds / self.duration) * 100)
            self.progress_bar.setValue(int(progress))
            
            # Format time display
            elapsed_str = f"{elapsed_seconds//3600:02d}:{(elapsed_seconds%3600)//60:02d}:{elapsed_seconds%60:02d}"
            remaining_str = f"{remaining_seconds//3600:02d}:{(remaining_seconds%3600)//60:02d}:{remaining_seconds%60:02d}"
            
            self.timer_label.setText(f"Elapsed: {elapsed_str} | Remaining: {remaining_str}")
            
            # Stop timer when complete
            if remaining_seconds <= 0:
                self.timer_update.stop()
                self.progress_bar.setValue(100)
                self.log_message("⏰ Capture session completed")
                
                # Check for auto-restart
                if self.auto_restart_enabled:
                    self.log_message("🔄 Auto-restart enabled - Starting new session in 3 seconds...")
                    QTimer.singleShot(3000, self.auto_restart_session)
                else:
                    self.log_message("🛑 Auto-restart disabled - Stopping monitor")
                    self.safe_stop_monitor()
                
        except Exception as e:
            self.logger.error(f"Error updating progress timer: {e}")
            
    def update_auto_restart(self, state):
        """Update auto-restart setting"""
        self.auto_restart_enabled = state == Qt.CheckState.Checked.value
        self.logger.info(f"Auto-restart {'enabled' if self.auto_restart_enabled else 'disabled'}")
        
    def auto_restart_session(self):
        """Restart monitoring session with same settings"""
        try:
            self.log_message("🔄 Auto-restarting monitoring session...")
            self.safe_start_monitor()
        except Exception as e:
            self.logger.error(f"Auto-restart failed: {e}")
            self.log_message(f"❌ Auto-restart failed: {e}")
            
    def safe_refresh_interfaces(self):
        """Safely refresh the interface list"""
        try:
            self.logger.info("Refreshing interfaces")
            self.interface_list.clear()
            
            interfaces = list(psutil.net_if_addrs().keys())
            self.logger.info(f"Found {len(interfaces)} interfaces: {interfaces}")
            
            for interface in sorted(interfaces):
                self.interface_list.addItem(f"🔌 {interface}")
                
            self.log_message(f"Refreshed {len(interfaces)} interfaces")
            
        except Exception as e:
            self.logger.error(f"Error refreshing interfaces: {e}")
            self.log_message(f"Error refreshing interfaces: {e}")
            
    def safe_update_duration(self, text):
        """Safely update capture duration"""
        try:
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
            self.logger.info(f"Duration updated to {self.duration} seconds")
            self.log_message(f"Capture duration set to {self.duration/60:.1f} minutes")
            
        except Exception as e:
            self.logger.error(f"Error updating duration: {e}")
            
    def safe_update_interval(self, value):
        """Safely update check interval"""
        try:
            self.interval = value
            self.interval_label.setText(f"{value} seconds")
            self.logger.info(f"Interval updated to {value} seconds")
            
        except Exception as e:
            self.logger.error(f"Error updating interval: {e}")
            
    def safe_select_directory(self):
        """Safely select capture directory"""
        try:
            directory = QFileDialog.getExistingDirectory(self, "Select Capture Directory")
            if directory:
                self.capture_dir = Path(directory)
                self.dir_label.setText(str(self.capture_dir))
                self.logger.info(f"Capture directory set to {self.capture_dir}")
                self.log_message(f"Capture directory: {self.capture_dir}")
                
        except Exception as e:
            self.logger.error(f"Error selecting directory: {e}")
            self.log_message(f"Error selecting directory: {e}")
            
    def safe_start_monitor(self):
        """Safely start the monitor"""
        try:
            if self.monitor_thread and self.monitor_thread.isRunning():
                self.log_message("Monitor is already running")
                return
                
            self.logger.info("Starting monitor")
            self.log_message("🚀 Starting Wireshark Monitor...")
            self.log_message(f"📁 Capture Directory: {self.capture_dir}")
            self.log_message(f"⏱️ Duration: {self.duration/60:.1f} minutes")
            self.log_message(f"🔄 Check Interval: {self.interval} seconds")
            
            self.monitor_thread = SafeMonitorThread(
                str(self.capture_dir), 
                self.duration, 
                self.interval
            )
            
            # Connect signals
            self.monitor_thread.alert_signal.connect(self.on_alert)
            self.monitor_thread.error_signal.connect(self.on_error)
            self.monitor_thread.capture_started.connect(self.on_capture_started)
            self.monitor_thread.capture_completed.connect(self.on_capture_completed)
            
            self.monitor_thread.start()
            
            # Start progress tracking
            self.start_time = datetime.now()
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.timer_update.start(1000)  # Update every second
            
            # Update UI
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("Status: Running")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            
            self.log_message("✅ Monitor started successfully")
            
            # Log selected interfaces for monitoring
            selected_interfaces = []
            for i in range(self.interface_list.count()):
                item = self.interface_list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    interface_name = item.text().split(' ')[0]  # Get interface name before stats
                    selected_interfaces.append(interface_name)
            
            if selected_interfaces:
                self.log_message(f"🔍 Selected interfaces: {', '.join(selected_interfaces)}")
            else:
                self.log_message("🔍 Monitoring all available interfaces")
            
        except Exception as e:
            self.logger.error(f"Error starting monitor: {e}")
            self.logger.error(traceback.format_exc())
            self.log_message(f"❌ Error starting monitor: {e}")
            self.show_error_dialog("Start Error", f"Failed to start monitor: {e}")
            
    def safe_stop_monitor(self):
        """Safely stop the monitor"""
        try:
            if self.monitor_thread:
                self.logger.info("Stopping monitor")
                self.log_message("🛑 Stopping Wireshark Monitor...")
                
                self.monitor_thread.stop()
                self.monitor_thread.wait(5000)  # Wait up to 5 seconds
                
                self.log_message("✅ Monitor stopped successfully")
                
            # Stop progress tracking
            if self.timer_update:
                self.timer_update.stop()
            self.start_time = None
            self.progress_bar.setVisible(False)
            self.timer_label.setText("Timer: Not started")
            
            # Update UI
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_label.setText("Status: Stopped")
            self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            
        except Exception as e:
            self.logger.error(f"Error stopping monitor: {e}")
            self.log_message(f"❌ Error stopping monitor: {e}")
            
    def safe_update_interface_stats(self):
        """Safely update interface statistics"""
        try:
            stats = psutil.net_io_counters(pernic=True)
            
            self.interfaces_table.setRowCount(len(stats))
            
            for row, (interface, stat) in enumerate(stats.items()):
                self.interfaces_table.setItem(row, 0, QTableWidgetItem(interface))
                self.interfaces_table.setItem(row, 1, QTableWidgetItem(str(stat.packets_sent + stat.packets_recv)))
                self.interfaces_table.setItem(row, 2, QTableWidgetItem(f"{(stat.bytes_sent + stat.bytes_recv):,}"))
                
                # Status based on activity
                if stat.packets_sent + stat.packets_recv > 0:
                    status = "🟢 Active"
                else:
                    status = "⚪ Idle"
                self.interfaces_table.setItem(row, 3, QTableWidgetItem(status))
                
        except Exception as e:
            self.logger.error(f"Error updating interface stats: {e}")
            
    def safe_clear_logs(self):
        """Safely clear the log display"""
        try:
            self.log_text.clear()
            self.logger.info("Log display cleared")
            
        except Exception as e:
            self.logger.error(f"Error clearing logs: {e}")
            
    def safe_export_logs(self):
        """Safely export logs to file"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Logs", 
                f"wireshark_monitor_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text Files (*.txt)"
            )
            if filename:
                with open(filename, 'w') as f:
                    f.write(self.log_text.toPlainText())
                self.log_message(f"📄 Logs exported to: {filename}")
                self.logger.info(f"Logs exported to {filename}")
                
        except Exception as e:
            self.logger.error(f"Error exporting logs: {e}")
            self.log_message(f"Error exporting logs: {e}")
            
    def log_message(self, message):
        """Add message to log display with error handling"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            self.log_text.append(formatted_message)
            
            # Auto-scroll to bottom
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
        except Exception as e:
            self.logger.error(f"Error logging message: {e}")
            
    def on_alert(self, message):
        """Handle alert signal with error handling"""
        try:
            self.logger.info(f"Alert received: {message}")
            self.log_message(f"🚨 ALERT: {message}")
            
        except Exception as e:
            self.logger.error(f"Error handling alert: {e}")
            
    def on_error(self, message):
        """Handle error signal"""
        try:
            self.logger.error(f"Monitor error: {message}")
            self.log_message(f"❌ ERROR: {message}")
            self.show_error_dialog("Monitor Error", message)
            
        except Exception as e:
            self.logger.error(f"Error handling error signal: {e}")
            
    def on_capture_started(self, interface, filename):
        """Handle capture started signal"""
        try:
            self.logger.info(f"Capture started: {interface} -> {filename}")
            self.log_message(f"🎬 Started capture on {interface}")
            
        except Exception as e:
            self.logger.error(f"Error handling capture started: {e}")
            
    def on_capture_completed(self, interface, message):
        """Handle capture completed signal"""
        try:
            self.logger.info(f"Capture completed: {interface} - {message}")
            self.log_message(f"✅ {message}")
            
        except Exception as e:
            self.logger.error(f"Error handling capture completed: {e}")
            
    def closeEvent(self, event):
        """Handle window close event safely"""
        try:
            self.logger.info("Close event received")
            
            if self.monitor_thread and self.monitor_thread.isRunning():
                reply = QMessageBox.question(
                    self, 'Confirm Exit',
                    'Monitor is still running. Stop monitoring and exit?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.safe_stop_monitor()
                    event.accept()
                else:
                    event.ignore()
            else:
                event.accept()
                
            self.logger.info("Application closing")
            
        except Exception as e:
            self.logger.error(f"Error in close event: {e}")
            event.accept()  # Force close on error

def main():
    try:
        gui_logger.info("Starting Enhanced Wireshark Monitor GUI application")
        
        app = QApplication(sys.argv)
        app.setApplicationName("Enhanced Wireshark Monitor")
        
        # Set application icon if available
        try:
            app.setWindowIcon(QIcon("icon.png"))
        except:
            pass
            
        window = EnhancedWiresharkMonitorGUI()
        window.show()
        
        gui_logger.info("GUI window shown, entering event loop")
        
        result = app.exec()
        gui_logger.info(f"Application exited with code {result}")
        return result
        
    except Exception as e:
        gui_logger.error(f"Critical application error: {e}")
        gui_logger.error(traceback.format_exc())
        print(f"CRITICAL ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
