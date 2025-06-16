from ax12 import Ax12

class Motor:
    def __init__(self, motor_id, controller: Ax12, name=""):
        self.id = motor_id
        self.ctrl = controller
        self.name = name or f"Motor-{motor_id}"

    def move(self, position, speed=512):
        #print(position)
        print(speed)
        self.ctrl.moveSpeed(self.id, 0, speed)
    
    def move_to(self, position):
        self.ctrl.move(self.id, position)

    def stop(self):
        self.ctrl.moveSpeed(self.id, 0, 0)

    def read_position(self):
        return self.ctrl.readPosition(self.id)
    
    def read_data(self):
        return self.ctrl.readData(self.id)

    def enable_torque(self, enable=True):
        return self.ctrl.setTorqueStatus(self.id, enable)

    def ping(self):
        return self.ctrl.ping(self.id)
    
    def limit(self):
        self.ctrl.setAngleLimit(self.id, 0, 1023)
    
    def set_wheel_mode(self):
        self.ctrl.setAngleLimit(self.id, 0, 0)

    def __repr__(self):
        return f"<{self.name} (ID: {self.id})>"

class RobotArm(Motor):
    def go_forward(self):
        self.move(1023, speed=300)

    def go_backward(self):
        self.move(0, speed=300)
