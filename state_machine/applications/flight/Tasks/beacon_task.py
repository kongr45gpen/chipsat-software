# Transmit "Hello World" beacon

from lib.template_task import Task
import time
import os
import logs

class task(Task):
    name = 'beacon'
    color = 'teal'

    async def main_task(self):
        """
        Pushes a beacon packet onto the transmission queue.
        """
        currTime = time.time()
        TIMEINTERVAL = 1000
        log_directory = "/sd/logs/"
        current_file = f"{log_directory}/beacon_log{int(currTime//TIMEINTERVAL)}.txt"

        try:
            beacon_packet = logs.beacon_packet(self)
            file = open(current_file, "ab+")
            file.write(bytearray(beacon_packet))
            file.close()
        except Exception:
            try:
                # uncomment the following line when building for emulator
                # os.mkdir('/sd')

                os.mkdir(log_directory)
                # make sure to still log file when making the directory or else we lose the first beacon_packet of data
                beacon_packet = logs.beacon_packet(self)
                file = open(current_file, "ab+")
                file.write(bytearray(beacon_packet))
                file.close()
            except Exception as e:
                self.debug(e)
