from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from picamera2 import Picamera2
from libcamera import Transform

import cv2
import numpy as np
import time


class CameraWorker(QThread):
    frame_ready = pyqtSignal(object)
    err_signal = pyqtSignal(int, int)
    status = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = False
        self.picam2 = None
        self.SLIDER_deadzone = 10

    def run(self):
        self.picam2 = Picamera2()
        self.picam2.configure(
            self.picam2.create_preview_configuration(
                main={"format": "BGR888", "size": (640, 480)},
                transform=Transform(rotation=180),
            )
        )
        
        self.picam2.start()
        time.sleep(1.5)
        
        self.picam2.set_controls({"AfMode": 2})
        self.status.emit("[!] Camera started")
        self.running = True

        while self.running:
            frame = self.picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            h, w, _ = frame.shape
            screen_center = (w // 2, h // 2)
            
            err_x, err_y = 0, 0

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_yellow = np.array([20, 100, 100])
            upper_yellow = np.array([30, 255, 255])
            
            mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
            mask = cv2.GaussianBlur(mask, (5, 5), 0)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            
            contours, _ = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            cv2.rectangle(frame, (w//2 - self.SLIDER_deadzone, h//2 - self.SLIDER_deadzone),
                                  (w//2 + self.SLIDER_deadzone, h//2 + self.SLIDER_deadzone), (255, 255, 0), 2)
            cv2.circle(frame, screen_center, 5, (255, 0, 255), -1)

            if contours:
                largest = max(contours, key=cv2.contourArea)
                if cv2.contourArea(largest) > 500:
                    x, y, bw, bh = cv2.boundingRect(largest)
                    obj_center = (x + bw // 2, y + bh // 2)

                    err_x = (obj_center[0] - screen_center[0])
                    err_y = (obj_center[1] - screen_center[1])

                    if abs(err_x) < self.SLIDER_deadzone:
                        err_x = 0
                    if abs(err_y) < self.SLIDER_deadzone:
                        err_y = 0

                    

                    cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)
                    cv2.circle(frame, obj_center, 5, (0, 0, 255), -1)
                    cv2.line(frame, screen_center, obj_center, (255, 0, 0), 2)
            
            self.err_signal.emit(err_x, err_y)
            self.frame_ready.emit(frame)
            time.sleep(0.01)

        self.picam2.stop()
        self.status.emit("[!] Camera stopped")
    
    @pyqtSlot(int)
    def update_deadzone(self, value):
        self.SLIDER_deadzone = value
        self.status.emit(f"[!] Deadzone updated to: {value}")

    def stop(self):
        self.running = False
