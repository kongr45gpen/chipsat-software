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
        log_directory = "/sd/beacon_logs/"
        current_file = f"{log_directory}/beacon_log{int(currTime//TIMEINTERVAL)}.txt"

        try:
            beacon_packet = logs.beacon_packet(self)
            file = open(current_file, "ab+")
            file.write(bytearray(beacon_packet))
            file.close()
        except Exception:
            try:
                # This line to be removed when testing on hardware which already has the sd directory
                # leave this file in when testing on emulation
                # os.mkdir('/sd')

                os.mkdir(log_directory)
                # make sure to still log file when making the directory or else we lose the first beacon_packet of data
                beacon_packet = logs.beacon_packet(self)
                file = open(current_file, "ab+")
                file.write(bytearray(beacon_packet))
                file.close()
            except Exception as e:
                self.debug(e)
