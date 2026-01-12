import time

import serial


class Serial:
    def __init__(self):
        self.serial = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
        time.sleep(2)

    def move(self, x_angle: int, y_angle: int) -> None:
        self.serial.write(f"{x_angle} {y_angle}\n\n".encode())
