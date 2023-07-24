from lib.image_utils import flags
import time
import random

class Camera:
    def __init__(self) -> None:
        self.buffer = bytearray(10)
        self.firstPacket = True
        self.packets_sent = 0

    @property
    def get_packet(self):
        time.sleep(0.1)
        rand_num = random.random()
        if rand_num < 0.05:
            return None, flags.FAIL_NO_PACKET
        self.packets_sent += 1
        if self.firstPacket:
            return self.buffer, flags.SUCCESS_FIRST_PACKET
        if self.packets_sent > 50:
            return self.buffer, flags.SUCCESS_END_PACKET
        return self.buffer, flags.SUCCESS_MID_PACKET

    def get_confirmation(self):
        time.sleep(2)
        return True
