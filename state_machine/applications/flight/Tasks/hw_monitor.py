from Tasks.log import LogTask as Task
from pycubed import cubesat
from lib.alerts import alerts

class task(Task):
    name = 'hw_monitor'
    color = 'orange'
    data_file = None

    async def main_task(self):
        """
        Prints the IMU data to the console.
        """
        alerts.set_value(self.debug, 'imu_available', cubesat.imu is not None)
        alerts.set_value(self.debug, 'radio_available', cubesat.radio is not None)
        alerts.set_value(self.debug, 'rtc_available', cubesat.rtc is not None)
        alerts.set_value(self.debug, 'neopixel_available', cubesat.neopixel is not None)
