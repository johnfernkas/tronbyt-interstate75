#!/usr/bin/env python3
"""
Tronbyt RGB Bridge
Converts WebP images from Tronbyt server to raw RGB data for Interstate 75W and other HUB75 displays

Author: Ollie (AI Assistant)
Date: February 15, 2026
License: MIT
"""
from flask import Flask, Response, request, jsonify
import requests
from PIL import Image
import io
import os
import logging
from functools import lru_cache
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
TRONBYT_SERVER = os.getenv('TRONBYT_SERVER', 'http://localhost:8000')
CACHE_SIZE = int(os.getenv('CACHE_SIZE', '100'))
TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '10'))

# Cache for converted images
@lru_cache(maxsize=CACHE_SIZE)
def convert_webp_to_rgb(url: str, cache_key: str) -> tuple:
    """
    Fetch WebP from Tronbyt server and convert to raw RGB
    
    Args:
        url: URL to fetch WebP from
        cache_key: Cache key (typically ETag or content hash)
    
    Returns:
        tuple: (rgb_data, width, height, headers_dict)
    """
    logger.info(f"Fetching and converting: {url}")
    
    try:
        resp = requests.get(url, timeout=TIMEOUT, stream=True)
        resp.raise_for_status()
        
        # Decode WebP
        img = Image.open(io.BytesIO(resp.content))
        
        # Ensure RGB mode
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convert to raw RGB bytes
        rgb_data = img.tobytes('raw', 'RGB')
        
        # Extract headers
        headers = {
            'dwell_secs': resp.headers.get('Tronbyt-Dwell-Secs', '15'),
            'brightness': resp.headers.get('Tronbyt-Brightness', '50'),
        }
        
        return (rgb_data, img.width, img.height, headers)
        
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        raise


@app.route('/<device_id>/next_rgb')
def next_rgb(device_id):
    """
    Serve raw RGB data for a device
    
    GET /{device_id}/next_rgb
    
    Response:
        - Body: Raw RGB888 data (3 bytes per pixel, row-major order)
        - Headers:
            - Tronbyt-Dwell-Secs: How long to display (seconds)
            - Tronbyt-Brightness: Display brightness (0-100)
            - X-Image-Width: Image width in pixels
            - X-Image-Height: Image height in pixels
            - Content-Type: application/octet-stream
    """
    # Construct Tronbyt server URL
    tronbyt_url = f"{TRONBYT_SERVER}/{device_id}/next"
    
    try:
        # Generate cache key (simple version - could use ETag if available)
        cache_key = f"{device_id}_{hash(tronbyt_url)}"
        
        # Convert (will use cache if available)
        rgb_data, width, height, tronbyt_headers = convert_webp_to_rgb(
            tronbyt_url, 
            cache_key
        )
        
        # Build response headers
        response_headers = {
            'Tronbyt-Dwell-Secs': tronbyt_headers['dwell_secs'],
            'Tronbyt-Brightness': tronbyt_headers['brightness'],
            'X-Image-Width': str(width),
            'X-Image-Height': str(height),
            'Content-Type': 'application/octet-stream',
            'Content-Length': str(len(rgb_data)),
        }
        
        logger.info(f"Serving {width}x{height} RGB image for {device_id}")
        
        return Response(rgb_data, headers=response_headers)
        
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return Response(f"Device '{device_id}' not found on Tronbyt server", status=404)
        else:
            return Response(f"Tronbyt server error: {e}", status=502)
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return Response(f"Internal error: {str(e)}", status=500)


@app.route('/<device_id>/next_rgb565')
def next_rgb565(device_id):
    """
    Serve RGB565 data (2 bytes per pixel) - more compact for bandwidth-constrained devices
    
    RGB565 format: RRRRR GGGGGG BBBBB (5-6-5 bits)
    """
    tronbyt_url = f"{TRONBYT_SERVER}/{device_id}/next"
    
    try:
        # Generate cache key
        cache_key = f"{device_id}_rgb565_{hash(tronbyt_url)}"
        
        # Fetch and convert
        resp = requests.get(tronbyt_url, timeout=TIMEOUT, stream=True)
        resp.raise_for_status()
        
        img = Image.open(io.BytesIO(resp.content))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convert RGB888 to RGB565
        rgb888_data = img.tobytes('raw', 'RGB')
        rgb565_data = bytearray()
        
        for i in range(0, len(rgb888_data), 3):
            r = rgb888_data[i] >> 3      # 8-bit to 5-bit
            g = rgb888_data[i+1] >> 2    # 8-bit to 6-bit
            b = rgb888_data[i+2] >> 3    # 8-bit to 5-bit
            
            # Pack into 16-bit value (big-endian)
            rgb565 = (r << 11) | (g << 5) | b
            rgb565_data.append((rgb565 >> 8) & 0xFF)  # High byte
            rgb565_data.append(rgb565 & 0xFF)         # Low byte
        
        headers = {
            'Tronbyt-Dwell-Secs': resp.headers.get('Tronbyt-Dwell-Secs', '15'),
            'Tronbyt-Brightness': resp.headers.get('Tronbyt-Brightness', '50'),
            'X-Image-Width': str(img.width),
            'X-Image-Height': str(img.height),
            'X-Pixel-Format': 'RGB565',
            'Content-Type': 'application/octet-stream',
            'Content-Length': str(len(rgb565_data)),
        }
        
        logger.info(f"Serving {img.width}x{img.height} RGB565 image for {device_id}")
        
        return Response(bytes(rgb565_data), headers=headers)
        
    except Exception as e:
        logger.error(f"Error processing RGB565 request: {e}")
        return Response(f"Internal error: {str(e)}", status=500)


@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Ping Tronbyt server
        resp = requests.get(f"{TRONBYT_SERVER}/health", timeout=5)
        tronbyt_status = "ok" if resp.status_code == 200 else "error"
    except:
        tronbyt_status = "unreachable"
    
    return jsonify({
        'status': 'ok',
        'tronbyt_server': TRONBYT_SERVER,
        'tronbyt_status': tronbyt_status,
        'cache_size': CACHE_SIZE,
    })


@app.route('/')
def index():
    """Info page"""
    return """
    <h1>Tronbyt RGB Bridge</h1>
    <p>Converts WebP images from Tronbyt server to raw RGB data for Interstate 75W and other HUB75 displays.</p>
    
    <h2>Endpoints</h2>
    <ul>
        <li><code>GET /{device_id}/next_rgb</code> - Raw RGB888 data (3 bytes/pixel)</li>
        <li><code>GET /{device_id}/next_rgb565</code> - Raw RGB565 data (2 bytes/pixel)</li>
        <li><code>GET /health</code> - Health check</li>
    </ul>
    
    <h2>Configuration</h2>
    <ul>
        <li>Tronbyt Server: <code>{}</code></li>
        <li>Cache Size: {} images</li>
    </ul>
    
    <h2>Usage</h2>
    <pre>
# Example: Fetch RGB data for device "matrix_1"
curl http://localhost:8001/matrix_1/next_rgb --output frame.rgb

# View image info
curl http://localhost:8001/matrix_1/next_rgb -I
    </pre>
    """.format(TRONBYT_SERVER, CACHE_SIZE)


if __name__ == '__main__':
    port = int(os.getenv('PORT', '8001'))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Tronbyt RGB Bridge")
    logger.info(f"Tronbyt Server: {TRONBYT_SERVER}")
    logger.info(f"Listening on port: {port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
