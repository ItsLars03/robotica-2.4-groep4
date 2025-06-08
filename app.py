# app.py

from controller.app_controller import AppController
from motor.motor_registry import registry

if __name__ == "__main__":
    # Maak de Controller
    app = AppController(width=800, height=480)
    # Start de applicatie (video_loop + mainloop)
    app.start()

    # arm_motor = registry.get("gripper_motor")
    #
    # if arm_motor:
    #     print(f"Using {arm_motor}")
    #     arm_motor.go_backward()
