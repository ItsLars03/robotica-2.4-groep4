from ax12 import Ax12
from motor.motor_registry import MotorRegistry


# from .base import Motor, RobotArm

class JoystickRegistry:
    def __init__(self):
        self.ax = Ax12()
        self.joysticks = {}
        self._initialize_joysticks()

    def _initialize_motors(self):
        found_ids = self.ax.learnServos(1, 7, verbose=True)
        # set motor to the registry based on their id and function in the robot
        # for i in found_ids:
        #     print(f"Found motor with ID: {i}")
        #     match i:
        #         case 5:
        #             self.motors["gripper_motor"] = Motor(i, self.ax, "gripper_motor")
        #         case 3:
        #             self.motors["gripper_move_motor"] = Motor(i, self.ax, "gripper_move_motor")
        #         case 6:
        #             self.motors["arm_in_out_motor"] = Motor(i, self.ax, "arm_in_out_motor")
        #         case 7:
        #             self.motors["turn_base_motor"] = Motor(i, self.ax, "turn_base_motor")
        #         case 2:
        #             self.motors["up_down_motor_1"] = Motor(i, self.ax, "up_down_motor_1")
        #         case 4:
        #             self.motors["up_down_motor_2"] = Motor(i, self.ax, "up_down_motor_2")

    def get(self, name):
        return self.motors.get(name)

# Global instance (singleton-style)
registry = MotorRegistry()
