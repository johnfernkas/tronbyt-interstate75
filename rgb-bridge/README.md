# Tronbyt RGB Bridge

Converts WebP images from Tronbyt server to raw RGB data for Interstate 75W and other HUB75 displays.

## Quick Start

### Docker (Recommended)

```bash
# Start both Tronbyt server and RGB bridge
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Python (Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Run
python app.py

# Or with environment variables
TRONBYT_SERVER=http://localhost:8000 python app.py
```

## Endpoints

- `GET /{device_id}/next_rgb` - Raw RGB888 data (3 bytes/pixel)
- `GET /{device_id}/next_rgb565` - Raw RGB565 data (2 bytes/pixel, more compact)
- `GET /health` - Health check
- `GET /` - Info page

## Configuration

Environment variables:

- `TRONBYT_SERVER` - Tronbyt server URL (default: `http://localhost:8000`)
- `PORT` - Listen port (default: `8001`)
- `CACHE_SIZE` - Number of images to cache (default: `100`)
- `REQUEST_TIMEOUT` - Request timeout in seconds (default: `10`)
- `DEBUG` - Enable debug mode (default: `false`)

## Usage Example

```bash
# Fetch RGB data
curl http://localhost:8001/matrix_1/next_rgb --output frame.rgb

# View headers
curl http://localhost:8001/matrix_1/next_rgb -I

# Output:
# Tronbyt-Dwell-Secs: 15
# Tronbyt-Brightness: 50
# X-Image-Width: 64
# X-Image-Height: 64
# Content-Type: application/octet-stream
```

## Integration with Interstate 75W

The Interstate 75W MicroPython client fetches RGB data from this bridge and renders it to the HUB75 matrix.

See `../interstate75-client/` for the client code.
