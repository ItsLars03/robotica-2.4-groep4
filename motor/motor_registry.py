from ax12 import Ax12
from motor.motor import Motor

class MotorRegistry:
    # A registry for managing motors
    def __init__(self):
        self.ax = Ax12()
        self.motors = {}
        self._initialize_motors()

    # Initialize motors by searching for their IDs and registering them
    def _initialize_motors(self):
        found_ids = self.ax.learnServos(2, 7, verbose=True)
        for i in found_ids:
            print(f"Found motor with ID: {i}")
            match i:
                case 5:
                    self._register("gripper_motor", i)
                case 3:
                    self._register("gripper_move_motor", i)
                case 6:
                    self._register("arm_in_out_motor", i)
                case 7:
                    self._register("turn_base_motor", i)
                case 2:
                    self._register("up_down_motor_1", i)
                case 4:
                    self._register("up_down_motor_2", i)

    def _register(self, name, motor_id):
        motor = Motor(motor_id, self.ax, name)
        motor.set_wheel_mode()
        self.motors[name] = motor

    def get(self, name):
        return self.motors.get(name)

    def motor_names(self):
        return list(self.motors.keys())
