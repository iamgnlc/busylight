#!/usr/bin/env python3

import sys
import subprocess
import os

BASE_URL = "http://pizero:5000/api"
# BASE_URL = "http://pizero.gnlc.lan:5000/api"

SCRIPT_NAME = os.path.basename(sys.argv[0])


def run_curl(endpoint):
    url = f"{BASE_URL}/{endpoint}"
    try:
        subprocess.run(["curl", "-s", url], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Request failed: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {SCRIPT_NAME} <command> [args]")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    match cmd:
        case "free" | "busy" | "away" | "dnd" | "off" | "status":
            run_curl(cmd)

        case "blink":
            if len(sys.argv) < 3 or sys.argv[2].lower() not in ["on", "off"]:
                print(f"Usage: {SCRIPT_NAME} blink <on|off>")
                sys.exit(1)
            run_curl(f"blink/{sys.argv[2].lower()}")

        case "brightness":
            if len(sys.argv) < 3:
                print(f"Usage: {SCRIPT_NAME} brightness <value>")
                sys.exit(1)
            run_curl(f"brightness/{sys.argv[2]}")

        case _:
            print(f"Unknown command: {cmd}")
            sys.exit(1)


if __name__ == "__main__":
    main()
