# File: camera.py
import requests

import cv2

URL = 'http://192.168.4.1'
STREAM = URL + ":81/stream"

class CameraHandler:
    def __init__(self, width, height, device_url=STREAM):
        self.width = width
        self.height = height
        self.device_index = device_url
        self.cap = cv2.VideoCapture(self.device_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.camera_on = False
        self.config()

    def config(self):
        try:
            requests.get(URL + "/xclk?xclk=24", timeout=2)
            requests.get(URL + "/control?var=framesize&val=12", timeout=2)
            print("Camera configured")
        except Exception as e:
            print("Camera configuration failed:", e)

    def toggle_led(self):
        if self.camera_on:
            try:
                requests.get(URL + "/control?var=led_intensity&val=255", timeout=2)
            except Exception as e:
                print("LED toggle failed:", e)
        if not self.camera_on:
            try:
                requests.get(URL + "/control?var=led_intensity&val=0", timeout=2)
            except Exception as e:
                print("LED toggle failed:", e)

    def toggle(self):
        """Toggle de camerastatus (aan/uit)."""
        self.camera_on = not self.camera_on
        self.toggle_led()
        return self.camera_on

    def read_frame(self):
        """
        Lees één frame van de camera.
        Retourneert (ret, frame) of (False, None) als niet beschikbaar.
        """
        if self.cap.isOpened() and self.camera_on:
            ret, frame = self.cap.read()
            return ret, frame
        else:
            return False, None

    def release(self):
        """Maak de camera vrij."""
        if self.cap.isOpened():
            self.cap.release()
