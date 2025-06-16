#!/usr/bin/env python3
import cv2
import numpy as np

# Parameters
ESP32_STREAM = 'http://192.168.4.1:81/stream'
DEADZONE = 5  # pixels

# Detecteer centroid van rode object
def detect_red(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (0,100,100), (10,255,255)) | cv2.inRange(hsv, (160,100,100), (179,255,255))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    c = max(contours, key=cv2.contourArea)
    M = cv2.moments(c)
    if M['m00'] == 0:
        return None
    return int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])

# Bepaal print-opdracht op basis van afwijking
def print_direction(dx, dy):
    commands = []
    if dx < 0:
        commands.append('move left')
    elif dx > 0:
        commands.append('move right')
    if dy < 0:
        commands.append('move up')
    elif dy > 0:
        commands.append('move down')
    if not commands:
        print('centered')
    else:
        print(', '.join(commands))

# Hoofdloop zonder motor-opdrachten
def main():
    cap = cv2.VideoCapture(ESP32_STREAM)

    cv2.namedWindow('Camera', cv2.WINDOW_NORMAL)

    try:
        while True:
            if not cap.grab():
                continue
            ret, frame = cap.retrieve()
            if not ret:
                continue

            # bepaal dynamische center
            h, w = frame.shape[:2]
            CX, CY = w // 2, h // 2

            target = detect_red(frame)
            if target:
                cx, cy = target
                dx = cx - CX
                dy = cy - CY
                # normaliseer naar -1,0,1
                dx = 0 if abs(dx) < DEADZONE else (1 if dx > 0 else -1)
                dy = 0 if abs(dy) < DEADZONE else (1 if dy > 0 else -1)
                print_direction(dx, dy)
                # optioneel: teken marker op het object
                cv2.drawMarker(frame, (cx, cy), (0,255,0), markerType=cv2.MARKER_CROSS, markerSize=10)

            # teken dynamische centerlijnen
            cv2.line(frame, (0, CY), (w, CY), (255, 0, 0), 1)
            cv2.line(frame, (CX, 0), (CX, h), (255, 0, 0), 1)

            cv2.imshow('Camera', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
