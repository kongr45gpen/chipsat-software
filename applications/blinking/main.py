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
pixels[0] = (10,0,50)

last_time = time.monotonic()

while True:
    pixels.show()
    time.sleep(0.02)

    t = time.monotonic()

    max_brt = 25

    red = int(max_brt * (math.sin(t *2 * 2 * math.pi)/2 + 0.5))
    green = int(max_brt * (math.sin(t * 0.5 * 2 * math.pi)/2 + 0.5))
    blue = int(max_brt * (math.sin(t * 2 * math.pi)/2 + 0.5))
    pixels[0] = (red, green, blue)

    if t - last_time >= 1:
        print(f"Time is now {time.monotonic()}!")
        last_time = t
