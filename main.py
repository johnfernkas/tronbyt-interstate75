"""
Tronbyt RP2350 Client
Fetches and displays WebP images from a Tronbyt server on HUB75 LED matrices.

This firmware is designed to work with any RP2350 board with:
- WiFi connectivity
- HUB75 LED matrix interface

Tested on:
- Pimoroni Interstate 75W (RP2350)
"""

# EARLY DEBUG - Print BEFORE any imports
import sys
print("\n" + "="*60)
print("[MAIN] main.py starting execution")
print("="*60)

# Track import progress
print("[MAIN] Importing time...")
import time
print("[MAIN] Importing gc...")
import gc
print("[MAIN] Basic imports OK")

# Check if we need provisioning before importing config
print("[MAIN] Checking provisioning status...")
_needs_provisioning = False
try:
    print("[MAIN] Attempting to import config_local...")
    import config_local
    print("[MAIN] config_local imported successfully")
    # Config exists, check if it has placeholder values
    if (not hasattr(config_local, 'WIFI_SSID') or 
        not config_local.WIFI_SSID or 
        config_local.WIFI_SSID == "YourWiFiSSID"):
        print("[MAIN] Config has placeholder values, provisioning needed")
        _needs_provisioning = True
    else:
        print(f"[MAIN] Config found, WiFi SSID: {config_local.WIFI_SSID}")
except ImportError as e:
    print(f"[MAIN] config_local not found: {e}")
    _needs_provisioning = True
except Exception as e:
    print(f"[MAIN] Error loading config_local: {e}")
    _needs_provisioning = True

# If provisioning needed, start provisioning server
if _needs_provisioning:
    print("=" * 60)
    print("TRONBYT PROVISIONING MODE")
    print("=" * 60)
    print("No valid configuration found.")
    print("Starting provisioning access point...")
    try:
        print("[MAIN] Importing provisioning module...")
        import provisioning
        print("[MAIN] Starting provisioning server...")
        provisioning.start_provisioning()
        print("[MAIN] Provisioning server exited")
    except Exception as e:
        print(f"[MAIN] Provisioning failed: {e}")
        sys.print_exception(e)
        # Fall through to allow manual config editing via USB
    # If provisioning exits without reboot, continue to normal mode
    # to allow fallback behavior
else:
    print("[MAIN] Valid configuration found, skipping provisioning")

# Import configuration (local config overrides defaults)
print("[MAIN] Loading configuration...")
try:
    from config_local import *
    print("[MAIN] Configuration loaded from config_local")
except ImportError:
    print("[MAIN] config_local not found, using default config.py")
    from config import *
    print("[MAIN] Default configuration loaded")

# Try to import the WebP decoder module
print("[MAIN] Checking for webpdec module...")
try:
    import webpdec
    WEBP_AVAILABLE = True
    print("[MAIN] webpdec module loaded successfully")
except ImportError as e:
    print(f"[MAIN] WARNING: webpdec module not found: {e}")
    WEBP_AVAILABLE = False

# Display driver imports - try different options
print("[MAIN] Detecting display driver...")
BOARD_TYPE = "unknown"
try:
    # Pimoroni Interstate 75
    print("[MAIN] Trying Interstate75 import...")
    from interstate75 import Interstate75
    from picographics import PicoGraphics
    BOARD_TYPE = "interstate75"
    print("[MAIN] Interstate 75 driver found")
except ImportError as e:
    print(f"[MAIN] Interstate75 not available: {e}")
    try:
        # Generic HUB75 via framebuffer
        print("[MAIN] Trying generic framebuffer...")
        import framebuf
        BOARD_TYPE = "generic"
        print("[MAIN] Generic framebuffer available")
    except ImportError as e2:
        print(f"[MAIN] No display driver found: {e2}")
        BOARD_TYPE = "unknown"

print("[MAIN] Display type:", BOARD_TYPE)
print("[MAIN] All imports completed successfully")
print("="*60)


class TronbytClient:
    """Client for connecting to Tronbyt server and displaying frames."""
    
    def __init__(self):
        """Initialize the Tronbyt client."""
        print("[CLIENT] Initializing TronbytClient...")
        
        self.display_id = DISPLAY_ID
        self.server_url = TRONBYT_SERVER_URL.rstrip('/')
        self.api_key = DEVICE_API_KEY if 'DEVICE_API_KEY' in globals() else ""
        self.current_brightness = DEFAULT_BRIGHTNESS
        self.width = DISPLAY_WIDTH
        self.height = DISPLAY_HEIGHT
        
        print(f"[CLIENT] Display: {self.width}x{self.height}")
        print(f"[CLIENT] Display ID: {self.display_id}")
        print(f"[CLIENT] Server URL: {self.server_url}")
        
        # Initialize display based on board type
        print("[CLIENT] Initializing display...")
        try:
            self._init_display()
            print("[CLIENT] Display initialized successfully")
        except Exception as e:
            print(f"[CLIENT] CRITICAL: Display initialization failed: {e}")
            sys.print_exception(e)
            raise
        
        # Set initial brightness
        print("[CLIENT] Setting initial brightness...")
        self.set_brightness(DEFAULT_BRIGHTNESS)
        
        # Show startup message
        print("[CLIENT] Showing startup message...")
        try:
            self.show_message("Tronbyt", (0, 255, 0))
            print("[CLIENT] Startup message displayed")
        except Exception as e:
            print(f"[CLIENT] Warning: Could not show startup message: {e}")
        
        time.sleep(1)
        print("[CLIENT] Initialization complete")
        
    def _init_display(self):
        """Initialize display driver based on board type."""
        global BOARD_TYPE
        
        print(f"[DISPLAY] Initializing for board type: {BOARD_TYPE}")
        
        if BOARD_TYPE == "interstate75":
            print("[DISPLAY] Initializing Interstate 75 display...")
            try:
                # Try 64x64 first, fall back to 64x32
                if self.height == 64:
                    from interstate75 import DISPLAY_INTERSTATE75_64X64
                    display_type = DISPLAY_INTERSTATE75_64X64
                    print("[DISPLAY] Using 64x64 display type")
                else:
                    from interstate75 import DISPLAY_INTERSTATE75_64X32
                    display_type = DISPLAY_INTERSTATE75_64X32
                    print("[DISPLAY] Using 64x32 display type")
                
                self.i75 = Interstate75(display=display_type)
                self.graphics = self.i75.display
                self._display_type = "interstate75"
                print("[DISPLAY] Interstate 75 initialized successfully")
            except Exception as e:
                print(f"[DISPLAY] Failed to init Interstate 75: {e}")
                sys.print_exception(e)
                raise
                
        elif BOARD_TYPE == "generic":
            print("[DISPLAY] Generic framebuffer - not fully implemented")
            # For generic RP2350 boards, you'd implement HUB75 driver here
            self._display_type = "generic"
            raise NotImplementedError("Generic HUB75 driver not yet implemented")
            
        else:
            raise RuntimeError(f"Unknown board type: {BOARD_TYPE}")
        
        print(f"[DISPLAY] Display initialized: {self.width}x{self.height}")
        
    def show_message(self, text, color=(255, 255, 255)):
        """Display a text message on the matrix."""
        if self._display_type == "interstate75":
            try:
                self.graphics.set_pen(self.graphics.create_pen(0, 0, 0))
                self.graphics.clear()
                
                # Center text
                text_x = max(2, (self.width - len(text) * 6) // 2)
                text_y = max(10, (self.height - 8) // 2)
                
                self.graphics.set_pen(self.graphics.create_pen(*color))
                self.graphics.text(text, text_x, text_y, scale=1)
                self.i75.update()
            except Exception as e:
                print(f"[DISPLAY] Error showing message: {e}")
        else:
            print(f"[DISPLAY] Cannot show message on {self._display_type}")
        
    def set_brightness(self, brightness):
        """Set display brightness (0-100)."""
        brightness = max(0, min(100, brightness))
        self.current_brightness = brightness
        
        if self._display_type == "interstate75":
            if hasattr(self.i75, 'set_brightness'):
                self.i75.set_brightness(brightness / 100.0)
        
        if DEBUG:
            print(f"[DISPLAY] Brightness set to {brightness}%")
    
    def connect_wifi(self):
        """Connect to WiFi network."""
        import network
        
        print(f"[WIFI] Connecting to WiFi: {WIFI_SSID}")
        try:
            self.show_message("WiFi...", (255, 255, 0))
        except:
            pass
        
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        print(f"[WIFI] Scanning for networks...")
        try:
            networks = wlan.scan()
            found_ssids = [n[0].decode('utf-8', 'ignore') for n in networks]
            print(f"[WIFI] Found {len(found_ssids)} networks")
            if DEBUG:
                print(f"[WIFI] Networks: {found_ssids[:10]}")  # Show first 10
            
            if WIFI_SSID not in found_ssids:
                print(f"[WIFI] WARNING: {WIFI_SSID} not found in scan!")
        except Exception as e:
            print(f"[WIFI] Scan failed (non-critical): {e}")
        
        print(f"[WIFI] Attempting connection...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Wait for connection
        max_wait = 20
        while max_wait > 0:
            status = wlan.status()
            if status < 0 or status >= 3:
                break
            max_wait -= 1
            print(f'[WIFI] Waiting for connection... ({max_wait} tries left)')
            time.sleep(1)
        
        # Check connection
        status = wlan.status()
        print(f"[WIFI] Final status: {status}")
        
        if status != 3:
            print(f"[WIFI] Connection failed with status: {status}")
            try:
                self.show_message("WiFi Fail", (255, 0, 0))
            except:
                pass
            raise RuntimeError(f'WiFi connection failed (status: {status})')
        else:
            status_config = wlan.ifconfig()
            print(f'[WIFI] Connected! IP: {status_config[0]}')
            try:
                self.show_message("WiFi OK", (0, 255, 0))
            except:
                pass
            time.sleep(1)
            return status_config[0]
    
    def fetch_frame(self):
        """Fetch a frame from the Tronbyt server using raw sockets."""
        import socket
        
        # Parse server URL to handle ports properly
        server = self.server_url.replace('http://', '').replace('https://', '')
        if '/' in server:
            server = server.split('/')[0]
        
        # Split host and port
        if ':' in server:
            host, port = server.split(':')
            port = int(port)
        else:
            host = server
            port = 80
        
        path = f"/v0/devices/{self.display_id}/next"
        
        if DEBUG:
            print(f"[FETCH] Host: {host}, Port: {port}")
            print(f"[FETCH] Path: {path}")
            print(f"[FETCH] API Key present: {'Yes' if self.api_key else 'No'}")
        
        try:
            # Create socket and connect
            addr = socket.getaddrinfo(host, port)[0][-1]
            s = socket.socket()
            s.settimeout(10)
            s.connect(addr)
            
            # Build HTTP request
            request_lines = [
                f"GET {path} HTTP/1.1",
                f"Host: {host}:{port}",
                "Connection: close",
            ]
            
            if self.api_key:
                request_lines.append(f"Authorization: {self.api_key}")
            
            request_lines.append("")  # Empty line before body
            request = "\r\n".join(request_lines) + "\r\n"
            
            if DEBUG:
                print(f"[FETCH] Sending request...")
            
            s.send(request.encode())
            
            # Receive response
            response = b""
            while True:
                try:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                except:
                    break
            
            s.close()
            
            # Parse response
            header_end = response.find(b"\r\n\r\n")
            if header_end == -1:
                print("[FETCH] Invalid HTTP response")
                return None, 15, None
            
            headers_bytes = response[:header_end]
            body = response[header_end + 4:]
            
            # Parse status line
            header_lines = headers_bytes.decode('utf-8', 'ignore').split("\r\n")
            status_line = header_lines[0]
            
            if DEBUG:
                print(f"[FETCH] Status: {status_line}")
            
            # Extract status code
            parts = status_line.split()
            if len(parts) < 2:
                print("[FETCH] Invalid status line")
                return None, 15, None
            
            try:
                status_code = int(parts[1])
            except:
                print("[FETCH] Could not parse status code")
                return None, 15, None
            
            # Parse headers for all responses
            headers = {}
            for line in header_lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip().lower()] = value.strip()
            
            if status_code == 200:
                dwell_secs = int(headers.get('tronbyt-dwell-secs', '15'))
                brightness = int(headers.get('tronbyt-brightness', '-1'))
                
                if brightness >= 0:
                    self.set_brightness(brightness)
                
                if DEBUG:
                    print(f"[FETCH] Got frame: {len(body)} bytes, dwell={dwell_secs}s")
                
                return body, dwell_secs, headers.get('content-type', '')
                
            elif status_code in (301, 302, 303, 307, 308):
                # Handle redirect
                location = headers.get('location', '')
                if location:
                    if DEBUG:
                        print(f"[FETCH] Redirect ({status_code}) to: {location}")
                    # Follow redirect
                    return self._fetch_with_redirect(location)
                else:
                    print(f"[FETCH] Redirect ({status_code}) but no Location header")
                    return None, 15, None
                
            elif status_code == 401:
                print(f"[FETCH] Error: Authentication failed (401)")
                return None, 15, None
            elif status_code == 404:
                print(f"[FETCH] Error: Endpoint not found (404)")
                return self._fetch_frame_alternate()
            else:
                print(f"[FETCH] Error: HTTP {status_code}")
                return None, 15, None
                
        except Exception as e:
            print(f"[FETCH] Error: {e}")
            import sys
            sys.print_exception(e)
            return self._fetch_frame_alternate()
    
    def _fetch_with_redirect(self, location, max_redirects=3):
        """Follow a redirect to fetch the frame."""
        import socket
        
        if max_redirects <= 0:
            print("[FETCH] Too many redirects")
            return None, 15, None
        
        # Parse the location URL
        if location.startswith('http://'):
            location = location[7:]
        elif location.startswith('https://'):
            print("[FETCH] HTTPS not supported, skipping")
            return None, 15, None
        
        # Split path from host
        if '/' in location:
            host_port, path = location.split('/', 1)
            path = '/' + path
        else:
            host_port = location
            path = '/'
        
        # Parse host and port
        if ':' in host_port:
            host, port = host_port.split(':')
            port = int(port)
        else:
            host = host_port
            port = 80
        
        if DEBUG:
            print(f"[FETCH] Redirect to: {host}:{port}{path}")
        
        try:
            addr = socket.getaddrinfo(host, port)[0][-1]
            s = socket.socket()
            s.settimeout(10)
            s.connect(addr)
            
            request_lines = [
                f"GET {path} HTTP/1.1",
                f"Host: {host}:{port}",
                "Connection: close",
            ]
            
            if self.api_key:
                request_lines.append(f"Authorization: {self.api_key}")
            
            request_lines.append("")
            request = "\r\n".join(request_lines) + "\r\n"
            
            s.send(request.encode())
            
            response = b""
            while True:
                try:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                except:
                    break
            
            s.close()
            
            header_end = response.find(b"\r\n\r\n")
            if header_end == -1:
                return None, 15, None
            
            headers_bytes = response[:header_end]
            body = response[header_end + 4:]
            
            header_lines = headers_bytes.decode('utf-8', 'ignore').split("\r\n")
            status_line = header_lines[0]
            parts = status_line.split()
            
            if len(parts) < 2:
                return None, 15, None
            
            try:
                status_code = int(parts[1])
            except:
                return None, 15, None
            
            # Parse headers
            headers = {}
            for line in header_lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip().lower()] = value.strip()
            
            if status_code == 200:
                dwell_secs = int(headers.get('tronbyt-dwell-secs', '15'))
                brightness = int(headers.get('tronbyt-brightness', '-1'))
                
                if brightness >= 0:
                    self.set_brightness(brightness)
                
                if DEBUG:
                    print(f"[FETCH] Got frame after redirect: {len(body)} bytes")
                
                return body, dwell_secs, headers.get('content-type', '')
            elif status_code in (301, 302, 303, 307, 308):
                # Follow another redirect
                new_location = headers.get('location', '')
                if new_location and max_redirects > 1:
                    return self._fetch_with_redirect(new_location, max_redirects - 1)
            
            return None, 15, None
            
        except Exception as e:
            print(f"[FETCH] Redirect fetch error: {e}")
            return None, 15, None

    def _fetch_frame_alternate(self):
        """Try alternate API endpoint formats using raw sockets."""
        import socket
        
        # Parse server URL
        server = self.server_url.replace('http://', '').replace('https://', '')
        if '/' in server:
            server = server.split('/')[0]
        
        if ':' in server:
            host, port = server.split(':')
            port = int(port)
        else:
            host = server
            port = 80
        
        # Try different paths
        paths_to_try = [
            f"/devices/{self.display_id}/next",
            f"/api/v1/devices/{self.display_id}/next",
        ]
        
        for path in paths_to_try:
            if DEBUG:
                print(f"[FETCH] Trying path: {path}")
            
            try:
                addr = socket.getaddrinfo(host, port)[0][-1]
                s = socket.socket()
                s.settimeout(10)
                s.connect(addr)
                
                request_lines = [
                    f"GET {path} HTTP/1.1",
                    f"Host: {host}:{port}",
                    "Connection: close",
                ]
                
                if self.api_key:
                    request_lines.append(f"Authorization: {self.api_key}")
                
                request_lines.append("")
                request = "\r\n".join(request_lines) + "\r\n"
                
                s.send(request.encode())
                
                response = b""
                while True:
                    try:
                        chunk = s.recv(4096)
                        if not chunk:
                            break
                        response += chunk
                    except:
                        break
                
                s.close()
                
                header_end = response.find(b"\r\n\r\n")
                if header_end == -1:
                    continue
                
                headers_bytes = response[:header_end]
                body = response[header_end + 4:]
                
                header_lines = headers_bytes.decode('utf-8', 'ignore').split("\r\n")
                status_line = header_lines[0]
                parts = status_line.split()
                
                if len(parts) < 2:
                    continue
                
                try:
                    status_code = int(parts[1])
                except:
                    continue
                
                if status_code == 200:
                    headers = {}
                    for line in header_lines[1:]:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            headers[key.strip().lower()] = value.strip()
                    
                    dwell_secs = int(headers.get('tronbyt-dwell-secs', '15'))
                    brightness = int(headers.get('tronbyt-brightness', '-1'))
                    
                    if brightness >= 0:
                        self.set_brightness(brightness)
                    
                    if DEBUG:
                        print(f"[FETCH] Success with path: {path}")
                    
                    return body, dwell_secs, headers.get('content-type', '')
                    
            except Exception as e:
                if DEBUG:
                    print(f"[FETCH] Failed: {e}")
                continue
        
        print(f"[FETCH] All endpoints failed")
        return None, 15, None
    
    def decode_and_display(self, webp_data):
        """Decode WebP data and display on matrix."""
        if not WEBP_AVAILABLE:
            print("[DISPLAY] ERROR: webpdec module not available!")
            self.show_message("No webpdec", (255, 0, 0))
            return False
        
        try:
            if DEBUG:
                print(f"[DISPLAY] Decoding WebP: {len(webp_data)} bytes")
            
            # Decode WebP to RGB565
            rgb565_data = webpdec.decode(webp_data, self.width, self.height)
            
            if rgb565_data is None or len(rgb565_data) == 0:
                print("[DISPLAY] WebP decode failed - no data returned")
                return False
            
            if DEBUG:
                print(f"[DISPLAY] Decoded to {len(rgb565_data)} bytes RGB565")
            
            # Display on matrix
            self._display_rgb565(rgb565_data)
            return True
            
        except Exception as e:
            print(f"[DISPLAY] Error decoding/displaying: {e}")
            import sys
            sys.print_exception(e)
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
            print(f"[DISPLAY] Frame displayed: {len(rgb565_data)} bytes")
    
    def run(self):
        """Main loop - fetch and display frames."""
        print("\n" + "="*60)
        print("Tronbyt RP2350 Client Starting")
        print("="*60)
        
        if not WEBP_AVAILABLE:
            print("CRITICAL ERROR: webpdec module not available!")
            self.show_message("No webpdec!", (255, 0, 0))
            while True:
                time.sleep(1)
        
        # Connect to WiFi
        try:
            self.connect_wifi()
        except Exception as e:
            print(f"[MAIN] WiFi connection failed: {e}")
            self.show_message("WiFi Error", (255, 0, 0))
            time.sleep(5)
            # Retry
            return self.run()
        
        print(f"\nConnecting to Tronbyt server: {self.server_url}")
        print(f"Display ID: {self.display_id}")
        print("="*60 + "\n")
        
        # Main loop
        loop_count = 0
        while True:
            try:
                loop_count += 1
                if DEBUG or loop_count % 10 == 1:
                    print(f"[MAIN] Loop iteration {loop_count}")
                
                # Fetch frame
                frame_data, dwell_secs, content_type = self.fetch_frame()
                
                if frame_data:
                    # Decode and display
                    if self.decode_and_display(frame_data):
                        if DEBUG:
                            print(f"[MAIN] Frame displayed, sleeping for {dwell_secs}s")
                    else:
                        self.show_message("Decode Error", (255, 0, 0))
                else:
                    print("[MAIN] No frame received from server")
                    self.show_message("No Frame", (255, 128, 0))
                
                # Wait before next fetch
                time.sleep(dwell_secs)
                
            except Exception as e:
                print(f"[MAIN] Error in main loop: {e}")
                import sys
                sys.print_exception(e)
                try:
                    self.show_message("Error", (255, 0, 0))
                except:
                    pass
                time.sleep(5)
            
            # Force garbage collection
            gc.collect()
            if DEBUG and loop_count % 10 == 0:
                print(f"[MAIN] Free memory: {gc.mem_free()} bytes")


# Entry point
print("[MAIN] Creating TronbytClient instance...")
try:
    client = TronbytClient()
    print("[MAIN] Starting main loop...")
    client.run()
except Exception as e:
    print("="*60)
    print("FATAL ERROR: Could not start Tronbyt client")
    print("="*60)
    print(f"Error: {e}")
    sys.print_exception(e)
    print("\nSystem halted. Check configuration and reboot.")
    while True:
        time.sleep(1)
