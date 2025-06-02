# app.py

from controller.app_controller import AppController

if __name__ == "__main__":
    # Maak de Controller
    app = AppController(width=640, height=480)
    # Start de applicatie (video_loop + mainloop)
    app.start()
