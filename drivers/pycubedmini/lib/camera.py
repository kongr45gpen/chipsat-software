from time import monotonic


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


class Camera:
    def __init__(self, uart_bus) -> None:
        self.uart = uart_bus

    @property
    def get_confirmation(self) -> bool:
        st = monotonic()
        # camera has likely just been turned on and we need to verify connection
        # look for 2 seconds
        while monotonic() - 2 < st:
            self.uart.readinto(header_buffer)
            if CONFIRMATION_SEND_CODE == header_buffer[0]:
                header_buffer[0] = CONFIRMATION_RECEIVE_CODE
                self.uart.write(header_buffer)
                self.uart.reset_input_buffer()
                return True
        return False

    @property
    def get_packet(self) -> tuple:
        """
        gets packets from the camera and writes those packets to the current
        working file.

        returns packet and a code which correspondes to what happened when getting the packet
        - 0: success
        - 1: success, image not interesting
        - 2: success, first packet
        - 3: success, last packet
        - 4: camera must not have received our confirmation byte as we are still getting
             the confirmation send code, send confirmation byte again
        - 5: failed to get packet
        """

        header_buffer[0] = PACKET_REQ
        self.uart.write(header_buffer)
        valid_packet = False
        st = monotonic()
        while monotonic() - 2 < st:
            self.uart.readinto(header_buffer)
            if header_buffer[0] == NO_IMAGE:
                return None, 1
            if (header_buffer[0] == IMAGE_START or header_buffer[0] == IMAGE_MID or header_buffer[0] == IMAGE_END):
                valid_packet = True
                self.uart.readinto(image_buffer)
                break
            elif header_buffer[0] == CONFIRMATION_SEND_CODE:
                return None, 4
        if not valid_packet:
            self.uart.reset_input_buffer()
            return None, 5
        if header_buffer[0] == IMAGE_START:
            # first packet
            # create new image file
            return image_buffer, 2
        elif header_buffer[0] == IMAGE_MID:
            # middle packet
            return image_buffer, 0
        elif header_buffer[0] == IMAGE_END:
            return image_buffer, 3

    @property
    def ack(self):
        self.uart.reset_input_buffer()
        header_buffer[0] = IMAGE_CONF
        self.uart.write(header_buffer)
