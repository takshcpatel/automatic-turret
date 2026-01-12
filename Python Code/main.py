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
        self.setWindowTitle("Everlong/")
        self.resize(960, 640)
        self.setStyleSheet(
            "background-color: #2b2b2b; color: white; font-family: Arial; font-size: 14px;"
        )

        self.BTN_Connect = QPushButton("Connect") # connect button
        self.BTN_Connect.setFixedSize(100, 40)
        self.BTN_Connect.setStyleSheet(
            "background-color: #4CAF50; color: white; border: none; border-radius: 5px;"
        )

        self.PBTN_Bonner = QPushButton("Bonner") # bonner toggle button
        self.PBTN_Bonner.setFixedSize(100, 40)
        self.PBTN_Bonner.setStyleSheet(
            "background-color: #2aab20; color: white; border: none; border-radius: 5px;"
        )

        self.BTN_CUMSHOT = QPushButton("CUMM") # cumshot button
        self.BTN_CUMSHOT.setFixedSize(100, 40)
        self.BTN_CUMSHOT.setStyleSheet(
            "background-color: #ffffff; color: black; border: none; border-radius: 5px;"
        )

        self.BTN_PULLOUT = QPushButton("PULL OUT") # pull out button
        self.BTN_PULLOUT.setFixedSize(100, 40)
        self.BTN_PULLOUT.setStyleSheet(
            "background-color: #ffffff; color: black; border: none; border-radius: 5px;"
        )

        self.BTN_PULLOUT.clicked.connect(self.pullout_manager)
        self.BTN_CUMSHOT.clicked.connect(self.cum_manager)

        self.PBTN_Bonner.setCheckable(True)
        self.PBTN_Bonner.setChecked(True)
        self.PBTN_Bonner.toggled.connect(self.bonnerManager)

        self.SLIDER_Deadzone = QSlider(Qt.Horizontal) # deadzone slider
        self.SLIDER_Deadzone.setRange(0, 50)
        self.SLIDER_Deadzone.setSingleStep(1)
        self.SLIDER_Deadzone.setValue(30)

        self.SLIDER_Deadzone.valueChanged.connect(self.deadzone_value.emit)

        self.deadzone_group = QGroupBox("Deadzone")
        deadzone_layout = QVBoxLayout()
        deadzone_layout.addWidget(self.SLIDER_Deadzone)
        self.deadzone_group.setLayout(deadzone_layout)
        self.deadzone_group.setFixedSize(500, 70)

        self.SLIDER_X_SPEED = QSlider(Qt.Horizontal) # x speed slider
        self.SLIDER_X_SPEED.setRange(1000, 6000)
        self.SLIDER_X_SPEED.setSingleStep(1000)
        self.SLIDER_X_SPEED.setPageStep(1000)
        self.SLIDER_X_SPEED.setValue(5000)

        self.SLIDER_X_SPEED.valueChanged.connect(self.on_x_speed_changed)

        self.SLIDER_Y_SPEED = QSlider(Qt.Horizontal) # y speed slider
        self.SLIDER_Y_SPEED.setRange(1000, 6000)
        self.SLIDER_Y_SPEED.setSingleStep(1000)
        self.SLIDER_Y_SPEED.setPageStep(1000)
        self.SLIDER_Y_SPEED.setValue(3000)

        self.SLIDER_Y_SPEED.valueChanged.connect(self.on_y_speed_changed)

        self.speed_group = QGroupBox("Speed")
        speed_layout = QVBoxLayout()
        
        # X slider with label
        x_slider_layout = QHBoxLayout()
        x_label = QLabel("X")
        x_label.setFixedWidth(20)
        x_slider_layout.addWidget(x_label)
        x_slider_layout.addWidget(self.SLIDER_X_SPEED)
        speed_layout.addLayout(x_slider_layout)
        
        # Y slider with label
        y_slider_layout = QHBoxLayout()
        y_label = QLabel("Y")
        y_label.setFixedWidth(20)
        y_slider_layout.addWidget(y_label)
        y_slider_layout.addWidget(self.SLIDER_Y_SPEED)
        speed_layout.addLayout(y_slider_layout)
        
        self.speed_group.setLayout(speed_layout)
        self.speed_group.setFixedSize(500, 70)

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

        layout_main_sub_btn = QHBoxLayout()
        layout_main_sub = QVBoxLayout()

        self.checkbox_lvl1 = QCheckBox("Notification Level [!]")  ## checkboxes
        self.checkbox_lvl2 = QCheckBox("Notification Level [!!]")
        self.checkbox_lvl3 = QCheckBox("Notification Level [!!!]")

        layout_main_sub.addWidget(self.video_label)
        layout_main_sub.addLayout(layout_main_sub_btn)
        layout_main_sub_btn.addWidget(self.PBTN_Bonner)
        layout_main_sub_btn.addWidget(self.BTN_CUMSHOT)
        layout_main_sub_btn.addWidget(self.BTN_PULLOUT)
        layout_main_sub.addWidget(self.deadzone_group)
        layout_main_sub.addWidget(self.speed_group)


        layout_main.addLayout(layout_main_sub)

        layout_console.addWidget(self.checkbox_lvl1)  ## add widgets
        layout_console.addWidget(self.checkbox_lvl2)
        layout_console.addWidget(self.checkbox_lvl3)

        layout_console.addWidget(self.BTN_Connect)
        layout_console.addWidget(self.Console)
        layout_console.addWidget(self.command_input)

        self.command_input.returnPressed.connect(
            lambda: self.send_command(self.command_input.text().strip())
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
        x_speed = self.SLIDER_X_SPEED.value()
        y_speed = self.SLIDER_Y_SPEED.value()

        if self.ser and self.ser.is_open:
            try:
                cmd = f"G2 {err_x} {err_y} {x_speed} {y_speed}"
                self.ser.write((cmd + "\n").encode())
            except Exception as e:
                self.log(f"[!!] Error while sending tracking command :- {e}")
        else:
            # self.log("[!!!] Serial port not connected.") # commented cuz fuck log spam
            pass

    def send_command(self, command):
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
            self.send_command("G98")
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

    def cum_manager(self):
        self.log("[ USER CMD ] => Cummed")
        self.send_command("G11")

    def pullout_manager(self):
        self.log("[ USER CMD ] => Pulling Out")
        self.send_command("G12")

    def bonnerManager(self):
        if self.PBTN_Bonner.isChecked():
            self.log("[ USER CMD ] => Bonner Activated")
            self.PBTN_Bonner.setStyleSheet(
                "background-color: #2aab20; color: white; border: none; border-radius: 5px;"
            )
            self.send_command("G98")
        else:
            self.log("[ USER CMD ] => Bonner Deactivated")
            self.PBTN_Bonner.setStyleSheet(
                "background-color: #eb4034; color: white; border: none; border-radius: 5px;"
            )
            self.send_command("G99")


    def on_x_speed_changed(self, value):
        self.log(f"[!] X Speed => {value}")

    def on_y_speed_changed(self, value):
        self.log(f"[!] Y Speed => {value}")


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
