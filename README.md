# Busylight

### `busylight.py`

Python server to run on a RPi with a 4×8 RGB LED hat model WS2812B.

### `send.py`

Shell script to send command to the server via terminal.

e.g.:

```bash
python send.py busy
```

### `msg.py`

Display a scrolling message.

e.g.:

```bash
sudo python3 msg.py --text=GNLC --color=#00ff00 --rotate180
```
