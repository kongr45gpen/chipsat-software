from lib.image_utils import flags
import time
import random
import os

class Camera:
    def __init__(self) -> None:
        self.buffer = bytearray(16)
        self.firstPacket = True
        self.packet_num = 0
        try:
            os.mkdir("sd/images")
        except Exception:
            pass

    @property
    def get_packet(self):
        time.sleep(0.05)
        rand_num = random.random()
        self.buffer[0] = self.packet_num
        if rand_num < 0.05:
            return None, flags.FAIL_NO_PACKET
        if self.packet_num == 0:
            return self.buffer, flags.SUCCESS_FIRST_PACKET
        if self.packet_num >= 100:
            self.packet_num = 0
            return self.buffer, flags.SUCCESS_END_PACKET
        return self.buffer, flags.SUCCESS_MID_PACKET

    def get_confirmation(self):
        time.sleep(2)
        return True

    @property
    def ack(self):
        self.packet_num += 1
