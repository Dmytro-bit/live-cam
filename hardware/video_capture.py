import time

import requests
from picamera2 import Picamera2

from devices.camera import Camera
from utils.config import CONFIG

if __name__ == "__main__":

    PORT = 9000
    camera = Camera()

    frame_interval = 1.0 / camera.fps

    while True:
        t0 = time.time()

        path = "/tmp/frame.jpg"
        camera.capture_file(path)

        with open(path, "rb") as f:
            files = {"frame": ("frame.jpg", f, "image/jpeg")}

            r = requests.post(f"0.0.0.0:{PORT}/video/upload_frame", headers={
                "certificate-string": CONFIG["certificate-string"],
                "device-id": CONFIG["device-id"],
            }, files=files, timeout=2)

            r.raise_for_status()

        dt = time.time() - t0
        time.sleep(max(0.0, frame_interval - dt))
