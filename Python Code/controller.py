from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from picamera2 import Picamera2
from libcamera import Transform

import cv2
import numpy as np
import time

import threading

class CameraWorker(QThread):
    frame_ready = pyqtSignal(object)
    err_signal = pyqtSignal(int, int, int, int)
    status = pyqtSignal(str)
    ATTACK = pyqtSignal(bool)

    
    X_STEP_SIZE = 0
    Y_STEP_SIZE = 0

    def __init__(self):
        super().__init__()
        self.running = False
        self.picam2 = None
        self.SLIDER_deadzone = 20

        self.attack_timer_start = None
        self.attack_emitted = False
        self.attack_timeout = 1

        self.X_SPEED = 4000
        self.Y_SPEED = 4000


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

            in_deadzone = False
            if contours:
                largest = max(contours, key=cv2.contourArea)
                if cv2.contourArea(largest) > 500:
                    x, y, bw, bh = cv2.boundingRect(largest)
                    obj_center = (x + bw // 2, y + bh // 2)

                    raw_err_x = (obj_center[0] - screen_center[0])
                    raw_err_y = (obj_center[1] - screen_center[1])

                    if abs(raw_err_x) < self.SLIDER_deadzone:
                        in_deadzone = True
                        err_x = 0
                    if abs(raw_err_y) < self.SLIDER_deadzone:
                        in_deadzone = True
                        err_y = 0
                    else:
                        err_x = raw_err_x
                        err_y = raw_err_y

                    if abs(err_x) < 50 and abs(err_x) > 0:
                        X_STEP_SIZE = 1
                        self.X_SPEED = 4000
                    if abs(err_x) >= 50 and abs(err_x) < 100:
                        X_STEP_SIZE = 2
                        self.X_SPEED = 4000
                    if abs(err_x) >= 100 and abs(err_x) < 200:
                        X_STEP_SIZE = 3
                        self.X_SPEED = 5000
                    if abs(err_x) >= 200:
                        X_STEP_SIZE = 3
                        self.X_SPEED = 5000

                    if abs(err_y) < 50 and abs(err_y) > 0:
                        Y_STEP_SIZE = 1
                        self.Y_SPEED = 3000
                    if abs(err_y) >= 50 and abs(err_y) < 100:
                        Y_STEP_SIZE = 2
                        self.Y_SPEED = 3000
                    if abs(err_y) >= 100 and abs(err_y) < 200:
                        Y_STEP_SIZE = 3
                        self.Y_SPEED = 4000
                    if abs(err_y) >= 200:
                        Y_STEP_SIZE = 3
                        self.Y_SPEED = 4000

                    if err_x > 0:
                        err_x = -X_STEP_SIZE
                    elif err_x < 0:
                        err_x = X_STEP_SIZE
                    if err_y > 0:
                        err_y = -Y_STEP_SIZE
                    elif err_y < 0:
                        err_y = Y_STEP_SIZE

                    cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)
                    cv2.circle(frame, obj_center, 3, (0, 0, 255), -1)
                    cv2.line(frame, screen_center, obj_center, (255, 0, 0), 2)

            if in_deadzone:
                if self.attack_timer_start is None:
                    self.attack_timer_start = time.monotonic()
                elif not self.attack_emitted and (time.monotonic() - self.attack_timer_start) >= self.attack_timeout:
                    self.attack_emitted = True
                    # self.status.emit("[!] ATTACK triggered")
                    self.ATTACK.emit(True)
            else:
                if self.attack_timer_start is not None or self.attack_emitted:
                    self.attack_timer_start = None
                    self.attack_emitted = False
                    # self.status.emit("[!] ATTACK triggered")
                    self.ATTACK.emit(False)   

            self.err_signal.emit(err_x, err_y, self.X_SPEED, self.Y_SPEED)
            # print(f"Error X: {err_x}, Error Y: {err_y}")
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