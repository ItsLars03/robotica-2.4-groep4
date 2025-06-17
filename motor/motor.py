from ax12 import Ax12

# Motor class for controlling the motors using the Ax12 library
class Motor:
    # Initialize the motor with its ID, controller, and name
    def __init__(self, motor_id, controller: Ax12, name=""):
        self.id = motor_id
        # Assign the controller instance to the motor
        self.ctrl = controller
        self.name = name or f"Motor-{motor_id}"

    # Move the motor with speed control
    def move(self, position, speed=512):
        self.ctrl.moveSpeed(self.id, 0, speed)
    # move to a specific position
    def move_to(self, position):
        self.ctrl.move(self.id, position)
    # Stop the motor
    def stop(self):
        self.ctrl.moveSpeed(self.id, 0, 0)
    # Read the current position of the motor
    def read_position(self):
        return self.ctrl.readPosition(self.id)
    # Read the current data from the motor
    def read_data(self):
        return self.ctrl.readData(self.id)
    # Enable or disable the torque of the motor
    def enable_torque(self, enable=True):
        return self.ctrl.setTorqueStatus(self.id, enable)
    # Read the current load of the motor
    def ping(self):
        return self.ctrl.ping(self.id)
    # Set the angle limit for the motor
    def limit(self):
        self.ctrl.setAngleLimit(self.id, 0, 1023)
    # Set the motor to wheel mode, which disables angle limits
    def set_wheel_mode(self):
        self.ctrl.setAngleLimit(self.id, 0, 0)

    def __repr__(self):
        return f"<{self.name} (ID: {self.id})>"
