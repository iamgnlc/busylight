#!/usr/bin/env python3

import os
import atexit
import signal
import sys
import threading
import time

from flask import Flask, jsonify, Response
from rpi_ws281x import PixelStrip, Color

# =====================
# LED CONFIGURATION
# =====================
LED_COUNT = 32  # 4x8 matrix
LED_PIN = 18  # GPIO18 (PWM)
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_INVERT = False
LED_MAX_BRIGHTNESS = 255

BLINK_INTERVAL = 0.5  # 500ms

# =====================
# STATE
# =====================
current_status = "free"  # off, busy, away, free, holiday
current_brightness = 1  # 0–10

blink_enabled = False
blink_thread = None
blink_stop_event = threading.Event()

# =====================
# LED SETUP
# =====================
strip = PixelStrip(
    LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_MAX_BRIGHTNESS
)
strip.begin()


# =====================
# HELPERS
# =====================
def set_all(color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()


def turn_off():
    set_all(Color(0, 0, 0))


def apply_brightness():
    brightness = int((current_brightness / 10) * LED_MAX_BRIGHTNESS)
    strip.setBrightness(brightness)
    strip.show()


def apply_status():
    if current_status == "free":
        # Green
        set_all(Color(0, 255, 0))
    elif current_status == "busy":
        # Red
        set_all(Color(255, 0, 0))
    elif current_status == "away":
        # Yellow
        set_all(Color(255, 165, 0))
    elif current_status == "holiday":
        # Purple
        set_all(Color(128, 0, 128))
    else:
        stop_blink()
        turn_off()


# =====================
# BLINK THREAD
# =====================
def blink_loop():
    while not blink_stop_event.is_set():
        turn_off()
        time.sleep(BLINK_INTERVAL)

        if blink_stop_event.is_set():
            break

        apply_status()
        time.sleep(BLINK_INTERVAL)


def start_blink():
    global blink_enabled, blink_thread, blink_stop_event

    if blink_enabled:
        return

    blink_enabled = True
    blink_stop_event.clear()

    blink_thread = threading.Thread(target=blink_loop, daemon=True)
    blink_thread.start()


def stop_blink():
    global blink_enabled, blink_stop_event

    if not blink_enabled:
        return

    blink_enabled = False
    blink_stop_event.set()
    apply_status()


# =====================
# CLEANUP ON EXIT
# =====================
def cleanup():
    print("Shutting down... turning off LEDs")
    stop_blink()
    turn_off()
    sys.exit(0)


atexit.register(turn_off)
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

# =====================
# FLASK APP
# =====================
app = Flask(__name__)


@app.route("/api/off", methods=["GET"])
def off():
    global current_status
    current_status = "off"
    apply_status()
    return current_status, 200


@app.route("/api/busy", methods=["GET"])
def busy():
    global current_status
    current_status = "busy"
    apply_status()
    return current_status, 200


@app.route("/api/free", methods=["GET"])
def free():
    global current_status
    current_status = "free"
    apply_status()
    return current_status, 200


@app.route("/api/away", methods=["GET"])
def away():
    global current_status
    current_status = "away"
    apply_status()
    return current_status, 200


@app.route("/api/holiday", methods=["GET"])
def holiday():
    global current_status
    current_status = "holiday"
    apply_status()
    return current_status, 200


@app.route("/api/status", methods=["GET"])
def status():
    return (
        jsonify(
            {
                "status": current_status,
                "blink": blink_enabled,
                "brightness": current_brightness,
            }
        ),
        200,
    )


@app.route("/api/brightness/<int:level>", methods=["GET"])
def brightness(level):
    global current_brightness

    if level < 1:
        level = 1
    elif level > 10:
        level = 10

    current_brightness = level
    apply_brightness()
    apply_status()

    return f"brightness {level}", 200


# =====================
# BLINK ENDPOINTS
# =====================
@app.route("/api/blink/on", methods=["GET"])
def blink_on():
    start_blink()
    return "blink on", 200


@app.route("/api/blink/off", methods=["GET"])
def blink_off():
    stop_blink()
    return "blink off", 200


# =====================
# SHUTDOWN ENDPOINT
# =====================
@app.route("/api/shutdown", methods=["GET"])
def shutdown_rpi():
    """
    Shuts down the Raspberry Pi safely.
    """

    def shutdown():
        stop_blink()
        turn_off()
        os.system("sudo shutdown now")  # or use 'sudo poweroff'

    threading.Thread(target=shutdown, daemon=True).start()
    return Response("Shutting down Raspberry Pi...", status=200)


# =====================
# STARTUP
# =====================
def init_app():
    apply_brightness()
    apply_status()


if __name__ == "__main__":
    init_app()
    app.run(host="0.0.0.0", port=5000)
