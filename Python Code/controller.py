from PyQt5.QtCore import QObject

class Controller(QObject):
    def __init__(self):
        super().__init__()

    def handle_button_click(self):
        print("Button clicked from Controller!")