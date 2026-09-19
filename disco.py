#!/usr/bin/env python3

import random
import threading
import time

from rpi_ws281x import Color

DEFAULT_SPEED = 1  # 1–10

disco_speed = DEFAULT_SPEED
disco_enabled = False

_strip = None
_thread = None
_stop_event = threading.Event()


def init(strip):
    global _strip
    _strip = strip


def clamp_speed(speed: int) -> int:
    if speed < 1:
        return 1
    if speed > 10:
        return 10
    return speed


def randomize(strip):
    for i in range(strip.numPixels()):
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


def _disco_loop():
    while not _stop_event.is_set():
        randomize(_strip)
        delay = speed_to_delay(disco_speed)
        # Sleep in small chunks so speed/stop changes apply quickly
        end = time.time() + delay
        while time.time() < end:
            if _stop_event.is_set():
                return
            time.sleep(0.05)


def start(speed=None):
    """Start disco mode. Optionally set speed (1–10). Returns active speed."""
    global disco_enabled, disco_speed, _thread

    if speed is not None:
        disco_speed = clamp_speed(speed)

    if disco_enabled:
        return disco_speed

    disco_enabled = True
    _stop_event.clear()
    _thread = threading.Thread(target=_disco_loop, daemon=True)
    _thread.start()
    return disco_speed


def stop():
    global disco_enabled

    if not disco_enabled:
        return

    disco_enabled = False
    _stop_event.set()
