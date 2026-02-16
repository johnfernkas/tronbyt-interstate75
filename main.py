"""
Tronbyt Interstate 75W Client
Fetches and displays WebP images from a Tronbyt server on a HUB75 LED matrix.
"""

import time
import network
import urequests as requests
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_64X32
from picographics import PicoGraphics, DISPLAY_INTERSTATE75_64X32 as DISPLAY_MODE
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


class TronbytClient:
    """Client for connecting to Tronbyt server and displaying frames."""
    
    def __init__(self):
        """Initialize the Tronbyt client."""
        self.display_id = DISPLAY_ID
        self.server_url = TRONBYT_SERVER_URL.rstrip('/')
        self.current_brightness = DEFAULT_BRIGHTNESS
        
        # Initialize Interstate 75
        print("Initializing Interstate 75...")
        self.i75 = Interstate75(display=DISPLAY_INTERSTATE75_64X32)
        self.graphics = self.i75.display
        
        # Set initial brightness
        self.set_brightness(DEFAULT_BRIGHTNESS)
        
        # Show startup message
        self.show_message("Starting...")
        
    def show_message(self, text, color=(255, 255, 255)):
        """Display a text message on the matrix."""
        self.graphics.set_pen(self.graphics.create_pen(0, 0, 0))
        self.graphics.clear()
        self.graphics.set_pen(self.graphics.create_pen(*color))
        self.graphics.text(text, 2, 12, scale=1)
        self.i75.update()
        
    def set_brightness(self, brightness):
        """Set display brightness (0-100)."""
        # Interstate 75 brightness is 0.0-1.0
        brightness = max(0, min(100, brightness))
        self.current_brightness = brightness
        # Note: Interstate75 may not have direct brightness control
        # This depends on the specific firmware version
        # Some versions use self.i75.set_brightness(brightness / 100.0)
        if hasattr(self.i75, 'set_brightness'):
            self.i75.set_brightness(brightness / 100.0)
        if DEBUG:
            print(f"Brightness set to {brightness}%")
    
    def connect_wifi(self):
        """Connect to WiFi network."""
        print(f"Connecting to WiFi: {WIFI_SSID}")
        self.show_message("WiFi...")
        
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
        url = f"{self.server_url}/frame?display={self.display_id}"
        
        if DEBUG:
            print(f"Fetching frame from: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # Check for brightness header
                brightness_header = response.headers.get('X-Brightness') or \
                                   response.headers.get('Tronbyt-Brightness')
                if brightness_header:
                    try:
                        new_brightness = int(brightness_header)
                        if new_brightness != self.current_brightness:
                            self.set_brightness(new_brightness)
                    except ValueError:
                        pass
                
                # Get WebP data
                webp_data = response.content
                response.close()
                
                if DEBUG:
                    print(f"Received {len(webp_data)} bytes of WebP data")
                
                return webp_data
            else:
                print(f"HTTP error: {response.status_code}")
                response.close()
                return None
                
        except Exception as e:
            print(f"Error fetching frame: {e}")
            return None
    
    def decode_and_display(self, webp_data):
        """Decode WebP data and display it on the matrix."""
        if not WEBP_AVAILABLE:
            print("Cannot decode: webpdec module not available")
            return False
        
        try:
            if DEBUG:
                print("Decoding WebP...")
            
            # Decode WebP to RGB565
            # webpdec.decode(data, width, height) -> bytearray of RGB565
            rgb_data = webpdec.decode(webp_data, DISPLAY_WIDTH, DISPLAY_HEIGHT)
            
            if rgb_data is None:
                print("WebP decode returned None")
                return False
            
            if DEBUG:
                print(f"Decoded to {len(rgb_data)} bytes")
            
            # Display the RGB565 data
            # This assumes PicoGraphics can accept RGB565 data directly
            # May need adjustment based on actual Interstate75 API
            self.display_rgb565(rgb_data)
            
            self.i75.update()
            
            return True
            
        except Exception as e:
            print(f"Error decoding/displaying: {e}")
            import sys
            sys.print_exception(e)
            return False
    
    def display_rgb565(self, rgb_data):
        """Display RGB565 data on the matrix."""
        # Convert RGB565 to individual pixels
        # RGB565 format: RRRRR GGGGGG BBBBB (2 bytes per pixel)
        
        for y in range(DISPLAY_HEIGHT):
            for x in range(DISPLAY_WIDTH):
                pixel_idx = (y * DISPLAY_WIDTH + x) * 2
                
                # Get RGB565 value (little-endian)
                rgb565 = rgb_data[pixel_idx] | (rgb_data[pixel_idx + 1] << 8)
                
                # Extract RGB components
                r = ((rgb565 >> 11) & 0x1F) << 3  # 5 bits -> 8 bits
                g = ((rgb565 >> 5) & 0x3F) << 2   # 6 bits -> 8 bits
                b = (rgb565 & 0x1F) << 3          # 5 bits -> 8 bits
                
                # Set pixel
                pen = self.graphics.create_pen(r, g, b)
                self.graphics.set_pen(pen)
                self.graphics.pixel(x, y)
    
    def run(self):
        """Main run loop."""
        print("Tronbyt Interstate 75W Client Starting...")
        print(f"Display ID: {self.display_id}")
        print(f"Server: {self.server_url}")
        
        # Connect to WiFi
        try:
            self.connect_wifi()
        except Exception as e:
            print(f"WiFi connection failed: {e}")
            self.show_message("No WiFi", (255, 0, 0))
            return
        
        # Show ready message
        self.show_message("Ready", (0, 255, 0))
        time.sleep(1)
        
        # Main loop
        error_count = 0
        while True:
            try:
                # Fetch frame
                webp_data = self.fetch_frame()
                
                if webp_data:
                    # Decode and display
                    if self.decode_and_display(webp_data):
                        error_count = 0  # Reset error count on success
                    else:
                        error_count += 1
                else:
                    error_count += 1
                
                # Handle errors
                if error_count >= MAX_RETRIES:
                    print(f"Too many errors ({error_count}), showing error message")
                    self.show_message("Error", (255, 0, 0))
                    time.sleep(5)
                    error_count = 0  # Reset
                
                # Clean up memory
                gc.collect()
                
                # Wait before next update
                time.sleep(UPDATE_INTERVAL)
                
            except KeyboardInterrupt:
                print("\nStopping...")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                import sys
                sys.print_exception(e)
                error_count += 1
                time.sleep(RETRY_DELAY)


# Entry point
if __name__ == "__main__":
    client = TronbytClient()
    client.run()
