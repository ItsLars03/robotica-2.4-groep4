from motor.motor_registry import registry as motor_registry
from joysticks.registry import registry as joystick_registry

# Constants
IDLE_MIN = 2100
IDLE_MAX = 2400
JOYSTICK_MIN = 0
JOYSTICK_MAX = 4000
MAX_SPEED = 1023
CENTER = (IDLE_MIN + IDLE_MAX) // 2

def map_joystick_to_speed(value):
    if IDLE_MIN <= value <= IDLE_MAX:
        return 0  # in dead zone
    delta = value - CENTER
    normalized = delta / (JOYSTICK_MAX - CENTER) if delta > 0 else delta / (CENTER - JOYSTICK_MIN)
    return int(max(-1, min(1, normalized)) * MAX_SPEED)

def update_motor_from_joystick():
    j2 = joystick_registry.get("J2")
    turn_base_motor = motor_registry.get("turn_base_motor")
    if j2 and turn_base_motor:
        speed = map_joystick_to_speed(j2.x)
        if speed == 0:
            turn_base_motor.stop()
        else:
            # Choose a dummy position far enough so it keeps turning
            target_position = 1023 if speed > 0 else 0
            turn_base_motor.move(position=target_position, speed=abs(speed))
