# app.py

from controller.app_controller import AppController
from joystick.joystick_registry import JoystickRegistry
from motor.motor_registry import registry as motor_registry

if __name__ == "__main__":
    # Maak de Controller
    app = AppController(width=800, height=480)
    # Start de applicatie (video_loop + mainloop)
    app.start()
