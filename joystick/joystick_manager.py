import serial
import threading
import time
from joystick.registry import registry
from motor.motor_manager import MotorManager

class JoystickManager:
    def __init__(self, port='/dev/ttyAMA2', baudrate=115200):
        self.motorManager = MotorManager()
        self.serial = serial.Serial(port, baudrate, timeout=1)
        self.running = False
        self.thread = None

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._poll_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def _poll_loop(self):
        while self.running:
            time.sleep(0.1)
            line = self.serial.readline().decode("utf-8")
            registry.update_from_serial(line)
            self.motorManager.update_from_joysticks()