print("Hello World!")

import board
import neopixel
import digitalio
import time
import math

cam_en = digitalio.DigitalInOut(board.CAM_EN)
cam_en.direction = digitalio.Direction.OUTPUT
cam_en.value = True

pixels = neopixel.NeoPixel(board.NEOPIXEL,1,pixel_order=neopixel.GRB)
pixels[0] = (0,0,0)

last_time = time.monotonic()

pixels.show()
