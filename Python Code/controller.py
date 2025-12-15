from picamera2 import Picamera2
from libcamera import Transform
import cv2
import time

picam2 = Picamera2()

picam2.configure(
    picam2.create_preview_configuration(
        main={"format": "BGR888", "size": (640, 480)},
        transform=Transform(rotation=180)
    )
)

picam2.start()
time.sleep(1.5)
picam2.set_controls({
    "AfMode": 2  # Continuous AF
})

while True:
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imshow("Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
