# view/main_view.py

import tkinter as tk
from PIL import ImageTk

class MainView:
    """
    De View is verantwoordelijk voor:
     - Het aanmaken van het Tkinter-venster
     - Alle widgets (Label voor video, knoppen, etc.)
     - Styling en layout via .place(...)
     - Signaleren van button-clicks en keypresses naar de Controller.
    """

    def __init__(self, width=640, height=480):
        self.root = tk.Tk()
        self.root.title("MVC Camera App")
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False, False)

        # Label waarin de videofeed (of zwart vlak) getoond wordt
        self.lbl_video = tk.Label(self.root)
        self.lbl_video.place(x=0, y=0, relwidth=1, relheight=1)

        # “CAM”-knop (rechtsboven)
        self.btn_cam = tk.Button(
            self.root,
            text="CAM",
            bd=1, relief="ridge",
            font=("Helvetica", 12, "bold"),
            padx=8, pady=4
        )
        self.btn_cam.place(relx=0.98, rely=0.02, anchor="ne")

        # “MODE”-label en “AUTO/MANUAL”-knop (middenboven)
        self.lbl_mode = tk.Label(
            self.root,
            text="MODE",
            font=("Helvetica", 16, "bold"),
            fg="#555555", bg="#ffffff"
        )
        self.lbl_mode.place(relx=0.5, rely=0.15, anchor="center")

        self.btn_mode = tk.Button(
            self.root,
            text="AUTO / MANUAL",
            bd=2, relief="ridge",
            font=("Helvetica", 14, "bold"),
            padx=12, pady=6
        )
        self.btn_mode.place(relx=0.5, rely=0.25, anchor="center")

        # “GRIPPER”-label en “Close / Open”-knop (linksonder)
        self.lbl_gripper = tk.Label(
            self.root,
            text="GRIPPER",
            font=("Helvetica", 14, "bold"),
            fg="#555555", bg="#ffffff"
        )
        self.lbl_gripper.place(relx=0.02, rely=0.80, anchor="sw")

        self.btn_gripper = tk.Button(
            self.root,
            text="Close / Open",
            bd=2, relief="ridge",
            font=("Helvetica", 12),
            padx=10, pady=4
        )
        self.btn_gripper.place(relx=0.02, rely=0.88, anchor="sw")

        # “STOP”-knop (rechtsonder)
        self.btn_stop = tk.Button(
            self.root,
            text="STOP",
            bd=2, relief="ridge",
            font=("Helvetica", 12, "bold"),
            padx=10, pady=4
        )
        self.btn_stop.place(relx=0.98, rely=0.90, anchor="se")

    def set_video_frame(self, pil_image):
        """
        Wordt door de Controller aangeroepen.
        Ontvangt een PIL.Image, converteert naar PhotoImage en toont op lbl_video.
        """
        imgtk = ImageTk.PhotoImage(image=pil_image)
        # Houd referentie levend
        self.lbl_video.imgtk = imgtk
        self.lbl_video.config(image=imgtk)

    def bind_cam(self, callback):
        """Verbind het CAM-click event met de callback van de Controller."""
        self.btn_cam.config(command=callback)

    def bind_mode(self, callback):
        """Verbind AUTO/MANUAL met de callback."""
        self.btn_mode.config(command=callback)

    def bind_gripper(self, callback):
        self.btn_gripper.config(command=callback)

    def bind_stop(self, callback):
        self.btn_stop.config(command=callback)

    def mainloop(self):
        self.root.mainloop()

    def after(self, ms, func):
        """
        Een kleine wrapper zodat de Controller niet rechtstreeks
        aan tk.after hoeft te zitten, maar via de View loopt.
        """
        self.root.after(ms, func)
