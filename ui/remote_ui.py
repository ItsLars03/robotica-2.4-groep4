# File: remote_py

import tkinter as tk

import cv2
from PIL import Image, ImageTk
from camera.camera import CameraHandler
from detection.color_detection import detect_colors
from detection.strawberry_detection import detect_strawberries
from motor.motor_controller import MotorController


class RemoteUI:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.camera = CameraHandler(width=self.width, height=self.height)
        self.detecting_mode = None

        # === Theme ===
        self.bg_color = "#0f1c3f"      # Retro dark blue
        self.btn_color = "#1e3f66"     # Button background
        self.btn_active = "#3399ff"    # Active button
        self.btn_fg = "#ffffff"        # Button text
        self.btn_font = ("Helvetica", 12, "bold")

        # === Main window ===
        self.root = tk.Tk()
        self.root.title("Remote UI")
        self.root.geometry(f"{width}x{height}")
        self.root.configure(bg=self.bg_color)
        self.root.resizable(False, False)

        # === Video label ===
        self.lbl_video = tk.Label(self.root, bg=self.bg_color)
        self.lbl_video.place(x=0, y=0, relwidth=1, relheight=1)

        # === Buttons ===
        self.btn_cam = self._styled_button("CAM", self.toggle_camera)
        self.btn_cam.place(relx=0.945, rely=0.06, anchor="center")

        self.btn_mode = self._styled_button("AUTO / MANUAL", self.on_mode_click)
        self.btn_mode.place(relx=0.11, rely=0.06, anchor="center")

        self.btn_gripper = self._styled_button("GRIPPER", self.on_gripper_click)
        self.btn_gripper.place(relx=0.079, rely=0.17, anchor="center")

        self.btn_stop = self._styled_button("STOP", self.on_stop_click)
        self.btn_stop.place(relx=0.942, rely=0.935, anchor="center")

        self.btn_cdetec = self._styled_button("Color Detection", self.color_detect_click)
        self.btn_cdetec.place(relx=0.892, rely=0.17, anchor="center")

        self.btn_sdetec = self._styled_button("Strawberry Detection", self.strawberry_detect_click)
        self.btn_sdetec.place(relx=0.868, rely=0.29, anchor="center")

        self.root.after(0, self.video_loop)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _styled_button(self, text, command):
        return tk.Button(
            self.root,
            text=text,
            font=self.btn_font,
            bg=self.btn_color,
            fg=self.btn_fg,
            activebackground=self.btn_active,
            activeforeground="#ffffff",
            relief="flat",
            bd=2,
            padx=10, pady=6,
            command=command
        )

    def toggle_camera(self):
        is_on = self.camera.toggle()
        if is_on:
            self.btn_cam.config(bg=self.btn_active, fg="#ffffff")
        else:
            self.btn_cam.config(bg="#000000", fg="#ff4444")

    def on_mode_click(self):
        print("MODE-knop ingedrukt!")

    def on_gripper_click(self):
        print("GRIPPER-knop ingedrukt!")
        MotorController.toggle_gripper()

    def on_stop_click(self):
        print("STOP-knop ingedrukt!")
        if self.camera.camera_on:
            self.camera.toggle()
        self.btn_cam.config(bg="#000000", fg="#ff4444")

    def color_detect_click(self):
        self.detecting_mode = "color" if self.detecting_mode != "color" else None
        self.update_detection_buttons()

    def strawberry_detect_click(self):
        self.detecting_mode = "strawberry" if self.detecting_mode != "strawberry" else None
        self.update_detection_buttons()

    def update_detection_buttons(self):
        if self.detecting_mode == "color":
            self.btn_cdetec.config(bg="#00cc66")
            self.btn_sdetec.config(bg=self.btn_color)
        elif self.detecting_mode == "strawberry":
            self.btn_cdetec.config(bg=self.btn_color)
            self.btn_sdetec.config(bg="#00cc66")
        else:
            self.btn_cdetec.config(bg=self.btn_color)
            self.btn_sdetec.config(bg=self.btn_color)

    def on_close(self):
        self.camera.release()
        self.root.destroy()

    def video_loop(self):
        ret, frame = self.camera.read_frame()
        if ret:
            if self.detecting_mode == "color":
                frame = detect_colors(frame, self)
            elif self.detecting_mode == "strawberry":
                frame = detect_strawberries(frame, self)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)
        else:
            pil_img = Image.new("RGB", (self.width, self.height), self.bg_color)

        imgtk = ImageTk.PhotoImage(image=pil_img)
        self.lbl_video.imgtk = imgtk
        self.lbl_video.config(image=imgtk)

        self.root.after(15, self.video_loop)

    def run(self):
        self.root.mainloop()
