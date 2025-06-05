import cv2
import numpy as np
import requests
import time
from strawberry_detection import detect_objects

cap = cv2.VideoCapture(0)

print("Press ESC to exit.")

# Variables to track previous positions for both colors
prevRedCX = None
prevGreenCX = None
movementThreshold = 5  # Minimum pixel change to consider as movement
displayDuration = 1.0

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    # Call the detection function with simplified parameters
    frame, prevRedCX, prevGreenCX = detect_objects(
        frame, prevRedCX, prevGreenCX,
        movementThreshold, displayDuration
    )

    cv2.imshow('Strawberry Detection', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()