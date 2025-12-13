from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QPlainTextEdit,
    QCheckBox,
)
from PyQt5.QtCore import QTimer
import sys
import serial

class Window(QWidget):
    def __init__(self):
        super().__init__()

        # --- UI ---#
        self.setWindowTitle("New Person, Same Old Mistakes - Tame Impala")
        self.BTN_Connect = QPushButton("Connect")
        self.Console = QPlainTextEdit()
        self.Console.setReadOnly(True)

        layout_main = QVBoxLayout()
        layout_console = QVBoxLayout()

        self.checkbox_lvl1 = QCheckBox("Notification Level [!]")
        self.checkbox_lvl2 = QCheckBox("Notification Level [!!]")
        self.checkbox_lvl3 = QCheckBox("Notification Level [!!!]")

        layout_console.addWidget(self.checkbox_lvl1)
        layout_console.addWidget(self.checkbox_lvl2)
        layout_console.addWidget(self.checkbox_lvl3)

        layout_console.addWidget(self.BTN_Connect)
        layout_console.addWidget(self.Console)
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

    def log(self, text):
        if text.startswith("[!!!]") and not self.checkbox_lvl3.isChecked():
            return
        
        if text.startswith("[!!]") and not self.checkbox_lvl2.isChecked():
            return

        if text.startswith("[!]") and not self.checkbox_lvl1.isChecked():
            return

        self.Console.appendPlainText(text)

    def connect_arduino(self):
        try:
            self.ser = serial.Serial("/dev/ttyACM0", 115200, timeout=0)
            self.log("Connected to Arduino")
            self.timer.start(25)

        except serial.SerialException as e:
            self.log(f"Error connecting to Arduino: {e}")

    def read_serial(self):
        if self.ser and self.ser.in_waiting:
            try:
                line = self.ser.readline().decode(errors="ignore").strip()
                if line:
                    self.log(f"{line}")
            except Exception as e:
                self.log(f"Read error: {e}")


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())
