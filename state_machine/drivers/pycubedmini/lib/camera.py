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
