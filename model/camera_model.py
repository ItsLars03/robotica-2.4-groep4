# model/camera_model.py

import cv2
from PIL import Image

class CameraModel:
    """
    Model dat verantwoordelijk is voor:
     - Openen/sluiten van de camera
     - Oproepen van frames
     - Wissen/togglen van camera-weergave
    """

    def __init__(self, width=640, height=480, camera_index=0):
        self.width = width
        self.height = height
        self.camera_index = camera_index
        self.cap = None
        self.camera_on = False

    def start_camera(self):
        """Open de camera en zet hem op de gewenste resolutie."""
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.camera_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.camera_on = True

    def stop_camera(self):
        """Sluit de camera veilig af."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.camera_on = False

    def toggle_camera(self):
        """
        Zet camera_on True ↔ False.
        Als je uitzet, blijft het cap-object gewoon bestaan (of je kunt kiezen om te releasen).
        Hier kiezen we ervoor om cap actief te laten, maar enkel zwarte beelden terug te geven.
        """
        if self.cap is None:
            # Nog niet gestart → start hem
            self.start_camera()
        else:
            self.camera_on = not self.camera_on

    def get_frame(self):
        """
        Retourneert een PIL.Image van een current frame in RGB.
        Als camera_on == False of er is een leesfout, maak dan een zwart plaatje.
        """
        from PIL import ImageDraw

        # Als camera nog niet gestart is, of explicit uit is, gewoon zwart
        if (self.cap is None) or (not self.camera_on):
            return Image.new("RGB", (self.width, self.height), (0, 0, 0))

        ret, frame = self.cap.read()
        if not ret:
            # Fallback: zwart plaatje
            return Image.new("RGB", (self.width, self.height), (0, 0, 0))

        # Converteer BGR → RGB en maak PIL-image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        return img

    def release(self):
        """ Sluit camera af als View/Controller eindigt. """
        self.stop_camera()
