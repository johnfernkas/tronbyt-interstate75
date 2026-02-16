"""
Tronbyt RP2350 Client
Fetches and displays WebP images from a Tronbyt server on HUB75 LED matrices.

This firmware is designed to work with any RP2350 board with:
- WiFi connectivity
- HUB75 LED matrix interface

Tested on:
- Pimoroni Interstate 75W (RP2350)
"""

import time
import network
import urequests as requests
import gc

# Try to import local config, fall back to default
try:
    from config_local import *
except ImportError:
    from config import *

# Try to import the WebP decoder module
try:
    import webpdec
    WEBP_AVAILABLE = True
except ImportError:
    print("WARNING: webpdec module not found! WebP decoding will fail.")
    WEBP_AVAILABLE = False

# Display driver imports - try different options
try:
    # Pimoroni Interstate 75
    from interstate75 import Interstate75
    from picographics import PicoGraphics
    BOARD_TYPE = "interstate75"
except ImportError:
    try:
        # Generic HUB75 via framebuffer
        import framebuf
        BOARD_TYPE = "generic"
    except ImportError:
        BOARD_TYPE = "unknown"
        print("WARNING: No display driver found!")


class TronbytClient:
    """Client for connecting to Tronbyt server and displaying frames."""
    
    def __init__(self):
        """Initialize the Tronbyt client."""
        self.display_id = DISPLAY_ID
        self.server_url = TRONBYT_SERVER_URL.rstrip('/')
        self.current_brightness = DEFAULT_BRIGHTNESS
        self.width = DISPLAY_WIDTH
        self.height = DISPLAY_HEIGHT
        
        # Initialize display based on board type
        self._init_display()
        
        # Set initial brightness
        self.set_brightness(DEFAULT_BRIGHTNESS)
        
        # Show startup message
        self.show_message("Tronbyt", (0, 255, 0))
        time.sleep(1)
        
    def _init_display(self):
        """Initialize display driver based on board type."""
        global BOARD_TYPE
        
        if BOARD_TYPE == "interstate75":
            print("Initializing Interstate 75 display...")
            try:
                # Try 64x64 first, fall back to 64x32
                if self.height == 64:
                    from interstate75 import DISPLAY_INTERSTATE75_64X64
                    display_type = DISPLAY_INTERSTATE75_64X64
                else:
                    from interstate75 import DISPLAY_INTERSTATE75_64X32
                    display_type = DISPLAY_INTERSTATE75_64X32
                
                self.i75 = Interstate75(display=display_type)
                self.graphics = self.i75.display
                self._display_type = "interstate75"
            except Exception as e:
                print(f"Failed to init Interstate 75: {e}")
                raise
                
        elif BOARD_TYPE == "generic":
            print("Initializing generic framebuffer display...")
            # For generic RP2350 boards, you'd implement HUB75 driver here
            # This is a placeholder - actual implementation depends on hardware
            self._display_type = "generic"
            # TODO: Implement generic HUB75 driver
            raise NotImplementedError("Generic HUB75 driver not yet implemented")
            
        else:
            raise RuntimeError(f"Unknown board type: {BOARD_TYPE}")
        
        print(f"Display initialized: {self.width}x{self.height}")
        
    def show_message(self, text, color=(255, 255, 255)):
        """Display a text message on the matrix."""
        if self._display_type == "interstate75":
            self.graphics.set_pen(self.graphics.create_pen(0, 0, 0))
            self.graphics.clear()
            
            # Center text
            text_x = max(2, (self.width - len(text) * 6) // 2)
            text_y = max(10, (self.height - 8) // 2)
            
            self.graphics.set_pen(self.graphics.create_pen(*color))
            self.graphics.text(text, text_x, text_y, scale=1)
            self.i75.update()
        
    def set_brightness(self, brightness):
        """Set display brightness (0-100)."""
        brightness = max(0, min(100, brightness))
        self.current_brightness = brightness
        
        if self._display_type == "interstate75":
            if hasattr(self.i75, 'set_brightness'):
                self.i75.set_brightness(brightness / 100.0)
        
        if DEBUG:
            print(f"Brightness set to {brightness}%")
    
    def connect_wifi(self):
        """Connect to WiFi network."""
        print(f"Connecting to WiFi: {WIFI_SSID}")
        self.show_message("WiFi...", (255, 255, 0))
        
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Wait for connection
        max_wait = 20
        while max_wait > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            max_wait -= 1
            print('Waiting for connection...')
            time.sleep(1)
        
        # Check connection
        if wlan.status() != 3:
            self.show_message("WiFi Fail", (255, 0, 0))
            raise RuntimeError('WiFi connection failed')
        else:
            status = wlan.ifconfig()
            print(f'Connected! IP: {status[0]}')
            self.show_message("WiFi OK", (0, 255, 0))
            time.sleep(1)
            return status[0]
    
    def fetch_frame(self):
        """Fetch a frame from the Tronbyt server."""
        url = f"{self.server_url}/next"
        
        if DEBUG:
            print(f"Fetching frame from: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # Get metadata from headers
                dwell_secs = int(response.headers.get('Tronbyt-Dwell-Secs', '15'))
                brightness = int(response.headers.get('Tronbyt-Brightness', '-1'))
                
                if brightness >= 0:
                    self.set_brightness(brightness)
                
                content_type = response.headers.get('Content-Type', '')
                
                if DEBUG:
                    print(f"Got frame: {len(response.content)} bytes, dwell={dwell_secs}s")
                
                return response.content, dwell_secs, content_type
            else:
                print(f"Error: HTTP {response.status_code}")
                return None, 15, None
                
        except Exception as e:
            print(f"Error fetching frame: {e}")
            return None, 15, None
    
    def decode_and_display(self, webp_data):
        """Decode WebP data and display on matrix."""
        if not WEBP_AVAILABLE:
            self.show_message("No webpdec", (255, 0, 0))
            return False
        
        try:
            if DEBUG:
                print(f"Decoding WebP: {len(webp_data)} bytes")
            
            # Decode WebP to RGB565
            rgb565_data = webpdec.decode(webp_data, self.width, self.height)
            
            if rgb565_data is None or len(rgb565_data) == 0:
                print("WebP decode failed")
                return False
            
            # Display on matrix
            self._display_rgb565(rgb565_data)
            return True
            
        except Exception as e:
            print(f"Error decoding/displaying: {e}")
            return False
    
    def _display_rgb565(self, rgb565_data):
        """Display RGB565 data on the matrix."""
        if self._display_type == "interstate75":
            # Interstate 75 uses 16-bit RGB565
            for y in range(self.height):
                for x in range(self.width):
                    idx = (y * self.width + x) * 2
                    if idx + 1 < len(rgb565_data):
                        # RGB565 is little-endian
                        pixel = rgb565_data[idx] | (rgb565_data[idx + 1] << 8)
                        
                        # Extract RGB components
                        r = ((pixel >> 11) & 0x1F) << 3
                        g = ((pixel >> 5) & 0x3F) << 2
                        b = (pixel & 0x1F) << 3
                        
                        self.graphics.set_pen(self.graphics.create_pen(r, g, b))
                        self.graphics.pixel(x, y)
            
            self.i75.update()
            
        if DEBUG:
            print(f"Displayed frame: {len(rgb565_data)} bytes")
    
    def run(self):
        """Main loop - fetch and display frames."""
        print("\n" + "="*50)
        print("Tronbyt RP2350 Client Starting")
        print("="*50)
        
        if not WEBP_AVAILABLE:
            print("ERROR: webpdec module not available!")
            self.show_message("No webpdec!", (255, 0, 0))
            while True:
                time.sleep(1)
        
        # Connect to WiFi
        try:
            self.connect_wifi()
        except Exception as e:
            print(f"WiFi connection failed: {e}")
            self.show_message("WiFi Error", (255, 0, 0))
            time.sleep(5)
            # Retry
            return self.run()
        
        print(f"\nConnecting to Tronbyt server: {self.server_url}")
        print(f"Display ID: {self.display_id}")
        print("="*50 + "\n")
        
        # Main loop
        while True:
            try:
                # Fetch frame
                frame_data, dwell_secs, content_type = self.fetch_frame()
                
                if frame_data:
                    # Decode and display
                    if self.decode_and_display(frame_data):
                        if DEBUG:
                            print(f"Frame displayed, sleeping for {dwell_secs}s")
                    else:
                        self.show_message("Decode Error", (255, 0, 0))
                else:
                    self.show_message("No Frame", (255, 128, 0))
                
                # Wait before next fetch
                time.sleep(dwell_secs)
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                self.show_message("Error", (255, 0, 0))
                time.sleep(5)
            
            # Force garbage collection
            gc.collect()


# Entry point
if __name__ == "__main__":
    client = TronbytClient()
    client.run()
