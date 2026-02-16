# Tronbyt Client for Interstate 75W

MicroPython client for displaying Tronbyt images on Pimoroni Interstate 75W + HUB75 LED matrix panels.

## Hardware Requirements

- **Pimoroni Interstate 75W** (RP2350-based)
- **HUB75 RGB LED Matrix Panel** (32x32, 64x32, 64x64, or 128x64)
- **USB-C cable** for power and programming
- **WiFi network**

## Software Requirements

- **MicroPython firmware** for Interstate 75W
- **Tronbyt RGB Bridge** server running somewhere (see `../rgb-bridge/`)

## Installation

### 1. Flash MicroPython to Interstate 75W

Download the latest Interstate 75W MicroPython firmware:
```bash
# Visit: https://github.com/pimoroni/interstate75/releases
# Download the .uf2 file for your Interstate 75W variant
```

Flash the firmware:
1. Hold the BOOT button on Interstate 75W
2. Plug in USB-C cable (keep holding BOOT)
3. Release BOOT - a drive should appear
4. Drag the .uf2 file onto the drive
5. The device will reboot with MicroPython

### 2. Upload Client Code

Using Thonny IDE (recommended):
1. Install Thonny: https://thonny.org/
2. Open Thonny, go to Tools → Options → Interpreter
3. Select "MicroPython (Raspberry Pi Pico)" and choose the correct port
4. Click "Files" in Thonny to see both your computer and the Pico
5. Upload these files to the Pico:
   - `main.py`
   - (Optional) `config.py` if you want to separate config

Or using ampy:
```bash
pip install adafruit-ampy

# Upload main.py
ampy --port /dev/ttyACM0 put main.py

# Upload config (if using separate config file)
ampy --port /dev/ttyACM0 put config.py
```

### 3. Configure WiFi and Server

Edit `main.py` (or create `config.py`):

```python
# WiFi credentials
WIFI_SSID = "YourWiFiNetwork"
WIFI_PASSWORD = "YourWiFiPassword"

# RGB Bridge server URL
SERVER_URL = "http://192.168.1.100:8001"  # Your RGB bridge IP
DEVICE_ID = "interstate75_1"               # Your device ID in Tronbyt
```

### 4. Select Display Type

Update the display type to match your panel:

```python
# For 64x64 panel (default)
DISPLAY_TYPE = DISPLAY_INTERSTATE75_64X64

# For 32x32 panel
# DISPLAY_TYPE = DISPLAY_INTERSTATE75_32X32

# For 64x32 panel
# DISPLAY_TYPE = DISPLAY_INTERSTATE75_64X32

# For 128x64 panel (two 64x32 panels)
# DISPLAY_TYPE = DISPLAY_INTERSTATE75_128X64
```

### 5. Reset and Run

1. Reset the Interstate 75W (press the RESET button)
2. The device should:
   - Connect to WiFi
   - Fetch images from the RGB bridge
   - Display them on the LED matrix

## Usage

### Buttons

- **Button A**: Force immediate refresh (fetch next image now)
- **Button B**: Reconnect to WiFi
- **BOOT Button**: Can be used as a third user button if needed

### Serial Console

View logs via serial (useful for debugging):

Using Thonny:
- Tools → Open MicroPython Shell (Ctrl+Alt+P)

Using screen:
```bash
screen /dev/ttyACM0 115200
```

Using minicom:
```bash
minicom -D /dev/ttyACM0 -b 115200
```

### Troubleshooting

**WiFi won't connect:**
- Check SSID and password
- Make sure you're in range
- Press Button B to retry connection
- Check serial console for error messages

**Display shows error messages:**
- `WiFi Failed` - Can't connect to network
- `Network Err` - Can't reach RGB bridge server
- `Fetch Error` - Failed to download image

**Image looks wrong:**
- Verify display type matches your panel
- Check image dimensions in Tronbyt server
- Ensure RGB bridge is converting correctly

**Memory errors:**
- Large images (128x64) may run out of RAM
- Try reducing image complexity in Tronbyt
- Check `gc.mem_free()` in serial console

## Architecture

```
Internet/Local Network
        ↓
Tronbyt Server (Go) - Renders Pixlet apps to WebP
        ↓
RGB Bridge (Python) - Converts WebP to raw RGB
        ↓ WiFi
Interstate 75W (MicroPython) - Fetches RGB data
        ↓ HUB75 protocol
LED Matrix Panel - Displays image
```

## Advanced Configuration

### Custom Brightness Curve

Edit the brightness conversion in `main.py`:

```python
# Linear (default)
display.set_backlight(brightness / 100.0)

# Exponential (more natural)
import math
display.set_backlight(math.pow(brightness / 100.0, 2.2))
```

### WebSocket Support (Future)

For real-time updates without polling, you'll need to implement WebSocket support. This requires:
- `uwebsockets` library
- Modified fetch loop
- Persistent connection handling

### Direct WebP Decoding

If you want to skip the RGB bridge and decode WebP directly on the Interstate 75W:
- Port a lightweight WebP decoder to MicroPython (challenging)
- Or compile a C extension for MicroPython (advanced)

## Performance

**Typical metrics:**
- **Fetch time:** 1-3 seconds (depends on network and image size)
- **Render time:** 0.5-2 seconds (depends on panel size)
- **Memory usage:** 
  - 32x32: ~3KB per frame
  - 64x64: ~12KB per frame
  - 128x64: ~24KB per frame
- **Frame rate:** Limited by network, not rendering (could do 10+ FPS locally)

## License

MIT License - See parent repository for details

## Credits

- **Tronbyt Project**: https://github.com/tronbyt
- **Pimoroni**: https://pimoroni.com
- **Author**: Ollie (AI Assistant)
- **Date**: February 15, 2026
