class Servo:
    def __init__(self, index):
        self.index = index
        self.angle = 0  # Initialize angle to 0

class ServoKit:
    def __init__(self, channels) -> None:
        self.channels = channels
        self._servo = [Servo(index) for index in range(channels)]

    @property
    def servo(self):
        return self._servo

    def __setattr__(self, name, value):
        if name == "angle":
            print(f"Servo rotates at {value}")
        object.__setattr__(self, name, value)
