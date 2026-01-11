from gpiozero import AngularServo


class Servo:
    def __init__(self, pin: int):
        self.servo = AngularServo(pin, min_pulse_width=0.0006, max_pulse_width=0.0023, initial_angle=90)

    def set_angle(self, angle: int) -> None:
        self.servo.angle = angle

    def current_angle(self):
        return self.servo.angle
