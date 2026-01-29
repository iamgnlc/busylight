#!/usr/bin/env python3

import sys
import subprocess

BASE_URL = "http://pizero.gnlc.lan:5000/api"


def run_curl(endpoint):
    url = f"{BASE_URL}/{endpoint}"
    try:
        subprocess.run(["curl", "-s", url], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Request failed: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py <command> [args]")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd in ["free", "busy", "away", "holiday", "off"]:
        run_curl(cmd)
    elif cmd == "blink":
        if len(sys.argv) < 3 or sys.argv[2].lower() not in ["on", "off"]:
            print("Usage: python bl.py blink <on|off>")
            sys.exit(1)
        run_curl(f"blink/{sys.argv[2].lower()}")
    elif cmd == "brightness":
        if len(sys.argv) < 3:
            print("Usage: python bl.py brightness <value>")
            sys.exit(1)
        run_curl(f"brightness/{sys.argv[2]}")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
