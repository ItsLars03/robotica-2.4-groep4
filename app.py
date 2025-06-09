
# app.py
from ui.remote_ui import RemoteUI
from joystick.joystick_registry import JoystickRegistry
from motor.motor_registry import registry as motor_registry

if __name__ == "__main__":
    # Pas hier de grootte eventueel aan
    app = RemoteUI(width=800, height=480)
    app.run()
