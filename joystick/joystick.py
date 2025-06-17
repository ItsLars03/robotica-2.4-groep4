# Joystick class for handling joystick input
class Joystick:
    # Joystick data and state
    def __init__(self, name):
        self.name = name
        self.x = 0
        self.y = 0
        self.pressed = 0

    # Update joystick state with new x, y coordinates and pressed state
    def update(self, x, y, pressed):
        self.x = x
        self.y = y
        self.pressed = pressed

    # Get the current state of the joystick
    def __repr__(self):
        return f"<{self.name}: x={self.x}, y={self.y}, pressed={self.pressed}>"