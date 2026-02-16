# Building the Firmware

This guide explains how to build custom MicroPython firmware with the `webpdec` module for the Interstate 75W.

## Prerequisites

### Required Software

- **Git** - for cloning repositories
- **Python 3** - for build scripts
- **GCC ARM Toolchain** - for cross-compilation
- **CMake** - build system
- **mpremote** or **ampy** - for deploying files

### Installing Prerequisites

#### macOS
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required tools
brew install gcc-arm-embedded cmake python3

# Install mpremote
pip3 install mpremote
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install git cmake gcc-arm-none-eabi python3 python3-pip

# Install mpremote
pip3 install mpremote
```

#### Windows
Use WSL2 (Windows Subsystem for Linux) and follow the Linux instructions.

## Quick Build

Use the provided Makefile:

```bash
# Setup MicroPython (first time only)
make setup

# Build firmware with webpdec module
make firmware

# Flash to device
make flash

# Deploy Python files
make deploy

# Or do everything at once
make all
```

## Manual Build Process

If you prefer to build manually:

### 1. Clone MicroPython

```bash
git clone https://github.com/micropython/micropython.git
cd micropython
git submodule update --init
```

### 2. Build mpy-cross

```bash
cd mpy-cross
make
cd ..
```

### 3. Copy Module to MicroPython

```bash
# From the tronbyt-interstate75 directory
cp -r webpdec /path/to/micropython/ports/rp2/modules/
```

### 4. Build Firmware

```bash
cd /path/to/micropython/ports/rp2

# Build with the webpdec module
make BOARD=PIMORONI_INTERSTATE75W \
     USER_C_MODULES=/path/to/tronbyt-interstate75/webpdec/micropython.mk
```

The firmware will be in:
```
build-PIMORONI_INTERSTATE75W/firmware.uf2
```

### 5. Flash Firmware

1. Connect Interstate 75W to your computer
2. Hold **BOOT** button and tap **RST**
3. A drive named **RP2350** will appear
4. Copy `firmware.uf2` to the drive
5. The device will reboot automatically

## Building with libwebp

For production use with real WebP decoding:

### 1. Clone libwebp

```bash
cd webpdec/
git clone https://chromium.googlesource.com/webm/libwebp
cd libwebp
git checkout v1.3.2  # Use a stable release
```

### 2. Update micropython.mk

Edit `webpdec/micropython.mk` and uncomment the libwebp sections:

```makefile
# Add libwebp include
CFLAGS_USERMOD += -I$(WEBPDEC_MOD_DIR)/libwebp/src

# Add libwebp sources
SRC_USERMOD += $(wildcard $(WEBPDEC_MOD_DIR)/libwebp/src/dec/*.c)
SRC_USERMOD += $(wildcard $(WEBPDEC_MOD_DIR)/libwebp/src/dsp/*.c)
SRC_USERMOD += $(wildcard $(WEBPDEC_MOD_DIR)/libwebp/src/utils/*.c)
```

### 3. Use Full Implementation

```bash
cd webpdec/
mv webpdec.c webpdec_placeholder.c
mv webpdec_full.c webpdec.c
```

### 4. Rebuild

```bash
make clean
make firmware
```

## Troubleshooting

### "No such file or directory" errors

Make sure you've run `git submodule update --init` in the MicroPython directory.

### ARM toolchain not found

Install the ARM GCC toolchain:
- macOS: `brew install gcc-arm-embedded`
- Linux: `sudo apt install gcc-arm-none-eabi`

### Build fails with libwebp

Try these solutions:

1. **Use a specific libwebp version:**
   ```bash
   cd webpdec/libwebp
   git checkout v1.3.2
   ```

2. **Reduce libwebp features** - edit `micropython.mk` to only include essential files

3. **Check memory** - libwebp can be large; you may need to disable other modules

### Device not recognized

- **macOS**: The RP2350 drive should appear in `/Volumes/`
- **Linux**: Check `/media/$USER/RP2350/` or use `lsblk` to find it
- **Windows**: Should appear as a new drive letter

### Build succeeds but module not found

Make sure:
1. The module was copied to `micropython/ports/rp2/modules/webpdec/`
2. You specified `USER_C_MODULES=` in the make command
3. The firmware.uf2 you flashed is the one you just built

## Optimizing Build Size

If the firmware is too large:

### Disable Unused Modules

Edit `micropython/ports/rp2/mpconfigboard.h` and disable modules:

```c
#define MICROPY_PY_USSL (0)
#define MICROPY_PY_BTREE (0)
#define MICROPY_PY_FRAMEBUF (0)
```

### Use Release Build

```bash
make BOARD=PIMORONI_INTERSTATE75W \
     USER_C_MODULES=/path/to/webpdec/micropython.mk \
     CFLAGS_EXTRA="-Os"  # Optimize for size
```

### Minimal libwebp

Only include the decoder, not encoder:

```makefile
# In micropython.mk, only add decoder files
SRC_USERMOD += $(WEBPDEC_MOD_DIR)/libwebp/src/dec/decode.c
SRC_USERMOD += $(WEBPDEC_MOD_DIR)/libwebp/src/dec/vp8.c
# ... (only what's needed)
```

## Testing the Build

After flashing, test the module:

```bash
# Connect to device
mpremote repl

# In the REPL:
>>> import webpdec
>>> webpdec.decode(b'\x00' * 100, 64, 32)
```

If you see a bytearray output, the module is working!

## Continuous Integration

The repository includes GitHub Actions for automated builds (see `.github/workflows/build.yml`).

## Next Steps

- [Deploy the firmware](../README.md#quick-start)
- [Configure your settings](../README.md#configuration)
- [Connect to Tronbyt server](../README.md#tronbyt-server-setup)
