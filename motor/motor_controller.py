from motor.motor_registry import registry as motor_registry
from joystick.joystick_registry import registry as joystick_registry
class MotorController:
    def __init__(self):
        self.toggle_state = False
        self.prev_j2_pressed = 0

    def update_motors_from_joysticks(self):
        j1 = joystick_registry.get("J1")
        j2 = joystick_registry.get("J2")

        if not j1 or not j2:
            return

        # Get motors
        motors = {
            "turn_base": motor_registry.get("turn_base_motor"),
            "up_down_1": motor_registry.get("up_down_motor_1"),
            "up_down_2": motor_registry.get("up_down_motor_2"),
            "gripper_move": motor_registry.get("gripper_move_motor"),
            "arm_in_out": motor_registry.get("arm_in_out_motor")
        }

        # Toggle control mode if J2 pressed changed from 0 to 1
        if j2.pressed == 1 and self.prev_j2_pressed == 0:
            self.toggle_state = not self.toggle_state
        self.prev_j2_pressed = j2.pressed

        # J2.x: either turn base OR up/down motors depending on toggle state
        if self.toggle_state:
            self._drive_motor(motors["up_down_1"], j2.x, "joystick2")
            self._drive_motor(motors["up_down_2"], j2.x, "joystick2")
        else:
            self._drive_motor(motors["turn_base"], j2.x, "joystick2")

        # J2.y → gripper_move_motor
        self._drive_motor(motors["gripper_move"], j2.y, "joystick2")

        # J1.x → arm_in_out_motor
        self._drive_motor(motors["arm_in_out"], j1.x, "joystick1")

    def _drive_motor(self, motor, axis_value, joystick: str):
        if not motor:
            return

        map_func = (
            joystick_registry.map_joystick1_to_speed
            if joystick == "joystick1"
            else joystick_registry.map_joystick2_to_speed
        )

        speed = map_func(axis_value)
        if speed == 0:
            motor.stop()
        else:
            position = 1023 if speed > 0 else 0
            motor.move(position=position, speed=abs(speed))

MotorController = MotorController()