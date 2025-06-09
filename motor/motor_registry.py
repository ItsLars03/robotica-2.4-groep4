from motor.ax12 import Ax12
from .motor import Motor

class MotorRegistry:
    def __init__(self):
        self.ax = Ax12()
        self.motors = {}
        self._initialize_motors()

    def _initialize_motors(self):
        # List all required motor IDs and check if they are present
        req_motor_ids = [2, 3, 4, 5, 6, 7]
        found_ids = self.ax.learnServos(1, 7, verbose=True)

        missing = req_motor_ids - found_ids
        if missing:
            raise RuntimeError(f"Missing motors with IDs: {sorted(missing)}.")

        # set motor to the registry based on their id and function in the robot
        for i in found_ids:
            print(f"Found motor with ID: {i}")
            match i:
                case 5:
                    motor = self.motors["gripper_motor"] = Motor(i, self.ax, "gripper_motor")
                    motor.limit()
                case 3:
                    motor = self.motors["gripper_move_motor"] = Motor(i, self.ax, "gripper_move_motor")
                    motor.limit()
                case 6:
                    motor = self.motors["arm_in_out_motor"] = Motor(i, self.ax, "arm_in_out_motor")
                    motor.limit()
                case 7:
                    motor = self.motors["turn_base_motor"] = Motor(i, self.ax, "turn_base_motor")
                    motor.limit()
                case 2:
                    motor = self.motors["up_down_motor_1"] = Motor(i, self.ax, "up_down_motor_1")
                    motor.limit()
                case 4:
                    motor = self.motors["up_down_motor_2"] = Motor(i, self.ax, "up_down_motor_2")
                    motor.limit()

    def get(self, name):
        return self.motors.get(name)

# Global instance (singleton-style)
registry = MotorRegistry()
