import tkinter as tk
import cv2
from PIL import Image, ImageTk

from motor.motor_manager import MotorManager


class RemoteUI:
    """
    Een afstandsbediening-UI voor het weergeven van camerabeelden
    en het activeren van acties zoals gripper-besturing en detectie.
    """
    def __init__(self, width, height, camera_handler, gripper_controller= "", detectors=None):
        # Sla afmetingen en handlers op
        self.width = width
        self.height = height
        self.camera = camera_handler
        self.gripper_controller = MotorManager.toggle_gripper()
        # Optionele dict met detectiefuncties per modus
        self.detectors = detectors or {}

        # Huidige detectiemodus (bijv. 'color', 'strawberry')
        self.detecting_mode = None

        # UI-kleuren en lettertype instellen
        self.bg_color = "#0f1c3f"
        self.btn_color = "#1e3f66"
        self.btn_active = "#3399ff"
        self.btn_fg = "#ffffff"
        self.btn_font = ("Helvetica", 12, "bold")

        # Hoofdvenster initialiseren
        self.root = tk.Tk()
        self.root.title("Remote UI")
        self.root.geometry(f"{width}x{height}")  # Venstergrootte instellen
        self.root.configure(bg=self.bg_color)
        self.root.resizable(False, False)  # Niet her-schaalbaar maken

        # Label voor videoweergave
        self.lbl_video = tk.Label(self.root, bg=self.bg_color)
        self.lbl_video.place(x=0, y=0, relwidth=1, relheight=1)

        # Knoppen aanmaken en positioneren
        self.btn_cam = self._styled_button("CAM", self.toggle_camera)
        self.btn_cam.place(relx=0.945, rely=0.06, anchor="center")

        self.btn_mode = self._styled_button("AUTO / MANUAL", self.on_mode_click)
        self.btn_mode.place(relx=0.11, rely=0.06, anchor="center")

        self.btn_gripper = self._styled_button("GRIPPER", self.on_gripper_click)
        self.btn_gripper.place(relx=0.079, rely=0.17, anchor="center")

        self.btn_stop = self._styled_button("STOP", self.on_stop_click)
        self.btn_stop.place(relx=0.942, rely=0.935, anchor="center")

        self.btn_cdetec = self._styled_button("Kleur Detectie", self.color_detect_click)
        self.btn_cdetec.place(relx=0.892, rely=0.17, anchor="center")

        self.btn_sdetec = self._styled_button("Aardbei Detectie", self.strawberry_detect_click)
        self.btn_sdetec.place(relx=0.868, rely=0.29, anchor="center")

        # Start videoloop en sluitprotocol
        self.root.after(0, self.video_loop)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _styled_button(self, text, command):
        """
        Helper voor een gestileerde knop met uniforme opmaak.
        """
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
        """
        Zet de camera aan/uit en pas de CAM-knopkleur aan.
        """
        is_on = self.camera.toggle_camera()
        # Blauw bij aan, zwart met rode tekst bij uit
        self.btn_cam.config(
            bg=self.btn_active if is_on else "#000000",
            fg="#ffffff" if is_on else "#ff4444"
        )

    def on_mode_click(self):
        """
        Callback voor de AUTO/MANUAL-knop. Uit te breiden door gebruiker.
        """
        print("MODE-knop geklikt.")

    def on_gripper_click(self):
        """
        Activeer de gripper-controller.
        """
        self.gripper_controller()

    def on_stop_click(self):
        """
        Stoppen: camera uitzetten en knopkleur bijwerken.
        """
        print("STOP-knop geklikt.")
        self.camera.toggle_camera()
        self.btn_cam.config(bg="#000000", fg="#ff4444")

    def color_detect_click(self):
        """
        Zet kleuren-detectiemodus aan/uit.
        """
        # Wissel tussen 'color' en None
        self.detecting_mode = "color" if self.detecting_mode != "color" else None
        self.update_detection_buttons()

    def strawberry_detect_click(self):
        """
        Zet aardbei-detectiemodus aan/uit.
        """
        # Wissel tussen 'strawberry' en None
        self.detecting_mode = "strawberry" if self.detecting_mode != "strawberry" else None
        self.update_detection_buttons()

    def update_detection_buttons(self):
        """
        Werk de weergave van detectieknoppen bij op basis van de huidige modus.
        """
        # Actieve knop in groen, anders standaardkleur
        self.btn_cdetec.config(
            bg="#00cc66" if self.detecting_mode == "color" else self.btn_color
        )
        self.btn_sdetec.config(
            bg="#00cc66" if self.detecting_mode == "strawberry" else self.btn_color
        )

    def on_close(self):
        """
        Ruim camera-hulpbron op en sluit het venster.
        """
        self.camera.release()
        self.root.destroy()

    def video_loop(self):
        """
        Lees frames van de camera, pas detectie toe en werk de UI bij.
        """
        ret, frame = self.camera.read_frame()
        if ret:
            # Pas de geselecteerde detector toe als die bestaat
            if self.detecting_mode and self.detecting_mode in self.detectors:
                frame = self.detectors[self.detecting_mode](frame, self)
            # Converteer BGR naar RGB voor PIL
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)
        else:
            # Toon achtergrondkleur als geen frame beschikbaar
            pil_img = Image.new("RGB", (self.width, self.height), self.bg_color)

        # Zet om naar ImageTk voor Label-weergave
        imgtk = ImageTk.PhotoImage(image=pil_img)
        self.lbl_video.imgtk = imgtk  # Voorkom garbage collection
        self.lbl_video.config(image=imgtk)

        # Plan volgende update
        self.root.after(15, self.video_loop)

    def run(self):
        """
        Start de tkinter hoofdloop.
        """
        self.root.mainloop()
