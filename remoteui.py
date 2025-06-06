# File: remoteui.py

import tkinter as tk

import cv2
from PIL import Image, ImageTk
from camera import CameraHandler

class SimpleCameraApp:
    def __init__(self, width=1040, height=480):
        self.width = width
        self.height = height

        # Camera-handler importeren
        self.camera = CameraHandler(width=self.width, height=self.height)

        # Tkinter-venster aanmaken
        self.root = tk.Tk()
        self.root.title("Eenvoudige Camera App")
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False, False)

        # Label voor videofeed (of zwart vlak)
        self.lbl_video = tk.Label(self.root)
        self.lbl_video.place(x=0, y=0, relwidth=1, relheight=1)

        # Basislettertype voor alle knoppen
        btn_font = ("Helvetica", 12, "bold")

        # CAM-knop (rechtsboven)
        self.btn_cam = tk.Button(
            self.root,
            text="CAM",
            font=btn_font,
            padx=8, pady=4,
            command=self.toggle_camera
        )
        # Symmetrisch: 90% van de breedte, 5% van de hoogte
        self.btn_cam.place(relx=0.90, rely=0.05, anchor="center")

        # MODE-knop (middenboven)
        self.btn_mode = tk.Button(
            self.root,
            text="AUTO / MANUAL",
            font=btn_font,
            padx=12, pady=6,
            command=self.on_mode_click
        )
        # Precies gecentreerd bovenaan (50% van breedte, 5% van hoogte)
        self.btn_mode.place(relx=0.50, rely=0.05, anchor="center")

        # GRIPPER-knop (linksonder)
        self.btn_gripper = tk.Button(
            self.root,
            text="GRIPPER",
            font=btn_font,
            padx=10, pady=4,
            command=self.on_gripper_click
        )
        # Symmetrisch: 10% van de breedte, 90% van de hoogte
        self.btn_gripper.place(relx=0.10, rely=0.90, anchor="center")

        # STOP-knop (rechtsonder)
        self.btn_stop = tk.Button(
            self.root,
            text="STOP",
            font=btn_font,
            padx=10, pady=4,
            command=self.on_stop_click
        )
        # Symmetrisch: 90% van de breedte, 90% van de hoogte
        self.btn_stop.place(relx=0.90, rely=0.90, anchor="center")

        # Start video-update loop
        self.root.after(0, self.video_loop)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def toggle_camera(self):
        """Zet de camera aan/uit en update knopkleuren."""
        is_on = self.camera.toggle()
        if is_on:
            self.btn_cam.config(fg="#333333", bg="#ffffff")
        else:
            self.btn_cam.config(fg="#ff0000", bg="#000000")

    def on_mode_click(self):
        print("MODE-knop ingedrukt!")

    def on_gripper_click(self):
        print("GRIPPER-knop ingedrukt!")

    def on_stop_click(self):
        print("STOP-knop ingedrukt!")
        # Bij STOP gewoon de camera uitzetten, maar venster open laten
        if self.camera.camera_on:
            self.camera.toggle()
        self.btn_cam.config(fg="#ff0000", bg="#000000")

    def on_close(self):
        """Wordt aangeroepen als het venster wordt gesloten."""
        self.camera.release()
        self.root.destroy()

    def video_loop(self):
        """Lees elke ~15 ms een frame en toon het."""
        ret, frame = self.camera.read_frame()
        if ret:
            # BGR → RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)
        else:
            # Camera uit of leesfout: zwart vlak
            pil_img = Image.new("RGB", (self.width, self.height), (0, 0, 0))

        imgtk = ImageTk.PhotoImage(image=pil_img)
        self.lbl_video.imgtk = imgtk  # referentie bewaren
        self.lbl_video.config(image=imgtk)

        # Plan de volgende update na 15 ms (~60 fps)
        self.root.after(15, self.video_loop)

    def run(self):
        self.root.mainloop()
