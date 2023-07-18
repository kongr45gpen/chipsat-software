from Tasks.log import LogTask as Task
import radio_utils.image_queue as iq
from pycubed import cubesat
from time import monotonic, localtime
from gc import collect
from lib.alerts import alerts
import tasko

# constants
CONFIRMATION_SEND_CODE = 0xAA
CONFIRMATION_RECEIVE_CODE = 0xAB
IMAGE_START = 0xAC
IMAGE_MID = 0xAD
IMAGE_END = 0xAE
IMAGE_CONF = 0xAF
PACKET_REQ = 0xB0
NO_IMAGE = 0xB1
MAX_CONF_ATTEMPTS = 3

"""
buffer to be used with the UART channel to read into and get data
"""
image_buffer = bytearray(499)
"""
to avoid having to list slice (which uses signigicant memory creating "copies" of the list)
the buffer that contains the header and the buffer that contains the image data are separated
"""
header_buffer  = bytearray(1)
class task(Task):
    name = 'image'
    color = 'blue'

    last_time = monotonic()
    cam_on = False
    cam_active = False
    conf_attempts = 0

    filepath = ""

    def should_activate(self):
        """
        clock that returns True every 60 seconds
        """
        if monotonic() - 60 > self.last_time:
            self.last_time = monotonic()
            alerts.clear(self.debug, 'camera_disabled')
            return True
        return False

    async def main_task(self):
        """
        gets an image from the camera board
        """
        if not cubesat.camera:
            alerts.clear(self.debug, 'camera_available')
            alerts.clear(self.debug, 'image_queue_full')
            alerts.clear(self.debug, 'camera_disabled')
            return
        elif iq.size() >= 5:
            alerts.set(self.debug, 'image_queue_full')
            alerts.set(self.debug, 'camera_disabled')
            return
        else:
            alerts.clear(self.debug, 'image_queue_full')
        collect()

        st = monotonic()
        if self.should_activate() and not self.cam_active and not self.cam_on:
            # turn the camera on
            self.debug("Turning Camera on")
            cubesat.cam_pin.value = True
            self.cam_on = True
        elif (not self.cam_active) and self.cam_on:
            # await self.get_confirmation(st)
            self.debug("checking camera connection...")
            success = cubesat.camera.get_confirmation
            if success:
                self.cam_active = True
                self.conf_attempts = 0
                alerts.clear(self.debug, 'camera_failed')
                self.debug("...connection confirmed")
            else:
                self.conf_attempts += 1
            self.check_attempts()
        elif self.cam_active and self.cam_on:
            self.debug("getting image packets")
            # get as many packets in 2 seconds as it can
            await self.get_packets(st)
        else:
            self.debug("camera asleep")
            if not iq.empty():
                self.debug(f"{iq.peek()}", level=2)
            else:
                self.debug("queue empty", level=2)

        collect()

    def check_attempts(self):
        if self.conf_attempts > MAX_CONF_ATTEMPTS:
            # turn off camera to not waste battery as something is wrong
            alerts.set(self.debug, 'camera_disabled')
            alerts.set(self.debug, 'camera_failed')
            cubesat.cam_pin.value = False
            self.cam_on = False
            self.cam_active = False
            self.conf_attempts = 0

    async def get_confirmation(self, st) -> bool:
        # camera has likely just been turned on and we need to verify connection
        self.debug("checking camera connection...")
        # look for 2 seconds
        await tasko.sleep(0)
        while monotonic() - 2 < st:
            cubesat.uart_camera.readinto(header_buffer)
            if CONFIRMATION_SEND_CODE == header_buffer[0]:
                alerts.clear(self.debug, 'camera_failed')
                header_buffer[0] = CONFIRMATION_RECEIVE_CODE
                cubesat.uart_camera.write(header_buffer)
                self.debug("responding", level=2)
                cubesat.uart.reset_input_buffer()
                self.cam_active = True
                self.conf_attempts = 0
                break
        self.conf_attempts += 1
        if self.conf_attempts > MAX_CONF_ATTEMPTS:
            # turn off camera to not waste battery as something is wrong
            alerts.set(self.debug, 'camera_disabled')
            alerts.set(self.debug, 'camera_failed')
            cubesat.cam_pin.value = False
            self.cam_on = False
            self.cam_active = False
            self.conf_attempts = 0

    async def get_packets(self, st):
        done = False
        await tasko.sleep(0)
        while monotonic() - 2 < st and not done:
            done = self.get_packet()

    def get_packet(self) -> bool:
        """gets packets from the camera and writes those packets to the current
        working file. If this is the last time this function should run within the
        given scope, it returns True, otherwise it returns False"""
        header_buffer[0] = PACKET_REQ
        cubesat.uart_camera.write(header_buffer)
        valid_packet = False
        st = monotonic()
        file_err = False
        while monotonic() - 2 < st:
            cubesat.uart_camera.readinto(header_buffer)
            if header_buffer[0] == NO_IMAGE:
                self.debug("image not interesting")
                cubesat.cam_pin.value = False
                self.cam_active = False
                self.cam_on = False
                valid_packet = True
                break
            cubesat.uart_camera.readinto(image_buffer)
            if (header_buffer[0] == IMAGE_START or header_buffer[0] == IMAGE_MID or header_buffer[0] == IMAGE_END):
                valid_packet = True
                break
            elif header_buffer[0] == CONFIRMATION_SEND_CODE:
                self.cam_active = False
                self.debug("camera did not receive confirmation")
                return True
        if not valid_packet:
            self.debug("could not get packet")
            cubesat.uart_camera.reset_input_buffer()
            self.conf_attempts += 1
            if self.conf_attempts > MAX_CONF_ATTEMPTS:
                alerts.set(self.debug, 'camera_disabled')
                alerts.set(self.debug, 'camera_failed')
                cubesat.cam_pin.value = False
                self.cam_on = False
                self.cam_active = False
                self.conf_attempts = 0
            return False
        alerts.clear(self.debug, 'camera_failed')
        last_packet = False
        self.conf_attempts = 0
        if header_buffer[0] == IMAGE_START:
            valid_packet = True
            # first packet
            # create new image file
            if cubesat.rtc:
                t = cubesat.rtc.datetime
            else:
                t = localtime()
            timestamp = f"{t.tm_year:04}.{t.tm_mon:02}.{t.tm_mday:02}.{t.tm_hour:02}.{t.tm_min:02}.{t.tm_sec:02}"
            self.filepath = f"/sd/images/{timestamp}.jpeg"
            self.debug(f"creating image at: {self.filepath}")
            try:
                with open(self.filepath, "wb") as fd:
                    fd.write(image_buffer)
            except Exception as e:
                file_err = True
                print(f"could not create new image file: {e}")
        elif header_buffer[0] == IMAGE_MID:
            # middle packet
            try:
                with open(self.filepath, "ab") as fd:
                    fd.write(image_buffer)
            except Exception as e:
                file_err = True
                print(f"could not write mid packet to {self.filepath}: {e}")
        elif header_buffer[0] == IMAGE_END:
            self.debug("end file")
            index = image_buffer.find(b'\xFF\xD9')
            # last packet
            try:
                with open(self.filepath, "ab") as fd:
                    fd.write(image_buffer[1:index + 2])
                alerts.set(self.debug, 'camera_disabled')
                cubesat.cam_pin.value = False
                self.cam_on = False
                self.cam_active = False
                last_packet = True
                iq.push(self.filepath)
            except Exception as e:
                file_err = True
                print(f"could not write last packet to file: {e}")

        if not file_err:
            # send confirmation of recieved packet
            cubesat.uart_camera.reset_input_buffer()
            header_buffer[0] = IMAGE_CONF
            cubesat.uart_camera.write(header_buffer)
            return last_packet
