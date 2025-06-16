import requests
import cv2

class CameraHandler:
    def __init__(self, width=800, height=480, stream_url='http://192.168.4.1:81/stream', base_url='http://192.168.4.1'):
        self.width = width
        self.height = height
        self.stream_url = stream_url
        self.base_url = base_url

        self.cap = cv2.VideoCapture(self.stream_url)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        self.camera_on = False
        self.configure_camera()

    def configure_camera(self):
        try:
            requests.get(f"{self.base_url}/xclk?xclk=24", timeout=2)
            requests.get(f"{self.base_url}/control?var=quality&val=4", timeout=2)
            print("Camera configured.")
        except Exception as e:
            print("Configuration failed:", e)

    def _set_led_intensity(self, val):
        try:
            requests.get(f"{self.base_url}/control?var=led_intensity&val={val}", timeout=2)
        except Exception as e:
            print("LED control failed:", e)

    def toggle_camera(self):
        self.camera_on = not self.camera_on
        self._set_led_intensity(255 if self.camera_on else 0)
        return self.camera_on

    def read_frame(self):
        if self.cap.isOpened() and self.camera_on:
            ret, frame = self.cap.read()
            return ret, frame
        return False, None

    def release(self):
        if self.cap.isOpened():
            self.cap.release()
