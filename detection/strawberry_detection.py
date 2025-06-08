import cv2
import numpy as np

def detect_strawberries(frame, self):
    frame = cv2.resize(frame, (self.width, self.height))  # optional: smaller window
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    blurred = cv2.GaussianBlur(hsv, (17, 17), 0)

    # lower_gray = np.array([128, 40, 60])
    # upper_gray = np.array([250, 75, 255])
    lower_gray = np.array([60, 5, 60])
    upper_gray = np.array([120, 45, 255])
    mask = cv2.inRange(blurred, lower_gray, upper_gray)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

    result_gray = cv2.bitwise_and(frame, frame, mask=mask)

    # grayBlur = cv2.GaussianBlur(gray, (25, 25), 0)
    # ret, th = cv2.threshold(grayBlur, 180, 255, cv2.THRESH_BINARY_INV)
    # contours, hierarchy = cv2.findContours(th, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:

        area = cv2.contourArea(cnt)
        if area < 550:
            continue
        # if area > 1000:
        #     continue

        #print(cnt)

        x, y, w, h = cv2.boundingRect(cnt)

        # bounding_area = w * h
        # if bounding_area == 0:
        #     continue

        perimeter = cv2.arcLength(cnt, True)
        # if perimeter == 0:
        #     continue

        circularity = 4 * np.pi * area / (perimeter * perimeter)
        if circularity < 0.35:
            continue

        aspect_ratio = float(w) / h if h != 0 else 0
        if aspect_ratio < 0.75 or aspect_ratio > 1.33:
            continue

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        cv2.putText(frame, "Gray Berry", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
    return frame