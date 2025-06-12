import cv2
import numpy as np


# Callback functie voor trackbars (moet meegegeven worden, doet verder niets)
def nothing(x):
    pass


def main():
    # Open de standaard camera (0). Pas het getal aan als je een andere camera wilt gebruiken.
    cap = cv2.VideoCapture("http://192.168.4.1:81/stream")
    if not cap.isOpened():
        print("Error: kon de camera niet openen")
        return

    # Maak een venster aan voor de HSV trackbars
    cv2.namedWindow('HSV Threshold')

    # Trackbars voor hue, saturation en value ranges
    cv2.createTrackbar('Hue Min', 'HSV Threshold', 0, 179, nothing)
    cv2.createTrackbar('Hue Max', 'HSV Threshold', 179, 179, nothing)
    cv2.createTrackbar('Sat Min', 'HSV Threshold', 0, 255, nothing)
    cv2.createTrackbar('Sat Max', 'HSV Threshold', 255, 255, nothing)
    cv2.createTrackbar('Val Min', 'HSV Threshold', 0, 255, nothing)
    cv2.createTrackbar('Val Max', 'HSV Threshold', 255, 255, nothing)

    while True:
        # Lees een frame van de camera
        ret, frame = cap.read()
        if not ret:
            print("Error: kon geen frame lezen van de camera")
            break

        # Optioneel: resize voor consistente weergave
        frame = cv2.resize(frame, (600, int(600 * frame.shape[0] / frame.shape[1])))

        # Converteer naar HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Lees waarden van de trackbars
        h_min = cv2.getTrackbarPos('Hue Min', 'HSV Threshold')
        h_max = cv2.getTrackbarPos('Hue Max', 'HSV Threshold')
        s_min = cv2.getTrackbarPos('Sat Min', 'HSV Threshold')
        s_max = cv2.getTrackbarPos('Sat Max', 'HSV Threshold')
        v_min = cv2.getTrackbarPos('Val Min', 'HSV Threshold')
        v_max = cv2.getTrackbarPos('Val Max', 'HSV Threshold')

        # Stel de onder- en bovengrens in HSV in
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])

        # Maak de mask
        mask = cv2.inRange(hsv, lower, upper)

        # Toon origineel en mask naast elkaar
        mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        combined = np.hstack((frame, mask_bgr))
        cv2.imshow('HSV Threshold', combined)

        # Stoppen bij 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Opruimen
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
