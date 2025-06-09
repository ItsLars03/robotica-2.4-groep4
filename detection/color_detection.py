import cv2
import numpy as np
import time
from PIL import ImageEnhance, Image

# Movement tracking variables
red_movement_text = ""
red_movement_time = 0
green_movement_text = ""
green_movement_time = 0

prev_red_cx = 0
prev_green_cx = 0
movement_threshold = 1
display_duration = 1.0

def detect_colors(frame, self):
    global red_movement_text, red_movement_time, green_movement_text, green_movement_time, prev_red_cx, prev_green_cx, movement_threshold, display_duration


    # Convert the OpenCV image (BGR) to PIL format (RGB) for enhancement
    # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # pil_image = Image.fromarray(frame_rgb)
    #
    # # Enhance color saturation using PIL
    # enhanced_color = ImageEnhance.Color(pil_image).enhance(2)
    #
    # # Convert the enhanced PIL image back to OpenCV format (BGR)
    # enhanced_color_cv = np.array(enhanced_color)
    # enhanced_color_cv = cv2.cvtColor(enhanced_color_cv, cv2.COLOR_RGB2BGR)
    # enhanced_resized = cv2.resize(enhanced_color_cv, (width, height))
    # Resize for consistency
    frame = cv2.resize(frame, (self.width, self.height))

    # Optional: Contrast enhancement for better color separation at distance
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    frame = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    # Convert to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # === Color Ranges ===
    # Red (adjusted for distance/fading)
    lower_red1 = (0, 70, 100)
    upper_red1 = (10, 255, 255)
    lower_red2 = (170, 70, 100)
    upper_red2 = (180, 255, 255)

    # Green (broad + specific)
    lower_green1 = np.array([35, 100, 50])
    upper_green1 = np.array([85, 255, 255])
    lower_green2 = np.array([60, 100, 95])
    upper_green2 = np.array([70, 145, 135])

    # Blue background range (to mask out)
    lower_blue = np.array([85, 50, 150])
    upper_blue = np.array([105, 140, 255])
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    non_blue_mask = cv2.bitwise_not(blue_mask)

    # === Masks with background removed ===
    red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = (red1 | red2)

    green1 = cv2.inRange(hsv, lower_green1, upper_green1)
    green2 = cv2.inRange(hsv, lower_green2, upper_green2)
    green_mask = (green1 | green2)

    # Morphological operations to reduce noise
    kernel = np.ones((5, 5), np.uint8)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)

    # Adaptive area filtering based on resolution
    height, width = frame.shape[:2]
    scale = height * width / (self.width * self.height)
    min_area = int(10 * scale)

    # === Red Object Detection ===
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid_red_contours = [cnt for cnt in red_contours if cv2.contourArea(cnt) > min_area]

    if valid_red_contours:
        for contour in valid_red_contours:
            M = cv2.moments(contour)
            #if M["m00"] != 0:
                #cv2.drawContours(frame, [contour], 0, (0, 255, 255), 2)

        largest_contour = max(valid_red_contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.putText(frame, 'Red', (cx - 15, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
            cv2.drawContours(frame, [largest_contour], 0, (0, 255, 255), 2)

            current_time = time.time()
            if prev_red_cx is not None:
                if cx - prev_red_cx > movement_threshold:
                    red_movement_text = "MOVING RIGHT"
                    red_movement_time = current_time
                elif prev_red_cx - cx > movement_threshold:
                    red_movement_text = "MOVING LEFT"
                    red_movement_time = current_time

            if current_time - red_movement_time < display_duration and red_movement_text:
                cv2.putText(frame, red_movement_text, (cx - 50, cy + 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            prev_red_cx = cx

    # === Green Object Detection ===
    green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid_green_contours = [cnt for cnt in green_contours if cv2.contourArea(cnt) > min_area]

    if valid_green_contours:
        for contour in valid_green_contours:
            M = cv2.moments(contour)
            #if M["m00"] != 0:
                #cv2.drawContours(frame, [contour], 0, (0, 255, 0), 2)

        largest_contour = max(valid_green_contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.putText(frame, 'Green', (cx - 20, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            cv2.drawContours(frame, [largest_contour], 0, (0, 255, 0), 2)

            current_time = time.time()
            if prev_green_cx is not None:
                if cx - prev_green_cx > movement_threshold:
                    green_movement_text = "MOVING RIGHT"
                    green_movement_time = current_time
                elif prev_green_cx - cx > movement_threshold:
                    green_movement_text = "MOVING LEFT"
                    green_movement_time = current_time

            if current_time - green_movement_time < display_duration and green_movement_text:
                cv2.putText(frame, green_movement_text, (cx - 50, cy + 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            prev_green_cx = cx

    return frame
