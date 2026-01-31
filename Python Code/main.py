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

from PyQt5.QtGui import QImage, QPixmap
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

        self.camera.start()
        self.deadzone_value.connect(self.camera.update_deadzone)

        # --- UI ---#
        self.setWindowTitle("New Person, Same Old Mistakes - Tame Impala")
        self.resize(960, 640)
        self.setStyleSheet(
            "background-color: #2b2b2b; color: white; font-family: Arial; font-size: 14px;"
        )

        self.BTN_Connect = QPushButton("Connect")
        self.BTN_Connect.setFixedSize(100, 40)
        self.BTN_Connect.setStyleSheet(
            "background-color: #4CAF50; color: white; border: none; border-radius: 5px;"
        )

        self.SLIDER_Deadzone = QSlider(Qt.Horizontal)
        self.SLIDER_Deadzone.setRange(0, 50)
        self.SLIDER_Deadzone.setSingleStep(1)
        self.SLIDER_Deadzone.setValue(10)

        self.SLIDER_Deadzone.valueChanged.connect(self.deadzone_value.emit)

        self.deadzone_group = QGroupBox("Deadzone")
        deadzone_layout = QVBoxLayout()
        deadzone_layout.addWidget(self.SLIDER_Deadzone)
        self.deadzone_group.setLayout(deadzone_layout)
        self.deadzone_group.setFixedSize(500, 70)

        self.video_label = QLabel()  ## video display
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("background-color: black;")

        self.Console = QPlainTextEdit()  ## console
        self.Console.setFixedSize(300, 500)
        self.Console.setReadOnly(True)
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("GCode I/P ...")

        layout_main = QHBoxLayout()  ## main Layout

        layout_console = QVBoxLayout()
        layout_console.setContentsMargins(10, 0, 0, 0)
        layout_console.setSpacing(10)

        layout_main_sub = QVBoxLayout()

        self.checkbox_lvl1 = QCheckBox("Notification Level [!]")  ## checkboxes
        self.checkbox_lvl2 = QCheckBox("Notification Level [!!]")
        self.checkbox_lvl3 = QCheckBox("Notification Level [!!!]")

        layout_main_sub.addWidget(self.video_label)
        layout_main_sub.addWidget(self.deadzone_group)

        layout_main.addLayout(layout_main_sub)

        layout_console.addWidget(self.checkbox_lvl1)  ## add widgets
        layout_console.addWidget(self.checkbox_lvl2)
        layout_console.addWidget(self.checkbox_lvl3)

        layout_console.addWidget(self.BTN_Connect)
        layout_console.addWidget(self.Console)
        layout_console.addWidget(self.command_input)

        self.command_input.returnPressed.connect(
            self.send_command
        )  ## connect interactives
        layout_main.addLayout(layout_console)
        self.setLayout(layout_main)

        self.checkbox_lvl1.setChecked(True)
        self.checkbox_lvl2.setChecked(True)
        self.checkbox_lvl3.setChecked(True)

        # --- Serial comms ---#
        self.ser = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial)

        self.BTN_Connect.clicked.connect(self.connect_arduino)

    def send_tracking(self, err_x, err_y):
        if self.ser and self.ser.is_open:
            try:
                self.log(f"[ TRACK CMD ] => X:{err_x} Y:{err_y}")
            except Exception as e:
                self.log(f"[!!] Error while sending tracking command :- {e}")
        else:
            self.log("[!!!] Serial port not connected.")

    def send_command(self):
        command = self.command_input.text().strip()

        if self.ser and self.ser.is_open:
            try:
                self.ser.write((command + "\n").encode())
                self.log(f"[ USER CMD ] => {command}")
                self.command_input.clear()
            except Exception as e:
                self.log(f"[!!] Error while sending command :- {e}")
                self.command_input.clear()
        else:
            self.log("[!!!] Serial port not connected.")
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
                self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )

    def connect_arduino(self):
        try:
            self.ser = serial.Serial("/dev/ttyACM0", 115200, timeout=0)
            self.log("[ USER CMD ] => Connected to Arduino")
            self.timer.start(25)

        except serial.SerialException as e:
            self.log(f"[!!!] Error connecting to Arduino: {e}")

    def read_serial(self):
        if self.ser and self.ser.in_waiting:
            try:
                line = self.ser.readline().decode(errors="ignore").strip()
                if line:
                    self.log(f"{line}")
            except Exception as e:
                self.log(f"Read error: {e}")

    def bonnerManager(self):
        if self.PBTN_Bonner.isChecked():
            self.log("[ USER CMD ] => Bonner Activated")
            self.PBTN_Bonner.setStyleSheet(
                "background-color: #2aab20; color: white; border: none; border-radius: 5px;"
            )
            self.send_command("G99")
        else:
            self.log("[ USER CMD ] => Bonner Deactivated")
            self.PBTN_Bonner.setStyleSheet(
                "background-color: #eb4034; color: white; border: none; border-radius: 5px;"
            )
            self.send_command("G98")


    def closeEvent(self, event):
        if self.camera.isRunning():
            self.camera.stop()
            self.camera.wait()
        event.accept()


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())
