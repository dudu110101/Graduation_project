# camera.py

from picamera2 import Picamera2

from config import (
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    CAMERA_FORMAT
)


class Camera:

    def __init__(self):

        self.camera = Picamera2()

        self.config = self.camera.create_preview_configuration(
            main={
                "size": (
                    CAMERA_WIDTH,
                    CAMERA_HEIGHT
                ),
                "format": CAMERA_FORMAT
            }
        )

        self.camera.configure(self.config)

        self.started = False


    def start(self):

        if not self.started:

            self.camera.start()

            self.started = True


    def capture(self):

        if not self.started:
            raise RuntimeError(
                "Camera is not started."
            )

        return self.camera.capture_array()


    def stop(self):

        if self.started:

            self.camera.stop()

            self.started = False