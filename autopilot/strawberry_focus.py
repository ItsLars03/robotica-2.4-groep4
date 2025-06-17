import cv2
import numpy as np

# Functie om tracker te maken: KCF of CSRT
def create_tracker(name="CSRT"):
    if name == "KCF":
        return cv2.TrackerKCF_create()
    return cv2.TrackerCSRT_create()

# Initialisatie
tracker = create_tracker("CSRT")
initBB = None
tracking = False

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    vis = frame.copy()

    if not tracking:
        # Voorverwerking: blur en HSV-conversie
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # Rood masker
        lower1 = np.array([0, 100, 100])
        upper1 = np.array([10, 255, 255])
        lower2 = np.array([160, 100, 100])
        upper2 = np.array([180, 255, 255])
        mask_r1 = cv2.inRange(hsv, lower1, upper1)
        mask_r2 = cv2.inRange(hsv, lower2, upper2)
        mask_red = cv2.bitwise_or(mask_r1, mask_r2)

        # Optionele: groen kroontje masker (blend later)
        lower_g = np.array([35, 50, 50])
        upper_g = np.array([85, 255, 255])
        mask_green = cv2.inRange(hsv, lower_g, upper_g)

        # Morfologische bewerkingen
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        # Contourdetectie
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            # Grootste contour selecteren
            cnt = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(cnt)
            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = w / float(h) if h > 0 else 0
            perimeter = cv2.arcLength(cnt, True)
            circularity = 4 * np.pi * area / (perimeter**2) if perimeter > 0 else 0

            # Filters instellen: experimenteer met de drempels
            if (area > 1000 and
                0.85 < solidity < 1.0 and
                0.6 < aspect_ratio < 1.4 and
                0.2 < circularity < 0.7):

                # Optioneel: controleer groen kroontje boven rood
                roi_green = mask_green[y:y+int(h*0.2), x:x+w]
                if cv2.countNonZero(roi_green) > (0.05 * roi_green.size):
                    initBB = (x, y, w, h)
                    tracker = create_tracker("CSRT")
                    tracker.init(frame, initBB)
                    tracking = True

        # Debug: toon mask en groene kroon
        cv2.imshow("Mask Red", mask)
        cv2.imshow("Mask Green", mask_green)

    else:
        # Tracker update
        success, box = tracker.update(frame)
        if success:
            x, y, w, h = [int(v) for v in box]
            cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(vis, "Tracking aardbei", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            cv2.putText(vis, "Lost aardbei", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Strawberry Tracker", vis)
    key = cv2.waitKey(30) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        tracking = False

cap.release()
cv2.destroyAllWindows()