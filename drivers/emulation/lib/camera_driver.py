
class Camera:
    def __init__(self) -> None:
        self.buffer = bytearray(10)

    def get_packet(self):
        return self.buffer

    def get_confirmation(self):
        return True
