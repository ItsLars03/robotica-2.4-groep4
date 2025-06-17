import cv2
# OpenCV-bibliotheek voor beeldverwerking en computer vision taken
import numpy as np
# NumPy-bibliotheek voor numerieke bewerkingen op arrays

class StrawberryDetector:
    def detect(self, cls, frame):
        # Hoofd detectiemethode: verwerkt een frame om aarbeien te vinden
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Zet de BGR-afbeelding om naar HSV-kleurruimte voor betere kleursegmentatie
        blurred = cv2.GaussianBlur(hsv, (17, 17), 0)
        # Pas Gaussian blur toe om ruis te verminderen en het HSV-beeld te verzachten

        gray_mask = cls._create_gray_mask(blurred)
        # Maak een masker voor onrijpe (groene/grijsachtige) aardbeien
        red_mask = cls._create_red_mask(hsv)
        # Maak een masker voor rijpe (rode) aardbeien

        cls._detect_unripe_strawberries(frame, gray_mask)
        # Detecteer en annoteer onrijpe aardbeien op het originele frame
        cls._detect_ripe_strawberries(frame, red_mask)
        # Detecteer en annoteer rijpe aardbeien op het originele frame

        return frame
        # Geef het geannoteerde frame terug

    def _create_gray_mask(self, hsv_blurred):
        # Genereer masker voor onrijpe aardbeien op basis van HSV-drempels
        lower_gray = np.array([34, 12, 8])
        # Ondergrens voor grijze/groene tinten in HSV
        upper_gray = np.array([97, 255, 140])
        # Bovengrens voor grijze/groene tinten in HSV
        kernel = np.ones((3, 3), np.uint8)
        # Structurerend element voor morfologische bewerkingen

        mask = cv2.inRange(hsv_blurred, lower_gray, upper_gray)
        # Drempel het vervaagde HSV-beeld om alleen de grijze/groene gebieden te krijgen
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        # Pas opening toe om kleine ruis te verwijderen
        return cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)
        # Dilateer het masker om kleine gaten te vullen en kenmerken te versterken

    def _create_red_mask(self, hsv):
        # Genereer masker voor rijpe aardbeien op basis van rode HSV-bereiken
        lower_red1 = np.array([0, 80, 50])
        # Ondergrens voor eerste segment van rode tinten
        upper_red1 = np.array([10, 255, 255])
        # Bovengrens voor eerste segment van rode tinten
        lower_red2 = np.array([160, 80, 50])
        # Ondergrens voor tweede segment van rode tinten nabij kleurwrapping
        upper_red2 = np.array([180, 255, 255])
        # Bovengrens voor tweede segment van rode tinten
        kernel = np.ones((3, 3), np.uint8)
        # Structurerend element voor morfologische bewerkingen

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        # Drempel HSV-beeld voor het eerste rode bereik
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        # Drempel HSV-beeld voor het tweede rode bereik
        red_mask = cv2.bitwise_or(mask1, mask2)
        # Combineer beide rode maskers
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
        # Verwijder kleine ruis uit het rode masker
        return cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
        # Sluit kleine openingen om rode gebieden te verenigen

    def _detect_unripe_strawberries(self, frame, mask):
        # Zoek contouren in het grijze masker voor mogelijke onrijpe aardbeien
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Bereken de oppervlakte van de contour
            if area < 550:
                # Sla kleine contouren over die waarschijnlijk geen aardbei zijn
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            # Bepaal de begrenzende rechthoek van de contour
            perimeter = cv2.arcLength(cnt, True)
            # Bereken de omtrek van de contour
            circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter != 0 else 0
            # Bereken circulariteit om niet-ronde vormen te filteren
            if circularity < 0.35:
                # Sla contouren over die te onregelmatig zijn
                continue

            aspect_ratio = float(w) / h if h != 0 else 0
            # Bereken de verhouding breedte/hoogte van de rechthoek
            if aspect_ratio < 0.75 or aspect_ratio > 1.33:
                # Sla contouren over met onwaarschijnlijke verhoudingen
                continue

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
            # Teken een rechthoek om de onrijpe aardbei
            cv2.putText(frame, "Onrijpe Aardbei", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
            # Label de gedetecteerde onrijpe aardbei

    def _detect_ripe_strawberries(self, frame, mask):
        # Zoek contouren in het rode masker voor mogelijke rijpe aardbeien
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Bereken de oppervlakte van de contour
            if area < 150:
                # Sla kleine ruiscontouren over
                continue

            perimeter = cv2.arcLength(cnt, True)
            # Bereken de omtrek van de contour
            if perimeter == 0:
                # Sla degenerate contouren over
                continue

            circularity = 4 * np.pi * area / (perimeter * perimeter)
            # Bereken circulariteit om vormen te filteren
            if circularity < 0.4:
                # Sla niet-ronde contouren over
                continue

            hull = cv2.convexHull(cnt)
            # Bereken de convexe hull van de contour
            hull_area = cv2.contourArea(hull)
            # Bereken de oppervlakte van de convexe hull
            if hull_area == 0:
                # Sla over als de hull-oppervlakte nul is
                continue

            solidity = float(area) / hull_area
            # Bereken solidity (vulratio) om concaviteit te controleren
            if solidity < 0.8:
                # Sla contouren over die te concave zijn
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            # Bepaal de begrenzende rechthoek van de contour
            aspect_ratio = float(w) / h
            # Bereken de verhouding breedte/hoogte van de rechthoek
            if 0.4 < aspect_ratio < 1.6:
                # Accepteer contouren met plausibele aardbei-verhoudingen
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                # Teken een rechthoek om de rijpe aardbei
                cv2.putText(frame, "Rijpe Aardbei", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                # Label de gedetecteerde rijpe aardbei
