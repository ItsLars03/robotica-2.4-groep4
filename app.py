from joystick.joystick_manager import JoystickManager
from ui.remote_ui import RemoteUI
from camera.camera_handler import CameraHandler
from detection.color_detection import ColorDetector
from detection.strawberry_detection import StrawberryDetector

if __name__ == "__main__":
    # Initialize the camera handler with the desired resolution
    camera = CameraHandler(width=800, height=480)

    # Create detectors dict
    detectors = {
        "color": ColorDetector.detect_colors,
        "strawberry": StrawberryDetector.detect_strawberries
    }

    # Inject dependencies into UI (change width/height based on screen size)
    app = RemoteUI(
        width=800,
        height=480,
        camera_handler=camera,
        gripper_controller="",
        detectors=detectors
    )

    # Start the joystick manager so it starts listening for joystick input
    # Also starts the motor manager after initializing the joysticks to avoid problems
    joystickManager = JoystickManager()
    joystickManager.start()