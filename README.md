# Busylight

### `busylight.py`

Python server to run on a RPi with a 4×8 RGB LED hat model WS2812B.

### `send.py`

Shell script to send command to the server via terminal.

e.g.:

```bash
python send.py busy
```

### `.hammerspoon/init.lua`

Hammerspoon config file to read Teams status and send update to the server running on RPi.
