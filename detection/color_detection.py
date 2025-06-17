import cv2
import numpy as np
import time

class ColorDetector:
    red_movement_text = ""
    red_movement_time = 0
    green_movement_text = ""
    green_movement_time = 0

    def create_color_masks(self, hsv):
        """Maakt kleurmaskers voor rode en groene objecten"""
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([15, 255, 255])
        lower_red2 = np.array([160, 120, 70])
        upper_red2 = np.array([180, 255, 255])

        lower_green1 = np.array([35, 100, 50])
        upper_green1 = np.array([85, 255, 255])

        lower_green2 = np.array([60,100,95])
        upper_green2 = np.array([70,145,135])

        red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = red1 | red2

        green1 = cv2.inRange(hsv, lower_green1, upper_green1)
        green2 = cv2.inRange(hsv, lower_green2, upper_green2)
        green_mask = green1 | green2
        
        return red_mask, green_mask

    def find_valid_contours(self, mask, min_area=1):
        """Vindt geldige contouren boven een minimale oppervlakte"""
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

    def draw_contours_on_frame(self, frame, contours, color):
        """Tekent alle contouren op het frame met de gegeven kleur"""
        for contour in contours:
            cv2.drawContours(frame, [contour], 0, color, 2)

    def get_centroid_from_largest_contour(self, contours):
        """Berekent het middelpunt van de grootste contour"""
        if not contours:
            return None, None
        
        largest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return cx, cy
        return None, None

    def draw_object_label(self, frame, cx, cy, label, color):
        """Tekent een label op het object"""
        if cx is not None and cy is not None:
            cv2.putText(frame, label, (cx - 15, cy - 10),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    def determine_movement_direction(self, current_cx, prev_cx, movement_threshold):
        """Bepaalt de bewegingsrichting op basis van huidige en vorige x-positie"""
        if prev_cx is None:
            return None
        
        if current_cx - prev_cx > movement_threshold:
            return "MOVING RIGHT"
        elif prev_cx - current_cx > movement_threshold:
            return "MOVING LEFT"
        return None

    def update_movement_text(self, movement_direction, movement_text_attr, movement_time_attr):
        """Werkt de bewegingstekst en tijd bij voor een specifieke kleur"""
        current_time = time.time()
        if movement_direction:
            setattr(self, movement_text_attr, movement_direction)
            setattr(self, movement_time_attr, current_time)

    def draw_movement_text_if_needed(self, frame, cx, cy, movement_text_attr, movement_time_attr, color, display_duration):
        """Tekent bewegingstekst als deze nog zichtbaar moet zijn"""
        current_time = time.time()
        movement_text = getattr(self, movement_text_attr)
        movement_time = getattr(self, movement_time_attr)
        
        if current_time - movement_time < display_duration and movement_text:
            cv2.putText(frame, movement_text, (cx - 50, cy + 25),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    def process_red_objects(self, frame, red_mask, prev_red_cx, movement_threshold, display_duration):
        """Verwerkt rode objecten en detecteert hun beweging"""
        valid_contours = self.find_valid_contours(red_mask)
        
        if not valid_contours:
            return prev_red_cx
        
        self.draw_contours_on_frame(frame, valid_contours, (0, 255, 255))
        cx, cy = self.get_centroid_from_largest_contour(valid_contours)
        
        if cx is not None and cy is not None:
            self.draw_object_label(frame, cx, cy, 'Red', (0, 255, 255))
            
            movement_direction = self.determine_movement_direction(cx, prev_red_cx, movement_threshold)
            self.update_movement_text(movement_direction, 'red_movement_text', 'red_movement_time')
            self.draw_movement_text_if_needed(frame, cx, cy, 'red_movement_text', 'red_movement_time', 
                                            (0, 255, 255), display_duration)
            prev_red_cx = cx
        
        return prev_red_cx

    def process_green_objects(self, frame, green_mask, prev_green_cx, movement_threshold, display_duration):
        """Verwerkt groene objecten en detecteert hun beweging"""
        valid_contours = self.find_valid_contours(green_mask)
        
        if not valid_contours:
            return prev_green_cx
        
        self.draw_contours_on_frame(frame, valid_contours, (0, 255, 0))
        cx, cy = self.get_centroid_from_largest_contour(valid_contours)
        
        if cx is not None and cy is not None:
            self.draw_object_label(frame, cx, cy, 'Green', (0, 255, 0))
            
            movement_direction = self.determine_movement_direction(cx, prev_green_cx, movement_threshold)
            self.update_movement_text(movement_direction, 'green_movement_text', 'green_movement_time')
            self.draw_movement_text_if_needed(frame, cx, cy, 'green_movement_text', 'green_movement_time', 
                                            (0, 255, 0), display_duration)
            prev_green_cx = cx
        
        return prev_green_cx

    def detect_objects(self, frame, prev_red_cx, prev_green_cx,
                       movement_threshold=3, display_duration=1.0):
        """Hoofdfunctie die objecten detecteert en hun beweging volgt"""
        frame = cv2.resize(frame, (320, 240))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        red_mask, green_mask = self.create_color_masks(hsv)
        
        prev_red_cx = self.process_red_objects(frame, red_mask, prev_red_cx, movement_threshold, display_duration)
        prev_green_cx = self.process_green_objects(frame, green_mask, prev_green_cx, movement_threshold, display_duration)

        return frame, prev_red_cx, prev_green_cx