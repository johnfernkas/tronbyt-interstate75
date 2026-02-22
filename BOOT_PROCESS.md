# Tronbyt RP2350 Boot Process

This document explains how the Tronbyt RP2350 firmware boots and executes.

## Boot Sequence

MicroPython on RP2350 follows this execution order:

1. **MicroPython startup** - Core interpreter initializes
2. **Frozen `_boot.py`** - First Python code to run (FROZEN in firmware)
3. **Filesystem `boot.py`** - Optional user customization (on filesystem)
4. **Filesystem `main.py`** - Main application (on filesystem)

## Why This Design?

### Frozen `_boot.py`
- **Always runs** - even if filesystem is corrupted
- Mounts the filesystem
- Provides error handling that prints to serial
- Launches the main application

### Filesystem `main.py`
- Can be updated without reflashing firmware
- Users can customize behavior
- Easier to debug and modify

## Files Overview

### Frozen Modules (in firmware)
| File | Purpose |
|------|---------|
| `_boot.py` | Mounts filesystem, launches main app |
| `config.py` | Default configuration values |
| `provisioning.py` | WiFi setup captive portal |

### Filesystem Modules (user-editable)
| File | Purpose |
|------|---------|
| `main.py` | Main application logic |
| `config_local.py` | User configuration (overrides defaults) |
| `boot.py` | Optional user boot code |

## Debugging Boot Issues

### Serial Console (115200 baud)
Connect to serial console to see detailed boot logs:

```bash
# Linux/Mac
picocom /dev/ttyACM0 -b 115200

# Or screen
screen /dev/ttyACM0 115200

# Windows (using PuTTY or similar)
# Connect to COM port at 115200 baud
```

### Expected Boot Output

```
============================================================
TRONBYT RP2350 BOOT
============================================================
[BOOT] _boot.py starting...
[BOOT] Mounting filesystem...
[BOOT] Filesystem mounted successfully
[BOOT] Checking for filesystem boot.py...
[BOOT] Filesystem contents: ['main.py', 'boot.py']
[BOOT] No filesystem boot.py found
[BOOT] Preparing to launch main application...
[BOOT] Found main.py on filesystem, executing...

============================================================
[MAIN] main.py starting execution
============================================================
[MAIN] Importing time...
[MAIN] Importing gc...
[MAIN] Basic imports OK
[MAIN] Checking provisioning status...
...
```

### Common Boot Issues

#### No output on serial
- Check baud rate is 115200
- Verify USB cable supports data (not charge-only)
- Try different USB port/cable

#### "Filesystem mount failed"
- First boot on new device - filesystem needs formatting
- The frozen `_boot.py` will attempt to create the filesystem
- If automatic creation fails, manually format using Thonny

#### "main.py not found"
- `main.py` should be on the filesystem root
- Upload `main.py` using Thonny, mpremote, or ampy

#### Import errors
- Check that `config_local.py` exists if you've configured WiFi
- Verify all files are in the root directory (not in subfolders)

## Provisioning Mode

If no valid configuration is found, the device enters **provisioning mode**:

1. A WiFi access point appears: `Tronbyt-Setup`
2. Connect with password: `setup1234`
3. Browse to: `http://192.168.4.1`
4. Enter your WiFi and display settings
5. Device saves config and reboots

### Manual Configuration (Alternative)

Create `config_local.py` on the filesystem:

```python
# WiFi Configuration
WIFI_SSID = "YourNetwork"
WIFI_PASSWORD = "YourPassword"

# Tronbyt Server Configuration
TRONBYT_SERVER_URL = "http://192.168.1.100:8000"
DISPLAY_ID = "my-display"

# Other settings...
DEBUG = True
DEFAULT_BRIGHTNESS = 50
```

## Firmware Structure

```
Firmware (frozen):
├── _boot.py          # Boot sequence
├── config.py         # Default config  
└── provisioning.py   # WiFi setup

Filesystem (user):
├── main.py           # Main app (auto-launched)
├── boot.py           # Optional boot code
└── config_local.py   # User config
```

## Building from Source

See `.github/workflows/build.yml` for the complete build process.

Key points:
1. Use `freeze()` not `module()` in the manifest
2. Frozen modules go in `modules/` directory
3. `main.py` can be on filesystem or frozen
4. Include `webpdec` as user C module

## Troubleshooting Checklist

- [ ] Serial console connected at 115200 baud
- [ ] Can see `[BOOT]` messages on startup
- [ ] Filesystem mounts successfully
- [ ] `main.py` exists on filesystem
- [ ] `config_local.py` has valid WiFi credentials
- [ ] WiFi network is in range
- [ ] Tronbyt server is accessible

## Getting Help

If boot issues persist:

1. Capture full serial output from power-on
2. Check for error messages in red
3. Verify firmware flashed correctly (size ~1MB)
4. Try erasing and re-flashing firmware
5. Report issue with serial output attached
