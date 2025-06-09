import threading
import serial
from motor.motor_controller import MotorController
from .joystick import Joystick

# Serial port of the joysticks
SERIAL_PORT = '/dev/ttyAMA2'
# Baud rate getting serial data
BAUD_RATE = 115200

class JoystickRegistry:
    def __init__(self):
        self.joysticks = {
            "J1": Joystick("J1"),
            "J2": Joystick("J2")
        }
        self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        self.running = True

        # Start the polling thread
        threading.Thread(target=self._poll_serial, daemon=True).start()

    def _poll_serial(self):
        while self.running:
            try:
                line = self.ser.readline().decode("utf-8").strip()
                if line:
                    self.update_from_serial(line)
                    MotorController.update_motors_from_joysticks()
                    print(f"J1: {self.joysticks['J1']}, J2: {self.joysticks['J2']}")
            except Exception as e:
                print(f"Joystick Serial read failed: {e}")

    def update_from_serial(self, line: str):
        parts = line.strip().split(",")
        i = 0
        while i < len(parts):
            if parts[i].startswith("J"):
                try:
                    label, x = parts[i].split(":")
                    y = int(parts[i + 1])
                    pressed = int(parts[i + 2])
                    x = int(x)
                    if label in self.joysticks:
                        self.joysticks[label].update(x, y, pressed)
                    i += 3
                except Exception as e:
                    print(f"Invalid joystick data at index {i}: {parts[i]} - {e}")
                    i += 1
            else:
                i += 1

    def get(self, name):
        return self.joysticks.get(name)

    def map_joystick1_to_speed(self, x):
        IDLE_MIN = 2100
        IDLE_MAX = 2400
        JOYSTICK_MIN = 0
        JOYSTICK_MAX = 4000
        MAX_SPEED = 1023
        CENTER = (IDLE_MIN + IDLE_MAX) // 2

        if IDLE_MIN <= x <= IDLE_MAX:
            return 0
        delta = x - CENTER
        if delta > 0:
            normalized = delta / (JOYSTICK_MAX - CENTER)
        else:
            normalized = delta / (CENTER - JOYSTICK_MIN)
        return int(max(-1, min(1, normalized)) * MAX_SPEED)

    def map_joystick2_to_speed(self, x):
        IDLE_MIN = 2100
        IDLE_MAX = 2400
        JOYSTICK_MIN = 0
        JOYSTICK_MAX = 4000
        MAX_SPEED = 1023
        CENTER = (IDLE_MIN + IDLE_MAX) // 2

        if IDLE_MIN <= x <= IDLE_MAX:
            return 0
        delta = x - CENTER
        if delta > 0:
            normalized = delta / (JOYSTICK_MAX - CENTER)
        else:
            normalized = delta / (CENTER - JOYSTICK_MIN)
        return int(max(-1, min(1, normalized)) * MAX_SPEED)

registry = JoystickRegistry()
