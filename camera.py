# File: camera.py

import cv2

class CameraHandler:
    def __init__(self, width, height, device_index=0):
        self.width = width
        self.height = height
        self.device_index = device_index
        self.cap = cv2.VideoCapture(self.device_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.camera_on = False

    def toggle(self):
        """Toggle de camerastatus (aan/uit)."""
        self.camera_on = not self.camera_on
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
