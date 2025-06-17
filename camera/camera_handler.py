import requests
import cv2
# CameraHandler class to manage camera operations for the ESP32-CAM module
class CameraHandler:
    # Initialize the camera
    # The camera is configured to stream at a specified resolution and URL, it has its own acces point
    def __init__(self, width=800, height=480, stream_url='http://192.168.4.1:81/stream', base_url='http://192.168.4.1'):
        self.width = width
        self.height = height
        self.stream_url = stream_url
        self.base_url = base_url
        # set up the video capture
        self.cap = cv2.VideoCapture(self.stream_url)
        # set camera width and height
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.camera_on = False
        self.configure_camera()

    # configuring some of the internal settings of the camera (via http requests)
    def configure_camera(self):
        try:
            # Set camera CPU clock speed
            requests.get(f"{self.base_url}/xclk?xclk=24", timeout=2)
            # Set camera resolution to 800x480
            requests.get(f"{self.base_url}/control?var=quality&val=4", timeout=2)
            print("Camera configured.")
        except Exception as e:
            print("Configuration failed:", e)

    # Set LED intensity to control the camera's onboard LED (which is technically a flash)
    def _set_led_intensity(self, val):
        try:
            # Set LED intensity (0-255)
            requests.get(f"{self.base_url}/control?var=led_intensity&val={val}", timeout=2)
        except Exception as e:
            print("LED control failed:", e)

    # Toggle the camera on or off on the remote display
    def toggle_camera(self):
        self.camera_on = not self.camera_on
        self._set_led_intensity(255 if self.camera_on else 0)
        return self.camera_on

    # Read a frame from the camera
    def read_frame(self):
        if self.cap.isOpened() and self.camera_on:
            ret, frame = self.cap.read()
            return ret, frame
        return False, None

    # Release the camera resources
    def release(self):
        if self.cap.isOpened():
            self.cap.release()
