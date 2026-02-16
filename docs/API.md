# API Documentation

## webpdec Module

The `webpdec` module provides WebP image decoding functionality.

### Functions

#### `decode(data, width, height)`

Decode a WebP image to RGB565 format.

**Parameters:**
- `data` (bytes): WebP image data
- `width` (int): Expected image width (1-256)
- `height` (int): Expected image height (1-256)

**Returns:**
- `bytearray`: RGB565 pixel data (width × height × 2 bytes)

**Raises:**
- `ValueError`: If dimensions are invalid or decoding fails
- `MemoryError`: If unable to allocate decode buffer

**Example:**
```python
import webpdec

# Read WebP file
with open('image.webp', 'rb') as f:
    webp_data = f.read()

# Decode to RGB565
rgb565 = webpdec.decode(webp_data, 64, 32)

# rgb565 is now a bytearray of 4096 bytes (64*32*2)
```

#### `version()`

Get the module version string.

**Returns:**
- `str`: Version string (e.g., "0.1.0")

**Example:**
```python
import webpdec
print(webpdec.version())  # "0.1.0"
```

### RGB565 Format

The output is in RGB565 format (little-endian):
- **5 bits** for Red (most significant)
- **6 bits** for Green
- **5 bits** for Blue (least significant)

Each pixel is **2 bytes** (16 bits):
```
Byte 0: [G2 G1 G0 B4 B3 B2 B1 B0]
Byte 1: [R4 R3 R2 R1 R0 G5 G4 G3]
```

**Converting RGB565 to RGB888:**
```python
def rgb565_to_rgb888(rgb565_data, width, height):
    rgb888 = bytearray(width * height * 3)
    
    for i in range(width * height):
        # Read RGB565 (little-endian)
        rgb565 = rgb565_data[i*2] | (rgb565_data[i*2+1] << 8)
        
        # Extract components
        r = ((rgb565 >> 11) & 0x1F) << 3  # 5 bits -> 8 bits
        g = ((rgb565 >> 5) & 0x3F) << 2   # 6 bits -> 8 bits  
        b = (rgb565 & 0x1F) << 3          # 5 bits -> 8 bits
        
        # Write RGB888
        rgb888[i*3 + 0] = r
        rgb888[i*3 + 1] = g
        rgb888[i*3 + 2] = b
    
    return rgb888
```

## TronbytClient Class

### Constructor

#### `TronbytClient()`

Initialize the Tronbyt client.

**Example:**
```python
from main import TronbytClient

client = TronbytClient()
```

### Methods

#### `connect_wifi()`

Connect to WiFi network using credentials from config.

**Returns:**
- `str`: IP address assigned to the device

**Raises:**
- `RuntimeError`: If WiFi connection fails

**Example:**
```python
ip = client.connect_wifi()
print(f"Connected with IP: {ip}")
```

#### `fetch_frame()`

Fetch a frame from the Tronbyt server.

**Returns:**
- `bytes`: WebP image data, or `None` on error

**Example:**
```python
webp_data = client.fetch_frame()
if webp_data:
    print(f"Received {len(webp_data)} bytes")
```

#### `decode_and_display(webp_data)`

Decode WebP data and display it on the matrix.

**Parameters:**
- `webp_data` (bytes): WebP image data

**Returns:**
- `bool`: `True` if successful, `False` on error

**Example:**
```python
success = client.decode_and_display(webp_data)
```

#### `set_brightness(brightness)`

Set display brightness.

**Parameters:**
- `brightness` (int): Brightness value (0-100)

**Example:**
```python
client.set_brightness(75)  # 75% brightness
```

#### `show_message(text, color=(255, 255, 255))`

Display a text message on the matrix.

**Parameters:**
- `text` (str): Message to display
- `color` (tuple): RGB color tuple (default: white)

**Example:**
```python
client.show_message("Hello!", (0, 255, 0))  # Green text
```

#### `run()`

Main run loop. Connects to WiFi and continuously fetches/displays frames.

**Example:**
```python
client.run()  # Runs until interrupted
```

## Configuration

All configuration is done via `config.py` or `config_local.py`. See [Configuration](../README.md#configuration) in the main README.

## Tronbyt Server API

The client interacts with the Tronbyt server using HTTP.

### Fetch Frame

**Endpoint:** `GET /frame`

**Query Parameters:**
- `display` (string): Display identifier

**Example Request:**
```
GET /frame?display=interstate75-001 HTTP/1.1
Host: 192.168.1.100:8000
```

**Response Headers:**
- `X-Brightness` or `Tronbyt-Brightness` (integer, 0-100): Display brightness
- `Content-Type`: `image/webp`

**Response Body:**
- WebP image data (binary)

**Example:**
```python
import urequests as requests

response = requests.get(
    "http://192.168.1.100:8000/frame?display=my-display"
)

brightness = int(response.headers.get('X-Brightness', 50))
webp_data = response.content
```

## Interstate75 Display API

The client uses Pimoroni's Interstate75 library. Key objects:

### Interstate75 Object

```python
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_64X32

i75 = Interstate75(display=DISPLAY_INTERSTATE75_64X32)
```

### Graphics Object

The `display` property provides a PicoGraphics instance:

```python
graphics = i75.display

# Clear screen
graphics.set_pen(graphics.create_pen(0, 0, 0))
graphics.clear()

# Draw pixel
pen = graphics.create_pen(255, 0, 0)
graphics.set_pen(pen)
graphics.pixel(x, y)

# Draw text
graphics.text("Hello", 0, 0, scale=1)

# Update display
i75.update()
```

For full documentation, see [Pimoroni's Interstate75 docs](https://github.com/pimoroni/interstate75/blob/main/docs/README.md).

## Memory Management

MicroPython includes automatic garbage collection. The client calls `gc.collect()` after each frame to free memory.

**Manual garbage collection:**
```python
import gc

gc.collect()  # Run garbage collection
print(gc.mem_free())  # Check free memory
```

## Error Handling

The client includes error handling for common issues:

- **Network errors**: Automatically retried up to `MAX_RETRIES`
- **Decode errors**: Logged and retried
- **Memory errors**: Application will show "Error" message

**Custom error handling:**
```python
try:
    client.run()
except KeyboardInterrupt:
    print("Stopped by user")
except Exception as e:
    print(f"Error: {e}")
    import sys
    sys.print_exception(e)
```
