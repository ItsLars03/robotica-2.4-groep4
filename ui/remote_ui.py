import tkinter as tk
import cv2
from PIL import Image, ImageTk

class RemoteUI:
    def __init__(self, width, height, camera_handler, gripper_controller, detectors=None):
        self.width = width
        self.height = height
        self.camera = camera_handler
        self.gripper_controller = gripper_controller
        self.detectors = detectors or {}

        self.detecting_mode = None

        self.bg_color = "#0f1c3f"
        self.btn_color = "#1e3f66"
        self.btn_active = "#3399ff"
        self.btn_fg = "#ffffff"
        self.btn_font = ("Helvetica", 12, "bold")

        self.root = tk.Tk()
        self.root.title("Remote UI")
        self.root.geometry(f"{width}x{height}")
        self.root.configure(bg=self.bg_color)
        self.root.resizable(False, False)

        self.lbl_video = tk.Label(self.root, bg=self.bg_color)
        self.lbl_video.place(x=0, y=0, relwidth=1, relheight=1)

        # Buttons
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
        is_on = self.camera.toggle_camera()
        self.btn_cam.config(bg=self.btn_active if is_on else "#000000", fg="#ffffff" if is_on else "#ff4444")

    def on_mode_click(self):
        print("MODE button clicked.")

    def on_gripper_click(self):
        self.gripper_controller()

    def on_stop_click(self):
        print("STOP button clicked.")
        self.camera.toggle_camera()
        self.btn_cam.config(bg="#000000", fg="#ff4444")

    def color_detect_click(self):
        self.detecting_mode = "color" if self.detecting_mode != "color" else None
        self.update_detection_buttons()

    def strawberry_detect_click(self):
        self.detecting_mode = "strawberry" if self.detecting_mode != "strawberry" else None
        self.update_detection_buttons()

    def update_detection_buttons(self):
        self.btn_cdetec.config(bg="#00cc66" if self.detecting_mode == "color" else self.btn_color)
        self.btn_sdetec.config(bg="#00cc66" if self.detecting_mode == "strawberry" else self.btn_color)

    def on_close(self):
        self.camera.release()
        self.root.destroy()

    def video_loop(self):
        ret, frame = self.camera.read_frame()
        if ret:
            if self.detecting_mode and self.detecting_mode in self.detectors:
                frame = self.detectors[self.detecting_mode](frame, self)
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
