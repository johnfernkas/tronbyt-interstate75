# Architecture & Design

This document explains the architecture of the Tronbyt Interstate 75W client and compares different implementation approaches.

## Overview

The Tronbyt Interstate 75W client fetches images from a Tronbyt server and displays them on HUB75 LED matrices using the Pimoroni Interstate 75W board.

## Primary Architecture (Direct WebP)

This is the recommended approach for production use.

```
┌─────────────────────┐
│ Tronbyt Server      │
│                     │
│ ┌─────────────────┐ │
│ │ Apps (Pixlet)   │ │
│ └────────┬────────┘ │
│          │          │
│          ▼          │
│ ┌─────────────────┐ │
│ │ WebP Renderer   │ │
│ └────────┬────────┘ │
└──────────┼──────────┘
           │ HTTP
           │ GET /frame?display=X
           │ (WebP image, 2-10 KB)
           ▼
┌─────────────────────┐
│ Interstate 75W      │
│ (RP2350)            │
│                     │
│ ┌─────────────────┐ │
│ │ MicroPython     │ │
│ │ - WiFi          │ │
│ │ - HTTP Client   │ │
│ │ - Display Ctrl  │ │
│ └────────┬────────┘ │
│          │          │
│          ▼          │
│ ┌─────────────────┐ │
│ │ webpdec.so      │ │
│ │ (C Module)      │ │
│ │ - libwebp       │ │
│ │ - RGB565 conv   │ │
│ └────────┬────────┘ │
│          │          │
│          ▼          │
│ ┌─────────────────┐ │      ┌──────────────┐
│ │ HUB75 Driver    │─┼──────►  64x32 LED   │
│ │ (PicoGraphics)  │ │      │  Matrix      │
│ └─────────────────┘ │      └──────────────┘
└─────────────────────┘
```

### Advantages

- ✅ **Efficient**: WebP is compressed (2-10 KB vs 6 KB for RGB888)
- ✅ **Simple**: No intermediate services needed
- ✅ **Fast**: Decoding in C is very fast
- ✅ **Standard**: Uses Tronbyt's native WebP output

### Disadvantages

- ❌ Requires custom firmware build
- ❌ Needs libwebp integration for production
- ❌ More complex setup initially

### Components

#### 1. Tronbyt Server
- Runs Pixlet apps
- Renders to WebP format
- Serves via HTTP on `/frame` endpoint
- Provides brightness control via headers

#### 2. Interstate 75W Firmware
- **main.py**: Main application logic
  - WiFi management
  - HTTP client
  - Display control
  - Error handling
  
- **webpdec Module** (C):
  - WebP decoding using libwebp
  - RGB888 → RGB565 conversion
  - Memory-efficient buffer management

#### 3. HUB75 Display
- Controlled via Interstate75's built-in driver
- RGB565 format for memory efficiency
- Hardware refresh handled by RP2350 PIO

## Alternative Architecture (RGB Bridge)

This approach uses an intermediate service for format conversion.

```
┌─────────────────────┐
│ Tronbyt Server      │
│ (Port 8000)         │
└──────────┬──────────┘
           │ WebP
           ▼
┌─────────────────────┐
│ RGB Bridge Service  │
│ (Port 8001)         │
│                     │
│ - WebP decode       │
│ - RGB888 conversion │
│ - Caching           │
└──────────┬──────────┘
           │ HTTP
           │ GET /rgb?device=X
           │ (RGB888 raw, 6 KB)
           ▼
┌─────────────────────┐
│ Interstate 75W      │
│ (Stock MicroPython) │
│                     │
│ - Fetch RGB data    │
│ - Display directly  │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │  64x32 LED   │
    │  Matrix      │
    └──────────────┘
```

### Advantages

- ✅ **Simple firmware**: No custom build needed
- ✅ **Quick start**: Deploy in minutes
- ✅ **Flexible**: Easy to add features to bridge

### Disadvantages

- ❌ Extra service to run (Docker container)
- ❌ More network traffic (uncompressed RGB)
- ❌ Higher latency
- ❌ Additional point of failure

### When to Use

The RGB Bridge approach is useful for:
- Quick prototyping
- Testing without custom firmware
- Network setups where you control the server
- Learning/educational purposes

The bridge service code is in the `rgb-bridge/` directory.

## Data Flow

### Direct WebP Flow

1. **Tronbyt server** renders Pixlet app to WebP
2. **Interstate 75W** requests frame via HTTP:
   ```
   GET /frame?display=my-display
   ```
3. **Server** responds with:
   - WebP image data (body)
   - `X-Brightness: 75` (header)
4. **webpdec module** decodes WebP to RGB565
5. **PicoGraphics** displays RGB565 data on matrix
6. **Brightness** adjusted based on header
7. Repeat every `UPDATE_INTERVAL` seconds

### RGB Bridge Flow

1. **Tronbyt server** renders Pixlet app to WebP
2. **RGB bridge** fetches WebP from Tronbyt
3. **RGB bridge** decodes to RGB888
4. **RGB bridge** caches the result
5. **Interstate 75W** requests RGB data:
   ```
   GET /rgb?device=my-display
   ```
6. **Bridge** responds with raw RGB888 bytes
7. **Interstate 75W** displays RGB directly
8. Repeat every update interval

## Image Formats

### WebP
- **Size**: 2-10 KB for 64x32 @ lossy
- **Compression**: Lossy or lossless
- **Pros**: Small, efficient, widely supported
- **Cons**: Requires decoder

### RGB888 (Raw)
- **Size**: width × height × 3 bytes = 6,144 bytes for 64x32
- **Format**: R, G, B per pixel (3 bytes)
- **Pros**: No decoding needed
- **Cons**: Larger network payload

### RGB565 (Internal)
- **Size**: width × height × 2 bytes = 4,096 bytes for 64x32
- **Format**: 16-bit color (5R, 6G, 5B)
- **Pros**: Memory efficient, good color depth
- **Cons**: Slight color loss vs RGB888

## Memory Layout (RP2350)

The RP2350 has **520 KB SRAM**:

```
┌─────────────────────────────────┐ 0x20000000
│                                 │
│   MicroPython Runtime           │ ~200 KB
│   (interpreter, modules, etc)   │
│                                 │
├─────────────────────────────────┤
│                                 │
│   Application Heap              │ ~250 KB
│   - Variables                   │
│   - Buffers                     │
│   - HTTP data                   │
│                                 │
├─────────────────────────────────┤
│                                 │
│   Frame Buffer (RGB565)         │ 4 KB
│   64 × 32 × 2 = 4096 bytes      │
│                                 │
├─────────────────────────────────┤
│                                 │
│   WebP Decode Buffer            │ ~10-20 KB
│   (temporary)                   │
│                                 │
├─────────────────────────────────┤
│                                 │
│   Stack & System                │ ~50 KB
│                                 │
└─────────────────────────────────┘ 0x20080000
```

Total usage: ~300-320 KB, leaving ~200 KB free for headroom.

## Performance Considerations

### Network Bandwidth

**Direct WebP:**
- WebP download: 2-10 KB @ 1 Hz = 2-10 KB/s
- Total: **~10 KB/s**

**RGB Bridge:**
- RGB888 download: 6 KB @ 1 Hz = 6 KB/s
- Total: **~6 KB/s**

Winner: Direct WebP (less data overall due to compression)

### Latency

**Direct WebP:**
- HTTP request: ~50 ms
- WebP decode: ~20-50 ms
- Display: ~5 ms
- **Total: ~75-105 ms**

**RGB Bridge:**
- HTTP request: ~50 ms
- Display: ~5 ms
- **Total: ~55 ms** (but bridge adds latency)

### CPU Usage

**Direct WebP:**
- Decoding: Medium (C code, optimized)
- Display: Low (hardware PIO)

**RGB Bridge:**
- Decoding: None (done on server)
- Display: Low (hardware PIO)

## Scalability

### Number of Displays

**Direct WebP:**
- Each display connects directly to Tronbyt
- Scales with Tronbyt server capacity
- No bottleneck

**RGB Bridge:**
- Bridge becomes bottleneck
- One bridge instance per ~10-20 displays
- More complex deployment

## Future Enhancements

### Planned Features

1. **OTA Updates**: Download firmware over WiFi
2. **Multi-size Support**: Auto-detect panel size
3. **Image Caching**: Cache last frame to show on error
4. **FPS Counter**: Display performance metrics
5. **Web Config**: Configure via web interface
6. **MQTT Support**: Alternative to HTTP polling

### libwebp Integration

The current WebP decoder is a placeholder. For production:

1. Clone libwebp into `webpdec/`
2. Update `micropython.mk` to build libwebp sources
3. Use `webpdec_full.c` implementation
4. Rebuild firmware

See [BUILD.md](BUILD.md) for details.

## Comparison Summary

| Feature | Direct WebP | RGB Bridge |
|---------|------------|------------|
| Setup Complexity | High | Low |
| Network Efficiency | High | Medium |
| Latency | Medium | Medium |
| Firmware Build | Required | Not Required |
| Extra Services | None | Docker Container |
| Scalability | Excellent | Good |
| Production Ready | Yes (with libwebp) | Yes |
| Recommended For | Production | Prototyping |

## Recommendations

- **For Production**: Use Direct WebP approach
- **For Quick Testing**: Use RGB Bridge approach
- **For Development**: Use RGB Bridge initially, migrate to Direct WebP

Both implementations are included in this repository.
