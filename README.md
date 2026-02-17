# Tronbyt RP2350 Client

MicroPython firmware for **RP2350-based boards** that fetches and displays WebP images from a [Tronbyt](https://github.com/tronbyt/server) server on HUB75 LED matrices.

## Features

- 📡 WiFi connectivity for remote image updates
- 🖼️ Native WebP decoding via C module (`webpdec`)
- 💡 Automatic brightness control from server
- 🔄 Continuous frame updates from Tronbyt
- 🔌 Board-agnostic design (pluggable display drivers)
- ⚡ Supports 64x32, 64x64, and other HUB75 matrix sizes
- 📱 Automatic WiFi provisioning with captive portal

## Supported Hardware

### Primary Target
- **[Pimoroni Interstate 75W](https://shop.pimoroni.com/products/interstate-75-w)** (RP2350-based HUB75 driver)

### Other RP2350 Boards
The firmware is designed to be board-agnostic. To add support for a new board, you need:
- RP2350 microcontroller
- WiFi connectivity
- HUB75 interface (GPIOs + level shifters if needed)
- Display driver implementation in `main.py`

## Hardware Requirements

- **RP2350 board with WiFi** (Interstate 75W recommended)
- **HUB75 LED Matrix** (64x32 or 64x64)
- **5V Power Supply** capable of driving your matrix
- **WiFi Network**

## Quick Start

### Option 1: Download Pre-built Firmware

Get the latest firmware from [GitHub Releases](https://github.com/johnfernkas/tronbyt-rp2350/releases):
- `tronbyt-rp2350-64x32.uf2` - For 64x32 matrices
- `tronbyt-rp2350-64x64.uf2` - For 64x64 matrices

Flash to your RP2350 board:
1. Hold **BOOT** button, plug in USB, release BOOT
2. Copy the `.uf2` file to the RPI-RP2 drive
3. Board will reboot with firmware

### Option 2: Build from Source

```bash
# Clone this repo
git clone https://github.com/johnfernkas/tronbyt-rp2350.git

# Clone MicroPython and Pimoroni libraries
git clone https://github.com/micropython/micropython.git
git clone https://github.com/pimoroni/interstate75.git

# Build firmware with webpdec module
cd micropython/ports/rp2
make USER_C_MODULES=/path/to/tronbyt-rp2350/webpdec
```

## Configuration

### Option 1: Automatic WiFi Provisioning (Recommended)

On first boot (or when no valid WiFi config exists), the device automatically enters provisioning mode:

1. Creates WiFi AP: `Tronbyt-Setup` (password: `setup1234`)
2. Connect your phone/computer to this AP
3. Open http://192.168.4.1 in your browser
4. Enter WiFi credentials and display settings
5. Device saves config and reboots automatically

### Option 2: Manual Configuration

Copy `config.py` to `config_local.py` and edit:

```python
# WiFi Configuration
WIFI_SSID = "YourWiFiSSID"
WIFI_PASSWORD = "YourWiFiPassword"

# Tronbyt Server Configuration
TRONBYT_SERVER_URL = "http://192.168.1.100:8000"
DISPLAY_ID = "rp2350-001"

# Display Configuration
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32

# Debug mode
DEBUG = False
```

Upload to your board using [Thonny](https://thonny.org/) or `mpremote`:

```bash
mpremote cp config_local.py :
mpremote cp provisioning.py :  # Required for provisioning mode
mpremote reset
```

### Re-Provisioning

To reconfigure WiFi on an existing device:

```bash
mpremote rm :config_local.py
mpremote reset
```

The device will enter provisioning mode on next boot.

## Architecture

```
┌─────────────────┐
│ Tronbyt Server  │  Renders Pixlet apps to WebP
└────────┬────────┘
         │ HTTP GET /next
         ▼
┌─────────────────┐
│  RP2350 Board   │  MicroPython + webpdec module
│  - WiFi         │  Decodes WebP to RGB565
│  - webpdec      │  Displays on HUB75 matrix
│  - HUB75 driver │
└────────┬────────┘
         │ HUB75 protocol
         ▼
┌─────────────────┐
│  LED Matrix     │  64x32 or 64x64 RGB panel
└─────────────────┘
```

## Board Abstraction

The firmware uses a board abstraction layer in `main.py`. Currently supports:

### Interstate 75 (Pimoroni)
```python
from interstate75 import Interstate75
BOARD_TYPE = "interstate75"
```

### Adding New Board Support

To add a new board, modify the `_init_display()` method in `main.py`:

```python
def _init_display(self):
    if BOARD_TYPE == "your_board":
        # Initialize your display driver
        self.display = YourDriver()
        self._display_type = "your_board"
```

And implement `_display_rgb565()` for your hardware.

## webpdec Module

The `webpdec` module is a MicroPython native module in C that decodes WebP to RGB565.

**API:**
```python
import webpdec

# Decode WebP to RGB565 format
rgb565_data = webpdec.decode(webp_bytes, width, height)
# Returns: bytearray (width * height * 2 bytes)
```

See `webpdec/webpdec.c` for the implementation.

## CI/CD

GitHub Actions automatically builds firmware on every push:
- Builds for 64x32 and 64x64 display sizes
- Creates release artifacts
- Publishes to GitHub Releases on tagged versions

## Tronbyt Server Setup

You'll need a Tronbyt server running. See [github.com/tronbyt/server](https://github.com/tronbyt/server) for setup.

## Files

- `main.py` - Main firmware with board abstraction
- `config.py` - Configuration template
- `provisioning.py` - WiFi captive portal for automatic setup
- `webpdec/` - C WebP decoder module
  - `webpdec.c` - Module implementation
  - `micropython.mk` - Build integration

## License

MIT License - See [LICENSE](LICENSE)
