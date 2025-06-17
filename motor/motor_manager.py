import time
from joystick.joystick_registry import registry as joystick_registry
from motor.motor_registry import MotorRegistry

# Joystick idle minimum value of the joystick (not moving)
IDLE_MIN = 2200
# Joystick idle maximum value of the joystick (not moving)
IDLE_MAX = 2400
# Joystick minimal value
JOYSTICK_MIN = 0
# Joystick maximum value
JOYSTICK_MAX = 4090
# A set max speed for the motors
MAX_SPEED_REGULAR = 700
# A set max speed for the gripper motor
MAX_SPEED_GRIPPER = 150
# The center value of the joystick, used to determine if the joystick is idle
CENTER = (IDLE_MIN + IDLE_MAX) // 2
# Torque threshold for the gripper motor to determine if the gripper is as closed as possible
TORQUE_THRESHOLD = 1300

# MotorManager class for managing the motors
class MotorManager:
    # Initializes the MotorManager with a registry of motors and joystick states
    def __init__(self):
        self.registry = MotorRegistry()
        self.motor_states = {name: {"stopped": False, "last_speed": None} for name in self.registry.motor_names()}
        self.gripper_state = False
        self.joystick_pressed_state = False
        self.prev_j1_pressed = 0
        self._get_joysticks()

    # gets the joysticks from the joystick registry
    def _get_joysticks(self):
        self.j1 = joystick_registry.get("J2")
        self.j2 = joystick_registry.get("J1")

    # Maps joystick axis value to motor speed
    def _map_joystick_to_speed(self, value):
        # if the joystick value is within the idle range, return 0 speed
        if IDLE_MIN <= value <= IDLE_MAX:
            return 0
        # Normalize the joystick value to a speed value
        delta = value - CENTER
        # if the delta is positive, normalize it by the maximum range above center, otherwise normalize it by the maximum range below center
        normalized = delta / (JOYSTICK_MAX - CENTER) if delta > 0 else delta / (CENTER - JOYSTICK_MIN)
        # Scale the normalized value to the maximum speed
        return int(max(-1, min(1, normalized)) * MAX_SPEED_REGULAR)

    # Drives a motor based on the joystick axis value
    def _drive_motor(self, motor_name, axis_value):
        # get the motor from the registry
        motor = self.registry.get(motor_name)
        if not motor:
            return

        # Map the joystick axis value to a speed
        speed = self._map_joystick_to_speed(axis_value)
        # Get the current state of the motor for stopping logic
        state = self.motor_states[motor_name]

        # If the speed is 0, stop the motor if it was previously moving
        if speed == 0:
            if not state["stopped"]:
                motor.stop()
                state["stopped"] = True
                state["last_speed"] = 0
            return

        # If the speed is different from the last speed, move the motor
        if speed != state["last_speed"]:
            motor.move(motor.id, speed if speed > 0 else abs(speed) + 1024)
            # Update the state to reflect the motor is now moving
            state["last_speed"] = speed
            state["stopped"] = False

    # Updates the motor states based on joystick inputs
    def update_from_joysticks(self):
        # Ensure both joysticks are available
        if not self.j1 or not self.j2:
            return

        # Toggle the joystick pressed state if the button is pressed
        if self.j1.pressed == 1 and self.prev_j1_pressed == 0:
            self.joystick_pressed_state = not self.joystick_pressed_state
        self.prev_j1_pressed = self.j1.pressed

        # Drive the motors based on joystick inputs
        self._drive_motor("up_down_motor_1", self.j1.x)
        self._drive_motor("up_down_motor_2", self.j1.x)
        self._drive_motor("arm_in_out_motor", self.j2.x)

        # Depending on the joystick pressed state, drive different motors
        if self.joystick_pressed_state:
            self._drive_motor("gripper_move_motor", self.j2.y)
        else:
            self._drive_motor("turn_base_motor", self.j2.y)

    # Toggles the gripper state by moving the gripper motor
    def toggle_gripper(self):
        # Get the gripper motor from the registry
        motor = self.registry.get("gripper_motor")
        if not motor:
            return

        # Enable the motor torque before moving
        motor.enable_torque()

        # If the gripper is not engaged, move it to close, otherwise move it to open
        if not self.gripper_state:
            motor.move(motor.id, MAX_SPEED_GRIPPER)
            # Wait until the torque limit is reached or timeout occurs
            self._wait_until_torque_limit(motor)
        else:
            motor.move(motor.id, 1024 + MAX_SPEED_GRIPPER)
            time.sleep(2.0)
            motor.stop()

        # Toggle the gripper state
        self.gripper_state = not self.gripper_state

    # Waits until the torque limit is reached or a timeout occurs
    def _wait_until_torque_limit(self, motor):
        # Initialize a buffer to store load values
        load_buffer = []
        # Start a timer to limit the waiting time
        start_time = time.time()
        # Continuously read the load from the motor until the torque limit is reached or timeout occurs
        while True:
            # Read the load from the motor and append it to the buffer
            load = abs(motor.ctrl.readLoad(motor.id))
            load_buffer.append(load)
            # If the buffer exceeds 5 values, remove the oldest one
            if len(load_buffer) > 5:
                load_buffer.pop(0)

            # Calculate the average load from the buffer
            avg_load = sum(load_buffer) / len(load_buffer)

            # If the average load exceeds the torque threshold and enough time has passed, stop the motor
            if time.time() - start_time > 0.2 and avg_load > TORQUE_THRESHOLD:
                motor.stop()
                break

            # If the elapsed time exceeds 2 seconds, stop the motor and exit the loop
            if time.time() - start_time > 2.0:
                motor.stop()
                break

            # Small delay to allow the motors to respond smoothly
            time.sleep(0.01)