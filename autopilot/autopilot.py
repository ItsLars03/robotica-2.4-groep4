#!/usr/bin/env python3
import cv2
import numpy as np
from gpiozero import Motor
import time


# Parameters
ESP32_STREAM = 'http://192.168.4.1:81/stream'
DEADZONE = 5  # pixels
SPEED = 0.1   # motor speed (0.0 to 1.0)
# Motor setup: adjust GPIO pins to your wiring
# Example: left motor on pins 17 (forward) and 18 (backward)
#          right motor on pins 22 (forward) and 23 (backward)
left_motor = Motor(forward=17, backward=18)
right_motor = Motor(forward=22, backward=23)

# Detect centroid of red object
def detect_red(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (0,100,100), (10,255,255)) |
           cv2.inRange(hsv, (160,100,100), (179,255,255))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    c = max(contours, key=cv2.contourArea)
    M = cv2.moments(c)
    if M['m00'] == 0:
        return None
    return int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])

# Send motor commands based on direction
def apply_motor_command(dx, dy):
    # Stop both motors first
    left_motor.stop()
    right_motor.stop()

    # Rotate or drive based on dx, dy
    if dx < 0:
        # move left: turn left slowly
        left_motor.backward(SPEED)
        right_motor.forward(SPEED)
    elif dx > 0:
        # move right: turn right slowly
        left_motor.forward(SPEED)
        right_motor.backward(SPEED)
    elif dy < 0:
        # move up: forward
        left_motor.forward(SPEED)
        right_motor.forward(SPEED)
    elif dy > 0:
        # move down: backward
        left_motor.backward(SPEED)
        right_motor.backward(SPEED)
    else:
        # centered
        pass

# Main loop without print statements
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

            # dynamic center
            h, w = frame.shape[:2]
            CX, CY = w // 2, h // 2

            target = detect_red(frame)
            if target:
                cx, cy = target
                dx = cx - CX
                dy = cy - CY
                # normalize to -1,0,1
                dx = 0 if abs(dx) < DEADZONE else (1 if dx > 0 else -1)
                dy = 0 if abs(dy) < DEADZONE else (1 if dy > 0 else -1)
                apply_motor_command(dx, dy)

                # optional: draw marker on object
                cv2.drawMarker(frame, (cx, cy), (0,255,0), markerType=cv2.MARKER_CROSS, markerSize=10)

            # draw center lines
            cv2.line(frame, (0, CY), (w, CY), (255, 0, 0), 1)
            cv2.line(frame, (CX, 0), (CX, h), (255, 0, 0), 1)

            cv2.imshow('Camera', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # small delay to allow motors to respond smoothly
            time.sleep(0.02)
    finally:
        # ensure motors stop on exit
        left_motor.stop()
        right_motor.stop()
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
