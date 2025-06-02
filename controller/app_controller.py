# controller/app_controller.py

from model.camera_model import CameraModel
from view.main_view     import MainView

class AppController:
    """
    De Controller koppelt Model en View:
     - Leest periodiek een frame uit het Model (camera_model.get_frame())
     - Stuurt dat door naar de View (view.set_video_frame())
     - Behandelt button-clicks: roept camera_model.toggle_camera() aan, etc.
    """

    def __init__(self, width=640, height=480):
        # Maak Model en start camera alvast
        self.camera_model = CameraModel(width=width, height=height)
        self.camera_model.start_camera()

        # Maak View
        self.view = MainView(width=width, height=height)

        # Bind knoppen in de View aan Controller-methoden
        self.view.bind_cam(self.on_cam_click)
        self.view.bind_mode(self.on_mode_click)
        self.view.bind_gripper(self.on_gripper_click)
        self.view.bind_stop(self.on_stop_click)

    def start(self):
        """Start de periodieke update en de Tkinter mainloop."""
        # Zet de eerste video-update alvast in de wachtrij
        self.view.after(0, self.video_loop)
        # Start de GUI
        self.view.mainloop()
        # Als de GUI afgesloten wordt, clean up de camera
        self.camera_model.release()

    def video_loop(self):
        """
        Wordt telkens opnieuw opgeroepen via self.view.after().
        1) Vraag frame op bij het model
        2) Stuur dat door naar de View
        3) Plan opnieuw na 15 ms
        """
        pil_img = self.camera_model.get_frame()
        self.view.set_video_frame(pil_img)
        # Schedule opnieuw na ~15 ms (~60 fps)
        self.view.after(15, self.video_loop)

    # --- Callback methods voor knoppen ---

    def on_cam_click(self):
        """
        Toggles het model tussen cam-aan en cam-uit.
        De View krijgt na de toggle vanzelf een nieuw frame (zwart of live).
        Je kunt de View hier ook instrueren de CAM-knop visueel aan te passen.
        """
        self.camera_model.toggle_camera()

        # Optioneel: wijzig look van de CAM-knop om ON/OFF aan te geven
        if self.camera_model.camera_on:
            self.view.btn_cam.config(fg="#333333", bg="#ffffff")
        else:
            self.view.btn_cam.config(fg="#ff0000", bg="#000000")

    def on_mode_click(self):
        print("MODE-button ingedrukt! (controller)")
        # Hier kun je logica toevoegen voor “AUTO / MANUAL”

    def on_gripper_click(self):
        print("GRIPPER Close/Open ingedrukt! (controller)")
        # Voeg hier jouw grijper-logica toe

    def on_stop_click(self):
        print("STOP-button ingedrukt! (controller)")
        # Voeg hier stop-logica toe (bv. camera_model.stop_camera())

