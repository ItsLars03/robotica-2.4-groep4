import cv2
import numpy as np

class StrawberryDetector:
    def detect(self, cls, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        blurred = cv2.GaussianBlur(hsv, (17, 17), 0)

        gray_mask = cls._create_gray_mask(blurred)
        red_mask = cls._create_red_mask(hsv)

        cls._detect_unripe_strawberries(frame, gray_mask)
        cls._detect_ripe_strawberries(frame, red_mask)

        return frame

    def _create_gray_mask(self, hsv_blurred):
        lower_gray = np.array([34, 12, 8])
        upper_gray = np.array([97, 255, 140])
        kernel = np.ones((3, 3), np.uint8)

        mask = cv2.inRange(hsv_blurred, lower_gray, upper_gray)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        return cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

    def _create_red_mask(self, hsv):
        lower_red1 = np.array([0, 80, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 80, 50])
        upper_red2 = np.array([180, 255, 255])
        kernel = np.ones((3, 3), np.uint8)

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(mask1, mask2)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
        return cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

    def _detect_unripe_strawberries(self, frame, mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 550:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            perimeter = cv2.arcLength(cnt, True)
            circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter != 0 else 0
            if circularity < 0.35:
                continue

            aspect_ratio = float(w) / h if h != 0 else 0
            if aspect_ratio < 0.75 or aspect_ratio > 1.33:
                continue

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
            cv2.putText(frame, "Unripe Strawberry", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

    def _detect_ripe_strawberries(self, frame, mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 150:
                continue

            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue

            circularity = 4 * np.pi * area / (perimeter * perimeter)
            if circularity < 0.4:
                continue

            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            if hull_area == 0:
                continue

            solidity = float(area) / hull_area
            if solidity < 0.8:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h
            if 0.4 < aspect_ratio < 1.6:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, "Ripe Strawberry", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
