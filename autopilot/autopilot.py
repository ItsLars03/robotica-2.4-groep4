import cv2
import numpy as np

# Video capture instellen
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Kan de camera niet openen")

# Functie om richting te bepalen
def bepaal_richting(obj_cx, obj_cy, center_x, center_y, tol=20):
    dx = obj_cx - center_x
    dy = obj_cy - center_y
    if abs(dx) < tol and abs(dy) < tol:
        return "Gecentreerd"
    if abs(dx) > abs(dy):
        return "Rechts" if dx > 0 else "Links"
    return "Omlaag" if dy > 0 else "Omhoog"

prev_richting = None
# Minimum straal om object als aardbei te beschouwen
MIN_RADIUS = 15

while True:
    ret, frame = cap.read()
    if not ret:
        break
    h, w = frame.shape[:2]
    center_x, center_y = w // 2, h // 2

    # Teken rood kruisje in het midden
    cv2.drawMarker(frame, (center_x, center_y), color=(0,0,255), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)
    # Teken groene assenlijnen
    cv2.line(frame, (center_x, 0), (center_x, h), (0,255,0), 1)
    cv2.line(frame, (0, center_y), (w, center_y), (0,255,0), 1)

    # Beeld converteren naar HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Aangescherpte drempels voor rode kleur (aardbeien)
    lower1 = np.array([0, 120, 120])
    upper1 = np.array([8, 255, 255])
    lower2 = np.array([172, 120, 120])
    upper2 = np.array([179, 255, 255])
    mask = cv2.bitwise_or(cv2.inRange(hsv, lower1, upper1), cv2.inRange(hsv, lower2, upper2))

    # Ruis verwijderen
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Contouren vinden
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    richting = None
    if contours:
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        if M["m00"] > 0 and radius > MIN_RADIUS:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            # Teken blauwe omcirkel
            cv2.circle(frame, (int(x), int(y)), int(radius), (255,0,0), 2)
            # Teken bounding vierkant (rechthoek) rond contour
            x_rect, y_rect, w_rect, h_rect = cv2.boundingRect(c)
            cv2.rectangle(frame, (x_rect, y_rect), (x_rect+w_rect, y_rect+h_rect), (255,0,0), 2)
            # Teken centroid
            cv2.circle(frame, (cx, cy), 5, (255,0,0), -1)
            # Bepaal en print richting als veranderd
            richting = bepaal_richting(cx, cy, center_x, center_y)
            if richting and richting != prev_richting:
                print(f"Richting: {richting}")
                prev_richting = richting

    # Venster weergeven
    cv2.imshow("Aardbei Tracker", frame)

    # Stop bij 'q' of ESC
    if cv2.waitKey(1) & 0xFF in (ord('q'), 27):
        break

# Opruimen
cap.release()
cv2.destroyAllWindows()
