class Joystick:
    def __init__(self, name):
        self.name = name
        self.x = 0
        self.y = 0
        self.pressed = 0

    def update(self, x, y, pressed):
        self.x = x
        self.y = y
        self.pressed = pressed

    def __repr__(self):
        return f"<{self.name}: x={self.x}, y={self.y}, pressed={self.pressed}>"