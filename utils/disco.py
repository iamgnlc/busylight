#!/usr/bin/env python3
#
# Examples:
#   sudo python3 disco.py
#   sudo python3 disco.py --brightness=1 --speed=10

import argparse
import time
import random
from rpi_ws281x import PixelStrip, Color

# MATRIX CONFIG
WIDTH = 8
HEIGHT = 4
LED_COUNT = WIDTH * HEIGHT

GPIO_PIN = 18
FREQ_HZ = 800000
DMA = 10
INVERT = False
CHANNEL = 0

DEFAULT_BRIGHTNESS = 5  # 1–10
DEFAULT_SPEED = 5  # 1–10


def clear(strip):
    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()


def randomize(strip):
    for i in range(LED_COUNT):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        strip.setPixelColor(i, Color(r, g, b))
    strip.show()


def speed_to_delay(speed_level: int) -> float:
    """
    Convert 1–10 speed scale to delay:
    1  -> 1.0 sec
    10 -> 0.1 sec
    """
    return 1.0 - ((speed_level - 1) * 0.1)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--speed",
        type=int,
        choices=range(1, 11),
        default=DEFAULT_SPEED,
        help="Speed 1–10 (1 = slowest 1s, 10 = fastest 0.1s)",
    )

    parser.add_argument(
        "--brightness",
        type=int,
        choices=range(1, 11),
        default=DEFAULT_BRIGHTNESS,
        help="Brightness level 1–10",
    )

    args = parser.parse_args()

    delay = speed_to_delay(args.speed)
    brightness = int(args.brightness * 255 / 10)

    strip = PixelStrip(
        LED_COUNT,
        GPIO_PIN,
        FREQ_HZ,
        DMA,
        INVERT,
        brightness,
        CHANNEL,
    )
    strip.begin()

    try:
        while True:
            randomize(strip)
            time.sleep(delay)

    except KeyboardInterrupt:
        clear(strip)


if __name__ == "__main__":
    main()
