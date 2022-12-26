# Transmit "Hello World" beacon

from Tasks.log import LogTask as Task
from pycubed import cubesat
import files
import time
import logs

class task(Task):
    name = 'beacon'
    color = 'teal'

    async def main_task(self):
        """
        Pushes a beacon packet onto the transmission queue.
        """
        if not cubesat.sdcard:
            return

        try:
            self.write_beacon()
        except Exception:
            files.mkdirp('/sd/logs/beacon/')
            self.write_beacon()

    def write_beacon(self):
        currTime = time.time()
        TIMEINTERVAL = 1000
        log_directory = "/sd/logs/"
        current_file = f"{log_directory}beacon/{int(currTime//TIMEINTERVAL)}.txt"
        beacon_packet = logs.beacon_packet()
        file = open(current_file, "ab+")
        file.write(bytearray(beacon_packet))
        file.close()
