from picamera2 import Picamera2


class Camera:
    fps = 15
    width, height = 640, 480

    def __init__(self):
        self.camera = Picamera2()
        self.camera.configure(
            self.camera.create_video_configuration(
                main={"size": (self.width, self.height), "format": "RGB888"}
            )
        )
        self.camera.start()

    def capture_file(self, path):
        self.camera.capture_file()

    def __del__(self):
        self.camera.stop()
