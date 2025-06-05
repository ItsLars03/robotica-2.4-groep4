import cv2
import numpy as np
import time

# Movement tracking variables
red_movement_text = ""
red_movement_time = 0
green_movement_text = ""
green_movement_time = 0

def detect_objects(frame, prev_red_cx, prev_green_cx,
                   movement_threshold=3, display_duration=1.0):
    """
    Detect red and green objects in the frame and track their movements.

    Returns:
        tuple: (processed_frame, prev_red_cx, prev_green_cx)
    """
    global red_movement_text, red_movement_time, green_movement_text, green_movement_time

    frame = cv2.resize(frame, (320, 240))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Red color range (in HSV)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([15, 255, 255])
    lower_red2 = np.array([160, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # Green color range (in HSV)
    lower_green = np.array([35, 100, 50])
    upper_green = np.array([85, 255, 255])

    # Create color masks
    red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = red1 | red2
    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    # Process red objects
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if red_contours:
        all_points = np.vstack(red_contours)
        hull = cv2.convexHull(all_points)
        cv2.drawContours(frame, [hull], 0, (0, 255, 255), 2)

        M = cv2.moments(hull)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.putText(frame, 'Red', (cx - 15, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

            if prev_red_cx is not None:
                current_time = time.time()
                if cx - prev_red_cx > movement_threshold:
                    red_movement_text = "MOVING RIGHT"
                    red_movement_time = current_time
                    cv2.putText(frame, red_movement_text, (cx - 50, cy + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                elif prev_red_cx - cx > movement_threshold:
                    red_movement_text = "MOVING LEFT"
                    red_movement_time = current_time
                    cv2.putText(frame, red_movement_text, (cx - 50, cy + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                else:
                    if current_time - red_movement_time < display_duration and red_movement_text:
                        cv2.putText(frame, red_movement_text, (cx - 50, cy + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            prev_red_cx = cx

    # Process green objects
    green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if green_contours:
        all_points = np.vstack(green_contours)
        hull = cv2.convexHull(all_points)
        cv2.drawContours(frame, [hull], 0, (0, 255, 0), 2)

        M = cv2.moments(hull)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.putText(frame, 'Green', (cx - 20, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

            if prev_green_cx is not None:
                current_time = time.time()
                if cx - prev_green_cx > movement_threshold:
                    green_movement_text = "MOVING RIGHT"
                    green_movement_time = current_time
                    cv2.putText(frame, green_movement_text, (cx - 50, cy + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                elif prev_green_cx - cx > movement_threshold:
                    green_movement_text = "MOVING LEFT"
                    green_movement_time = current_time
                    cv2.putText(frame, green_movement_text, (cx - 50, cy + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                else:
                    if current_time - green_movement_time < display_duration and green_movement_text:
                        cv2.putText(frame, green_movement_text, (cx - 50, cy + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            prev_green_cx = cx

    return frame, prev_red_cx, prev_green_cx