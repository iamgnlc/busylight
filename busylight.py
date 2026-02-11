#!/usr/bin/env python3

import os
import atexit
import signal
import sys
import threading
import time
import json

from flask import Flask, jsonify, Response
from rpi_ws281x import PixelStrip, Color

# =====================
# LED CONFIGURATION
# =====================
LED_COUNT = 32
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_INVERT = False
LED_MAX_BRIGHTNESS = 255

BLINK_INTERVAL = 0.5

# =====================
# STATE
# =====================
current_status = "free"  # off, busy, away, free, dnd
current_brightness = 1  # 1–10
blink_enabled = False

blink_thread = None
blink_stop_event = threading.Event()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "led_state.json")
state_lock = threading.Lock()

# =====================
# LED SETUP
# =====================
strip = PixelStrip(
    LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_MAX_BRIGHTNESS
)
strip.begin()


# =====================
# STATE PERSISTENCE
# =====================
def save_state():
    data = {
        "status": current_status,
        "brightness": current_brightness,
        "blink": blink_enabled,
    }
    try:
        with state_lock:
            with open(STATE_FILE, "w") as f:
                json.dump(data, f)
    except Exception:
        pass


def load_state():
    global current_status, current_brightness, blink_enabled

    if not os.path.exists(STATE_FILE):
        return

    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)

        current_status = data.get("status", current_status)
        current_brightness = int(data.get("brightness", current_brightness))
        blink_enabled = bool(data.get("blink", blink_enabled))
    except Exception:
        pass


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
        set_all(Color(0, 255, 0))
    elif current_status == "busy":
        set_all(Color(255, 0, 0))
    elif current_status == "away":
        set_all(Color(255, 165, 0))
    elif current_status == "dnd":
        set_all(Color(77, 23, 154))
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
    global blink_enabled, blink_thread

    if blink_enabled:
        return

    blink_enabled = True
    blink_stop_event.clear()

    blink_thread = threading.Thread(target=blink_loop, daemon=True)
    blink_thread.start()


def stop_blink():
    global blink_enabled

    if not blink_enabled:
        return

    blink_enabled = False
    blink_stop_event.set()
    apply_status()


# =====================
# CLEANUP
# =====================
def cleanup():
    stop_blink()
    turn_off()
    save_state()
    sys.exit(0)


atexit.register(save_state)
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
    save_state()
    return current_status, 200


@app.route("/api/busy", methods=["GET"])
def busy():
    global current_status
    current_status = "busy"
    apply_status()
    save_state()
    return current_status, 200


@app.route("/api/free", methods=["GET"])
def free():
    global current_status
    current_status = "free"
    apply_status()
    save_state()
    return current_status, 200


@app.route("/api/away", methods=["GET"])
def away():
    global current_status
    current_status = "away"
    apply_status()
    save_state()
    return current_status, 200


@app.route("/api/dnd", methods=["GET"])
def dnd():
    global current_status
    current_status = "dnd"
    apply_status()
    save_state()
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
    save_state()

    return f"brightness {level}", 200


@app.route("/api/blink/on", methods=["GET"])
def blink_on():
    start_blink()
    save_state()
    return "blink on", 200


@app.route("/api/blink/off", methods=["GET"])
def blink_off():
    stop_blink()
    save_state()
    return "blink off", 200


@app.route("/api/shutdown", methods=["GET"])
def shutdown_rpi():
    def shutdown():
        stop_blink()
        turn_off()
        save_state()
        os.system("sudo shutdown now")

    threading.Thread(target=shutdown, daemon=True).start()
    return Response("Shutting down Raspberry Pi...", status=200)


# =====================
# STARTUP
# =====================
def init_app():
    load_state()
    apply_brightness()
    apply_status()

    if blink_enabled:
        start_blink()


if __name__ == "__main__":
    init_app()
    app.run(host="0.0.0.0", port=5000, threaded=True, use_reloader=False)
