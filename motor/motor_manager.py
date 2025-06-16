import time
from ax12 import Ax12
from motor.motor import Motor
from joystick.registry import registry as joystick_registry

IDLE_MIN = 2200
IDLE_MAX = 2400
JOYSTICK_MIN = 0
JOYSTICK_MAX = 4090
MAX_SPEED_REGULAR = 700
MAX_SPEED_GRIPPER = 150
CENTER = (IDLE_MIN + IDLE_MAX) // 2
TORQUE_THRESHOLD = 1300

class MotorManager:
    def __init__(self):
        self.ax = Ax12()
        self.motors = {}
        self.motor_states = {}
        self.gripper_state = False
        self.joystick_pressed_state = False
        self.prev_j1_pressed = 0
        self._initialize_motors()
        self._get_joysticks()

    def _initialize_motors(self):
        # Search for the ID's of the motors used in the project (2 to 7)
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
        self.motor_states[name] = {"stopped": False, "last_speed": None}

    def _get_joysticks(self):
        self.j1 = joystick_registry.get("J2")
        self.j2 = joystick_registry.get("J1")

    def _map_joystick_to_speed(self, value):
        if IDLE_MIN <= value <= IDLE_MAX:
            return 0
        delta = value - CENTER
        normalized = delta / (JOYSTICK_MAX - CENTER) if delta > 0 else delta / (CENTER - JOYSTICK_MIN)
        return int(max(-1, min(1, normalized)) * MAX_SPEED_REGULAR)

    def _drive_motor(self, motor_name, axis_value):
        motor = self.motors.get(motor_name)
        if not motor:
            return
        speed = self._map_joystick_to_speed(axis_value)
        state = self.motor_states[motor_name]

        if speed == 0:
            if not state["stopped"]:
                motor.stop()
                state["stopped"] = True
                state["last_speed"] = 0
            return

        if speed != state["last_speed"]:
            motor.move(motor.id, speed if speed > 0 else abs(speed) + 1024)
            state["last_speed"] = speed
            state["stopped"] = False

    def update_from_joysticks(self):
        if not self.j1 or not self.j2:
            return

        if self.j1.pressed == 1 and self.prev_j1_pressed == 0:
            self.joystick_pressed_state = not self.joystick_pressed_state
        self.prev_j1_pressed = self.j1.pressed

        self._drive_motor("up_down_motor_1", self.j1.x)
        self._drive_motor("up_down_motor_2", self.j1.x)
        self._drive_motor("arm_in_out_motor", self.j2.x)

        if self.joystick_pressed_state:
            self._drive_motor("gripper_move_motor", self.j2.y)
        else:
            self._drive_motor("turn_base_motor", self.j2.y)

    def toggle_gripper(self):
        motor = self.motors.get("gripper_motor")
        if not motor:
            return

        motor.enable_torque()

        if not self.gripper_state:
            motor.move(motor.id, MAX_SPEED_GRIPPER)
            self._wait_until_torque_limit(motor)
        else:
            motor.move(motor.id, 1024 + MAX_SPEED_GRIPPER)
            time.sleep(2.0)
            motor.stop()

        self.gripper_state = not self.gripper_state

    def _wait_until_torque_limit(self, motor):
        load_buffer = []
        start_time = time.time()
        while True:
            load = abs(motor.ctrl.readLoad(motor.id))
            load_buffer.append(load)
            if len(load_buffer) > 5:
                load_buffer.pop(0)

            avg_load = sum(load_buffer) / len(load_buffer)

            if time.time() - start_time > 0.2 and avg_load > TORQUE_THRESHOLD:
                motor.stop()
                break

            if time.time() - start_time > 2.0:
                motor.stop()
                break

            time.sleep(0.01)

toggle_gripper = MotorManager.toggle_gripper