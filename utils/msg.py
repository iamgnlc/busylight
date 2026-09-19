#!/usr/bin/env python3
#
# Examples:
#   sudo python3 msg.py --text=GNLC
#   sudo python3 msg.py --text=GNLC --color=#00ff00 --rotate
#   sudo python3 msg.py --text=GNLC --brightness=5

import argparse
import time
from rpi_ws281x import PixelStrip, Color

# MATRIX CONFIG
WIDTH = 8
HEIGHT = 4
LED_COUNT = WIDTH * HEIGHT

GPIO_PIN = 18
BRIGHTNESS = 5  # default brightness level (1–10)
DEFAULT_COLOR = "ff0000"
FREQ_HZ = 800000
DMA = 10
INVERT = False
CHANNEL = 0

# ------------------------------------------------------------
# FONT
# ------------------------------------------------------------
FONT = {
    "A": ["0110", "1001", "1111", "1001"],
    "B": ["1110", "1001", "1110", "1111"],
    "C": ["0111", "1000", "1000", "0111"],
    "D": ["1110", "1001", "1001", "1110"],
    "E": ["1111", "1110", "1000", "1111"],
    "F": ["1111", "1000", "1110", "1000"],
    "G": ["0111", "1000", "1011", "0111"],
    "H": ["1001", "1001", "1111", "1001"],
    "I": ["1", "1", "1", "1"],
    "J": ["0011", "0001", "1001", "0110"],
    "K": ["1001", "1010", "1110", "1001"],
    "L": ["100", "100", "100", "111"],
    "M": ["10001", "11011", "10101", "10001"],
    "N": ["1001", "1101", "1011", "1001"],
    "O": ["0110", "1001", "1001", "0110"],
    "P": ["1110", "1001", "1110", "1000"],
    "Q": ["0110", "1001", "1011", "0111"],
    "R": ["1110", "1001", "1110", "1001"],
    "S": ["0111", "1100", "0011", "1110"],
    "T": ["111", "010", "010", "010"],
    "U": ["1001", "1001", "1001", "0110"],
    "V": ["10001", "10001", "01010", "00100"],
    "W": ["10001", "10101", "10101", "01110"],
    "X": ["1001", "0110", "0110", "1001"],
    "Y": ["1001", "0110", "0010", "0100"],
    "Z": ["1111", "0010", "0100", "1111"],
    "0": ["0110", "1001", "1001", "0110"],
    "1": ["010", "110", "010", "111"],
    "2": ["110", "001", "010", "111"],
    "3": ["1110", "0001", "0110", "1110"],
    "4": ["101", "101", "111", "001"],
    "5": ["1111", "1110", "0001", "1110"],
    "6": ["0111", "1000", "1110", "0111"],
    "7": ["111", "001", "010", "100"],
    "8": ["0110", "1111", "1001", "0110"],
    "9": ["0111", "1001", "0111", "0001"],
    " ": ["00", "00", "00", "00"],
    ".": ["0", "0", "0", "1"],
}


# ------------------------------------------------------------
# MATRIX MAPPING
# ------------------------------------------------------------
def xy_to_index(x, y):
    return y * WIDTH + x


def clear(strip):
    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()


def char_width(ch):
    if ch not in FONT:
        ch = " "
    return len(FONT[ch][0])


def parse_hex_color(hex_str):
    s = hex_str.strip()
    if s.startswith("#"):
        s = s[1:]
    if len(s) != 6:
        raise ValueError("Hex color must be 6 digits (RRGGBB)")
    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:6], 16)
    return Color(r, g, b)


def draw_char(strip, ch, x_offset, color, rotate=False):
    if ch not in FONT:
        ch = " "

    bitmap = FONT[ch]
    w = len(bitmap[0])

    for y in range(HEIGHT):
        for x in range(w):
            if bitmap[y][x] == "1":

                px = x_offset + x
                py = y

                if rotate:
                    px = (WIDTH - 1) - px
                    py = (HEIGHT - 1) - py

                if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                    strip.setPixelColor(xy_to_index(px, py), color)


def scroll_text_once(strip, text, color, speed=0.15, rotate=False):
    text = text.upper()

    total_width = 0
    for ch in text:
        total_width += char_width(ch) + 1

    for offset in range(total_width + WIDTH):
        clear(strip)

        x_cursor = WIDTH - offset
        for ch in text:
            draw_char(strip, ch, x_cursor, color, rotate)
            x_cursor += char_width(ch) + 1

        strip.show()
        time.sleep(speed)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--text",
        required=True,
        help="The text message to scroll on the LED matrix",
    )

    parser.add_argument(
        "--rotate", action="store_true", help="Rotate the text output by 180 degrees"
    )

    parser.add_argument(
        "--color",
        default=DEFAULT_COLOR,
        help=(f"Text color in hex (default: #{DEFAULT_COLOR})"),
    )

    # Brightness parameter (1–10)
    parser.add_argument(
        "--brightness",
        type=int,
        choices=range(1, 11),
        default=BRIGHTNESS,
        help="LED brightness level (default: %d)" % BRIGHTNESS,
    )

    args = parser.parse_args()

    text_color = parse_hex_color(args.color)

    # Convert 1–10 brightness into 0–255 range for WS281x
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
            scroll_text_once(strip, args.text, color=text_color, rotate=args.rotate)

    except KeyboardInterrupt:
        clear(strip)


if __name__ == "__main__":
    main()
