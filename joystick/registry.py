from .joystick import Joystick

class JoystickRegistry:
    def __init__(self):
        self.joysticks = {
            "J1": Joystick("J1"),
            "J2": Joystick("J2")
        }

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
                    i += 3  # move past x, y, pressed
                except Exception as e:
                    print(f"Invalid joystick data at index {i}: {parts[i]} - {e}")
                    i += 1
            else:
                i += 1  # skip non-joystick data

    def get(self, name):
        return self.joysticks.get(name)

# Singleton instance
registry = JoystickRegistry()
