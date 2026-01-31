from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QPlainTextEdit,
    QCheckBox,
    QLineEdit,
    QLabel,
    QSlider,
)

from PyQt5.QtGui import QImage, QPixmap, QBrush
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from controller import CameraWorker
import cv2
import sys
import serial


class Window(QWidget):
    deadzone_value = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.camera = CameraWorker()
        self.camera.frame_ready.connect(self.on_new_frame)
        self.camera.err_signal.connect(self.send_tracking)
        self.camera.status.connect(self.log)
        self.camera.ATTACK.connect(self.attack_manager)

        self.camera.start()
        self.deadzone_value.connect(self.camera.update_deadzone)
        
        self.previous_attack_state = False  

        self.setWindowTitle("TURRET CONTROL SYSTEM")
        self.resize(1000, 600)
        
        import os
        bg_path = os.path.join(os.path.dirname(__file__), "Background.jpg")
        bg_pixmap = QPixmap(bg_path)
        if not bg_pixmap.isNull():
            scaled_pixmap = bg_pixmap.scaled(1000, 600, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            palette = self.palette()
            palette.setBrush(self.backgroundRole(), QBrush(scaled_pixmap))
            self.setPalette(palette)
        
        self.setStyleSheet(
            "color: #ffffff; font-family: 'Courier New', monospace; font-size: 11px;"
        )

        self.BTN_Connect = QPushButton("CONNECT")
        self.BTN_Connect.setMinimumSize(100, 35)
        self.apply_retro_button(self.BTN_Connect, "#ffffff", "#000")
        self.BTN_Connect.setCheckable(True)

        self.PBTN_Bonner = QPushButton("BONER")
        self.PBTN_Bonner.setMinimumSize(100, 35)
        self.apply_retro_button(self.PBTN_Bonner, "#ffffff", "#000")
        self.PBTN_Bonner.setCheckable(True)
        self.PBTN_Bonner.setChecked(True)

        self.BTN_START_SHOOT = QPushButton("BRRR")
        self.BTN_START_SHOOT.setMinimumSize(100, 35)
        self.apply_retro_button(self.BTN_START_SHOOT, "#ffaa00", "#000")

        self.BTN_STOP_SHOOT = QPushButton("SHUT")
        self.BTN_STOP_SHOOT.setMinimumSize(100, 35)
        self.apply_retro_button(self.BTN_STOP_SHOOT, "#ff0000", "#000")

        self.BTN_STOP_SHOOT.clicked.connect(self.shoot_stop_manager)
        self.BTN_START_SHOOT.clicked.connect(self.shoot_start_manager)

        self.PBTN_Bonner.setCheckable(True)
        self.PBTN_Bonner.setChecked(True)
        self.PBTN_Bonner.toggled.connect(self.bonnerManager)

        self.SLIDER_Deadzone = QSlider(Qt.Horizontal)
        self.SLIDER_Deadzone.setRange(0, 50)
        self.SLIDER_Deadzone.setSingleStep(1)
        self.SLIDER_Deadzone.setValue(20)
        self.SLIDER_Deadzone.valueChanged.connect(self.deadzone_value.emit)

        self.video_label = QLabel()
        self.video_label.setMinimumSize(480, 360)
        self.video_label.setStyleSheet("background-color: #000; border: 3px solid #8800ff;")

        self.Console = QPlainTextEdit()
        self.Console.setMinimumSize(320, 360)
        self.Console.setReadOnly(True)
        self.Console.setStyleSheet(
            "background-color: #000; color: #ffffff; border: 2px solid #555; "
            "font-family: 'Courier New', monospace; font-size: 9px;"
        )
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText(">> ENTER COMMAND")
        self.command_input.setStyleSheet(
            "background-color: #000; color: #ffffff; border: 2px solid #555; "
            "font-family: 'Courier New', monospace; padding: 5px;"
        )

        layout_main = QHBoxLayout()
        layout_main.setContentsMargins(10, 10, 10, 10)
        layout_main.setSpacing(10)

        layout_video_section = QVBoxLayout()
        layout_video_section.setContentsMargins(0, 0, 0, 0)
        layout_video_section.setSpacing(8)
        layout_video_section.addWidget(self.video_label)
        
        layout_controls = QHBoxLayout()
        layout_controls.setContentsMargins(0, 0, 0, 0)
        layout_controls.setSpacing(5)
        layout_controls.addWidget(self.PBTN_Bonner)
        layout_controls.addWidget(self.BTN_START_SHOOT)
        layout_controls.addWidget(self.BTN_STOP_SHOOT)
        layout_controls.addStretch()
        
        layout_video_section.addLayout(layout_controls)
        layout_video_section.addWidget(self.SLIDER_Deadzone)

        layout_console = QVBoxLayout()
        layout_console.setContentsMargins(0, 0, 0, 0)
        layout_console.setSpacing(5)

        self.checkbox_lvl1 = QCheckBox("INFO")
        self.checkbox_lvl2 = QCheckBox("WARNINGS")
        self.checkbox_lvl3 = QCheckBox("ERRORS")
        self.checkbox_lvl1.setStyleSheet("QCheckBox { color: #ffffff; } QCheckBox::indicator { border: 2px solid #555; width: 14px; height: 14px; } QCheckBox::indicator:checked { background-color: #ffffff; }")
        self.checkbox_lvl2.setStyleSheet("QCheckBox { color: #ffffff; } QCheckBox::indicator { border: 2px solid #555; width: 14px; height: 14px; } QCheckBox::indicator:checked { background-color: #ffffff; }")
        self.checkbox_lvl3.setStyleSheet("QCheckBox { color: #ffffff; } QCheckBox::indicator { border: 2px solid #555; width: 14px; height: 14px; } QCheckBox::indicator:checked { background-color: #ffffff; }")
        
        layout_console.addWidget(self.BTN_Connect)
        layout_console.addWidget(self.checkbox_lvl1)
        layout_console.addWidget(self.checkbox_lvl2)
        layout_console.addWidget(self.checkbox_lvl3)
        layout_console.addWidget(self.Console)
        layout_console.addWidget(self.command_input)

        self.command_input.returnPressed.connect(
            lambda: self.send_command(self.command_input.text().strip())
        )
        
        layout_main.addLayout(layout_video_section, 2)
        layout_main.addLayout(layout_console, 1)
        self.setLayout(layout_main)

        self.checkbox_lvl1.setChecked(True)
        self.checkbox_lvl2.setChecked(True)
        self.checkbox_lvl3.setChecked(True)

        self.ser = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial)
        self.BTN_Connect.toggled.connect(self.connect_arduino)

    def apply_retro_button(self, button, fg_color, bg_color):
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {fg_color};
                border: 2px solid {fg_color};
                font-weight: bold;
                font-family: 'Courier New', monospace;
            }}
            QPushButton:hover {{
                background-color: {fg_color};
                color: {bg_color};
            }}
            QPushButton:pressed {{
                background-color: {fg_color};
                color: {bg_color};
            }}
        """)

    def send_tracking(self, err_x, err_y, x_speed, y_speed):
        if self.ser and self.ser.is_open:
            try:
                cmd = f"G2 {err_x} {err_y} {x_speed} {y_speed}"
                self.ser.write((cmd + "\n").encode())
            except Exception as e:
                self.log(f"ERROR: {e}")
        else:
            # self.log("[!!!] Serial port not connected.") # commented cuz fuck log spam
            pass

    def attack_manager(self, is_attacking):
        if is_attacking != self.previous_attack_state:
            self.previous_attack_state = is_attacking
            if is_attacking:
                self.log("TARGET LOCKED")
                self.send_command("G11")
            else:
                self.log("TARGET LOST")
                self.send_command("G12")
            

    def send_command(self, command):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write((command + "\n").encode())
                self.log(f">> {command}")
                self.command_input.clear()
            except Exception as e:
                self.log(f"ERROR: {e}")
                self.command_input.clear()
        else:
            self.log("NOT CONNECTED")
            self.command_input.clear()

    def log(self, text):
        if text.startswith("[!!!]") and not self.checkbox_lvl3.isChecked():
            return

        if text.startswith("[!!]") and not self.checkbox_lvl2.isChecked():
            return

        if text.startswith("[!]") and not self.checkbox_lvl1.isChecked():
            return

        self.Console.appendPlainText(text)

    def on_new_frame(self, frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(qt_image)

        self.video_label.setPixmap(
            pixmap.scaled(
                self.video_label.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            )
        )

    def connect_arduino(self):
        if self.BTN_Connect.isChecked():
            try:
                self.ser = serial.Serial("/dev/ttyACM0", 115200, timeout=0)
                self.log("CONNECTED")
                self.send_command("G98")
                self.timer.start(25)
                self.BTN_Connect.setText("DISCONNECT")
                self.apply_retro_button(self.BTN_Connect, "#ff0000", "#000")
            except serial.SerialException as e:
                self.log(f"ERROR: {e}")
                self.BTN_Connect.setChecked(False)
        else:
            try:
                if self.ser and self.ser.is_open:
                    self.timer.stop()
                    self.send_command("G99")
                    self.ser.close()
                    self.log("DISCONNECTED")
            except serial.SerialException as e:
                self.log(f"ERROR: {e}")
            finally:
                self.ser = None
                self.BTN_Connect.setText("CONNECT")
                self.apply_retro_button(self.BTN_Connect, "#ffffff", "#000")

    def read_serial(self):
        if self.ser and self.ser.in_waiting:
            try:
                line = self.ser.readline().decode(errors="ignore").strip()
                if line:
                    self.log(f"{line}")
            except Exception as e:
                self.log(f"Read error: {e}")

    def shoot_start_manager(self):
        self.log("BRRR")
        self.send_command("G11")

    def shoot_stop_manager(self):
        self.log("SHUT")
        self.send_command("G12")

    def bonnerManager(self):
        if self.PBTN_Bonner.isChecked():
            self.log("BONER ENABLED")
            self.apply_retro_button(self.PBTN_Bonner, "#ffffff", "#000")
            self.send_command("G98")
        else:
            self.log("BONER DISABLED")
            self.apply_retro_button(self.PBTN_Bonner, "#ff6600", "#000")
            self.send_command("G99")

    def closeEvent(self, event):
        if self.camera.isRunning():
            self.camera.stop()
            self.camera.wait() 
            self.send_command("G99")
        if self.ser and self.ser.is_open:
            self.ser.close()
        event.accept()


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())
