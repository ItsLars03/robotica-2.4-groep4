from .joystick import Joystick

# JoystickRegistry class for managing the joysticks
class JoystickRegistry:
    def __init__(self):
        self.joysticks = {
            "J1": Joystick("J1"),
            "J2": Joystick("J2")
        }

    # Update joysticks from serial input
    def update_from_serial(self, line: str):
        # Parsing string format to extract joystick data to usable format (e.g., "J1:100,200,1,J2:150,250,0")
        parts = line.strip().split(",")
        i = 0
        # Iterate through parts
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

    # Get a joystick by name
    def get(self, name):
        return self.joysticks.get(name)

# Singleton instance
registry = JoystickRegistry()
