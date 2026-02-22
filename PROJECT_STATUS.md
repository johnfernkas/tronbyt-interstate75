# Tronbyt RP2350 Firmware - Project Status

**Date:** 2026-02-22
**Status:** ABANDONED - Moving to MatrixPortal S3

## What Was Built

### Hardware
- **Pimoroni Interstate 75W (RP2350)** + 64x32 HUB75 LED matrix
- Custom MicroPython firmware with WebP decoder

### Firmware Components Created
1. **`_boot.py`** - Frozen boot module with serial output and filesystem mounting
2. **`main.py`** - Tronbyt client with HTTP fetch, display control, debug logging
3. **`provisioning.py`** - WiFi captive portal for device configuration
4. **`config.py`** - Default configuration template
5. **`webpdec/`** - C module for WebP image decoding
6. **`.github/workflows/build.yml`** - CI build for frozen firmware

### Features Working
- ✅ WiFi connection with debug output
- ✅ LED matrix display via Interstate75 driver
- ✅ WebP decoding via custom C module
- ✅ Provisioning mode (captive portal)
- ✅ HTTP fetch with socket implementation (not urequests)
- ✅ Serial debug logging at every stage

### Features NOT Working
- ❌ **Tronbyt API authentication** - Server returns 303 → /auth/login for all requests
- ❌ **No valid /next endpoint** - API appears to use push model, not pull model

## Root Cause

The Tronbyt server API uses a **push model** (server sends images to device) not a **pull model** (device requests images from server). The `/v0/devices/{id}/next` endpoint either:
1. Doesn't exist for GET requests
2. Requires different authentication
3. Only works with official Tronbyt device firmware

Attempts:
- `GET /v0/devices/{id}/next` → 303 redirect to /auth/login
- Various alternate endpoints → Same 303 redirect
- curl from desktop → Same 303 redirect (not a firmware bug)

## Decision

Moving to **Adafruit MatrixPortal S3** with official Tronbyt firmware:
- Out-of-box Tronbyt support
- No custom firmware maintenance
- Community maintained
- Same LED matrix output
- Similar price (~$35 vs ~$30)

## Repositories

- `github.com/johnfernkas/tronbyt-rp2350` - Main firmware repo
- Contains all working code up to commit `112d2ac`
- **Will be deleted** - not worth maintaining custom firmware

## Lessons Learned

1. **Verify API before building** - Assumed pull model, Tronbyt uses push
2. **Time vs cost tradeoff** - 4+ hours on firmware vs $5 hardware swap
3. **Community solutions win** - Custom firmware = permanent maintenance burden

## Hardware Swap

### From:
- Pimoroni Interstate 75W ($25)
- HUB75 LED matrix (already owned)
- Custom MicroPython firmware (4+ hours dev time)

### To:
- Adafruit MatrixPortal S3 ($35)
- Same HUB75 LED matrix
- Official Tronbyt firmware (0 hours dev time)

**Net cost:** $10, **Net time saved:** Infinite (no maintenance)

## Archive Notes

This project successfully built:
- Working MicroPython firmware for RP2350
- Custom WebP decoder module
- HTTP client without urequests (socket-based)
- WiFi provisioning system
- Comprehensive debug logging

But the fundamental architecture mismatch (pull vs push API) makes it unsustainable for production use.

**Recommendation:** Delete repos, use MatrixPortal S3, move on to actually displaying things.

---
*End of project. Onward to the MatrixPortal S3.*
