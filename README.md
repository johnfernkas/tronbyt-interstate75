# Tronbyt Interstate 75W Client

A MicroPython client for the [Pimoroni Interstate 75W (RP2350)](https://shop.pimoroni.com/products/interstate-75-w) that fetches and displays WebP images from a [Tronbyt server](https://github.com/tronbyt/server) on HUB75 LED matrices.

## Features

- 📡 WiFi connectivity for remote image updates
- 🖼️ WebP image decoding via native C module
- 💡 Automatic brightness control from server
- 🔄 Continuous frame updates from Tronbyt server
- ⚡ Optimized for 64x32 HUB75 matrices
- 🛠️ Easy configuration

## Hardware Requirements

- **Pimoroni Interstate 75W (RP2350)** - HUB75 matrix driver board
- **64x32 HUB75 LED Matrix** - Any standard HUB75 panel
- **Power Supply** - 5V power supply capable of powering your matrix
- **WiFi Network** - For connecting to Tronbyt server

## Quick Start

### 1. Flash MicroPython Firmware

Download the latest Interstate 75W MicroPython firmware:
```bash
# Get the latest release from Pimoroni
wget https://github.com/pimoroni/interstate75/releases/latest/download/interstate75w-rp2350-vX.X.X.uf2
```

Flash to your Interstate 75W:
1. Connect Interstate 75W to your computer via USB-C
2. Hold **BOOT** button and tap **RST** to enter bootloader mode
3. Drag and drop the `.uf2` file to the **RP2350** drive
4. The board will reboot automatically

### 2. Build and Install WebP Decoder Module

The WebP decoder is a C module that needs to be compiled:

```bash
# Clone MicroPython and this repo
git clone https://github.com/micropython/micropython.git
cd micropython
git submodule update --init

# Copy the webpdec module
cp -r /path/to/tronbyt-interstate75/webpdec ports/rp2/modules/

# Build MicroPython with the module
cd ports/rp2
make BOARD=PIMORONI_INTERSTATE75W USER_C_MODULES=modules/webpdec/micropython.mk

# Flash the resulting .uf2 file
```

**Note:** The current `webpdec.c` includes a placeholder test pattern. For production use, integrate libwebp (see [Building with libwebp](#building-with-libwebp)).

### 3. Configure and Deploy

1. Copy `config.py` to `config_local.py`:
```bash
cp config.py config_local.py
```

2. Edit `config_local.py` with your settings:
```python
WIFI_SSID = "YourWiFiNetwork"
WIFI_PASSWORD = "YourPassword"
TRONBYT_SERVER_URL = "http://192.168.1.100:8000"
DISPLAY_ID = "my-interstate75"
```

3. Copy files to Interstate 75W:
```bash
# Using Thonny, ampy, or mpremote
mpremote cp config_local.py :config_local.py
mpremote cp main.py :main.py
```

4. Reboot the board - it will automatically run `main.py`

## Configuration

All configuration is in `config.py` (or `config_local.py`):

| Setting | Description | Default |
|---------|-------------|---------|
| `WIFI_SSID` | WiFi network name | `"YourWiFiSSID"` |
| `WIFI_PASSWORD` | WiFi password | `"YourWiFiPassword"` |
| `TRONBYT_SERVER_URL` | Tronbyt server URL | `"http://192.168.1.100:8000"` |
| `DISPLAY_ID` | Unique display identifier | `"interstate75-001"` |
| `DISPLAY_WIDTH` | Matrix width in pixels | `64` |
| `DISPLAY_HEIGHT` | Matrix height in pixels | `32` |
| `UPDATE_INTERVAL` | Frame update interval (seconds) | `1.0` |
| `MAX_RETRIES` | Max consecutive errors before showing error | `3` |
| `DEFAULT_BRIGHTNESS` | Default brightness (0-100) | `50` |
| `DEBUG` | Enable debug output | `True` |

## Tronbyt Server Setup

This client connects to a Tronbyt server. Set up your server first:

1. **Install Tronbyt Server** (see [tronbyt/server](https://github.com/tronbyt/server)):
   ```bash
   docker compose up -d
   ```

2. **Add your display** via the web UI at `http://localhost:8000`

3. **Configure apps** using the Pixlet interface

4. The client will automatically fetch frames from:
   ```
   GET /frame?display={DISPLAY_ID}
   ```

Server response headers:
- `X-Brightness` or `Tronbyt-Brightness`: Brightness value (0-100)

## Building with libwebp

For production use with real WebP decoding:

### Option 1: Minimal libwebp Integration

1. Download libwebp:
```bash
cd webpdec/
git clone https://chromium.googlesource.com/webm/libwebp
```

2. Update `webpdec/micropython.mk` to include libwebp sources (see comments in file)

3. Replace `webpdec.c` with `webpdec_full.c`:
```bash
mv webpdec.c webpdec_placeholder.c
mv webpdec_full.c webpdec.c
```

4. Rebuild MicroPython firmware with the updated module

### Option 2: Pre-built Module (.mpy)

If you have a working `.mpy` compiled module, you can deploy it directly:

```bash
mpremote cp webpdec.mpy :webpdec.mpy
```

## Architecture

```
┌─────────────────────┐
│  Interstate 75W     │
│  (RP2350)           │
│                     │
│  ┌──────────────┐   │      ┌──────────────┐
│  │  main.py     │◄──┼──────┤ Tronbyt      │
│  │              │   │ WiFi │ Server       │
│  │  - WiFi      │   │      │              │
│  │  - HTTP      │   │      │ - Apps       │
│  │  - Display   │   │      │ - Rendering  │
│  └──────┬───────┘   │      └──────────────┘
│         │           │
│         ▼           │
│  ┌──────────────┐   │
│  │  webpdec.so  │   │
│  │  (C module)  │   │
│  │              │   │
│  │  - libwebp   │   │
│  │  - RGB565    │   │
│  └──────┬───────┘   │
│         │           │
│         ▼           │
│  ┌──────────────┐   │
│  │  HUB75       │   │      ┌──────────────┐
│  │  Driver      │───┼──────►  64x32 LED   │
│  └──────────────┘   │      │  Matrix      │
└─────────────────────┘      └──────────────┘
```

## Memory Considerations

The RP2350 has **520KB of SRAM**. For a 64x32 display:

- **Frame buffer (RGB565)**: 64 × 32 × 2 = 4,096 bytes
- **WebP decode buffer**: ~10-20KB (depends on image)
- **HTTP buffer**: ~4KB
- **MicroPython runtime**: ~200KB

Total usage is well within limits for this display size.

## Troubleshooting

### WiFi won't connect
- Check SSID and password in `config_local.py`
- Ensure your network is 2.4GHz (Interstate 75W doesn't support 5GHz)
- Check signal strength

### Display shows "Error"
- Check Tronbyt server is running and accessible
- Verify `TRONBYT_SERVER_URL` is correct
- Check `DISPLAY_ID` matches a display in your Tronbyt server
- Enable `DEBUG = True` and check serial output

### No image or blank display
- Verify WebP decoder module is installed (`import webpdec` in REPL)
- Check HUB75 matrix is properly connected
- Verify power supply is adequate for your matrix
- Try adjusting brightness

### "webpdec module not found"
- The C module wasn't compiled into the firmware
- See [Build and Install WebP Decoder Module](#2-build-and-install-webp-decoder-module)

### Memory errors
- Reduce `UPDATE_INTERVAL` to allow more GC time
- Use smaller images from Tronbyt server
- Disable debug mode (`DEBUG = False`)

## Development

### Project Structure
```
tronbyt-interstate75/
├── main.py                 # Main firmware logic
├── config.py               # Configuration template
├── config_local.py         # Your local config (gitignored)
├── webpdec/                # WebP decoder C module
│   ├── webpdec.c           # Placeholder implementation
│   ├── webpdec_full.c      # Full libwebp implementation
│   └── micropython.mk      # MicroPython build config
├── docs/                   # Additional documentation
├── examples/               # Example code
├── LICENSE                 # MIT License
└── README.md               # This file
```

### Running Tests

```bash
# Test on device via REPL
mpremote repl

>>> import main
>>> client = main.TronbytClient()
>>> client.connect_wifi()
>>> client.run()
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on real hardware
5. Submit a pull request

## Related Projects

- [Tronbyt Server](https://github.com/tronbyt/server) - Local Tidbyt-compatible server
- [Pimoroni Interstate 75](https://github.com/pimoroni/interstate75) - Official Interstate 75 MicroPython
- [libwebp](https://github.com/webmproject/libwebp) - WebP image library

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/johnfernkas/tronbyt-interstate75/issues)
- **Tronbyt Discussions**: [Tronbyt Server Discussions](https://github.com/tronbyt/server/discussions)
- **Pimoroni Forums**: [Pimoroni Forum](https://forums.pimoroni.com/)

## Acknowledgments

- [Pimoroni](https://pimoroni.com) for the excellent Interstate 75W hardware
- [Tronbyt](https://github.com/tronbyt) team for the local Tidbyt server
- [MicroPython](https://micropython.org) community
- [WebM Project](https://www.webmproject.org/) for libwebp
