import cv2
import numpy as np

MIN_RADIUS = 15
TOLERANCE = 20


def init_camera(device_index=0):
    """
    Initialiseert de videocapture.

    Argumenten:
        device_index (int): Index van het cameratoestel.

    Geeft terug:
        cv2.VideoCapture: Het Capture-object.

    Werpt:
        RuntimeError: Als de camera niet geopend kan worden.
    """
    cap = cv2.VideoCapture(device_index)
    if not cap.isOpened():
        raise RuntimeError("Kan de camera niet openen")
    return cap


def bepaal_richting(cx, cy, center_x, center_y, tol=TOLERANCE):
    """
    Bepaalt de richting van het object ten opzichte van een referentiepunt.

    Argumenten:
        cx (int): x-coördinaat van het object.
        cy (int): y-coördinaat van het object.
        center_x (int): x-coördinaat van het referentiepunt.
        center_y (int): y-coördinaat van het referentiepunt.
        tol (int): Tolerantie voor gecentreerd zijn.

    Geeft terug:
        str: Een van ['Gecentreerd', 'Links', 'Rechts', 'Omhoog', 'Omlaag'].
    """
    dx = cx - center_x
    dy = cy - center_y
    if abs(dx) < tol and abs(dy) < tol:
        return "Gecentreerd"
    if abs(dx) > abs(dy):
        return "Rechts" if dx > 0 else "Links"
    return "Omlaag" if dy > 0 else "Omhoog"


def maak_mask(hsv_frame):
    """
    Maakt een binaire mask voor rode tinten (bijv. aardbeien).

    Argumenten:
        hsv_frame (numpy.ndarray): Frame in HSV-kleurruimte.

    Geeft terug:
        numpy.ndarray: Binaire mask.
    """
    # Instellen van kleurgrenzen voor rood (onder- en boventinten)
    lower1 = np.array([0, 120, 120])
    upper1 = np.array([8, 255, 255])
    lower2 = np.array([172, 120, 120])
    upper2 = np.array([179, 255, 255])

    # Masken combineren
    mask1 = cv2.inRange(hsv_frame, lower1, upper1)
    mask2 = cv2.inRange(hsv_frame, lower2, upper2)
    mask = cv2.bitwise_or(mask1, mask2)

    # Morfologische bewerkingen om ruis te verwijderen
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask


def verwerk_frame(frame, prev_richting=None):
    """
    Verwerkt één frame: detecteert de grootste rode contour en bepaalt de richting.
    Tekent markeringen in het frame.

    Argumenten:
        frame (numpy.ndarray): BGR-frame van de camera.
        prev_richting (str, optioneel): Vorige richting om herhaling te voorkomen.

    Geeft terug:
        tuple: (bewerkt_frame, richting_str, prev_richting)
            bewerkt_frame (numpy.ndarray): Frame met getekende markeringen.
            richting_str (str of None): Bepaalde richting of None.
            prev_richting (str of None): Bijgewerkte vorige richting.
    """
    h, w = frame.shape[:2]
    center_x, center_y = w // 2, h // 2

    # Markeer het midden en kruislijnen
    cv2.drawMarker(frame, (center_x, center_y), (0, 0, 255), cv2.MARKER_CROSS, 20, 2)
    cv2.line(frame, (center_x, 0), (center_x, h), (0, 255, 0), 1)
    cv2.line(frame, (0, center_y), (w, center_y), (0, 255, 0), 1)

    # Converteer naar HSV en maak mask
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = maak_mask(hsv)

    # Vind contouren en selecteer de grootste
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    richting = None
    if contours:
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        if M["m00"] > 0 and radius > MIN_RADIUS:
            cx = int(M["m10"] / M["m00"] )
            cy = int(M["m01"] / M["m00"] )

            # Visualisatie van cirkel en rechthoek
            cv2.circle(frame, (int(x), int(y)), int(radius), (255, 0, 0), 2)
            x_r, y_r, w_r, h_r = cv2.boundingRect(c)
            cv2.rectangle(frame, (x_r, y_r), (x_r + w_r, y_r + h_r), (255, 0, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

            # Bepaal richting
            richting = bepaal_richting(cx, cy, center_x, center_y)
            if richting != prev_richting:
                print(f"Richting: {richting}")
                prev_richting = richting

    return frame, richting, prev_richting


def main():
    """
    Hoofdprogramma: initialiseert de camera en start de verwerkingslus.
    """
    cap = init_camera()
    prev_richting = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Verwerk frame en toon resultaat
        bewerkt, richting, prev_richting = verwerk_frame(frame, prev_richting)
        cv2.imshow("Aardbei Tracker", bewerkt)

        # Sluit bij toets 'q' of Esc
        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), 27):
            break

    # Ruim op na afloop
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
