from motor.motor_registry import registry

def do_something_with_arm():
    arm_motor = registry.get("arm_motor")
    if arm_motor:
        arm_motor.go_forward()