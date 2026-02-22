"""
WiFi Provisioning Module for Tronbyt RP2350
Handles captive portal setup for first-time device configuration.
"""

import sys
print("[PROV] Loading provisioning module...")

# Standard imports with error handling
try:
    import network
    print("[PROV] network module imported")
except ImportError as e:
    print(f"[PROV] CRITICAL: network module not available: {e}")
    raise

try:
    import socket
    print("[PROV] socket module imported")
except ImportError as e:
    print(f"[PROV] CRITICAL: socket module not available: {e}")
    raise

try:
    import ure as re
    print("[PROV] ure (regex) module imported")
except ImportError:
    print("[PROV] WARNING: ure not available, trying re...")
    try:
        import re
        print("[PROV] re module imported")
    except ImportError as e:
        print(f"[PROV] ERROR: No regex module available: {e}")
        re = None

try:
    import json
    print("[PROV] json module imported")
except ImportError as e:
    print(f"[PROV] CRITICAL: json module not available: {e}")
    raise

try:
    import machine
    print("[PROV] machine module imported")
except ImportError as e:
    print(f"[PROV] CRITICAL: machine module not available: {e}")
    raise

try:
    import time
    print("[PROV] time module imported")
except ImportError as e:
    print(f"[PROV] ERROR: time module not available: {e}")
    raise

print("[PROV] All required imports successful")

# AP Configuration
AP_SSID = "Tronbyt-Setup"
AP_PASSWORD = "setup1234"  # Open network would be better but MicroPython AP requires password
AP_IP = "192.168.4.1"
AP_NETMASK = "255.255.255.0"

print(f"[PROV] AP Config: SSID={AP_SSID}, IP={AP_IP}")

# HTML Template for the setup page
SETUP_PAGE = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tronbyt Setup</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: #fff;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: #16213e;
            border-radius: 12px;
            padding: 32px;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        h1 {
            text-align: center;
            margin-bottom: 8px;
            font-size: 24px;
        }
        .subtitle {
            text-align: center;
            color: #8892b0;
            margin-bottom: 24px;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 6px;
            font-size: 14px;
            color: #ccd6f6;
        }
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #233554;
            border-radius: 6px;
            background: #0a192f;
            color: #fff;
            font-size: 16px;
        }
        input:focus {
            outline: none;
            border-color: #64ffda;
        }
        .hint {
            font-size: 12px;
            color: #8892b0;
            margin-top: 4px;
        }
        button {
            width: 100%;
            padding: 14px;
            background: #64ffda;
            color: #0a192f;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 8px;
        }
        button:hover {
            background: #4fd1c5;
        }
        .status {
            text-align: center;
            padding: 16px;
            border-radius: 6px;
            margin-bottom: 20px;
            display: none;
        }
        .status.success {
            background: #064e3b;
            color: #6ee7b7;
            display: block;
        }
        .status.error {
            background: #450a0a;
            color: #fca5a5;
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Tronbyt Setup</h1>
        <p class="subtitle">Configure your display</p>
        <div id="status" class="status"></div>
        <form id="setupForm">
            <div class="form-group">
                <label for="ssid">WiFi Network Name</label>
                <input type="text" id="ssid" name="ssid" required placeholder="Your WiFi SSID">
            </div>
            <div class="form-group">
                <label for="password">WiFi Password</label>
                <input type="password" id="password" name="password" placeholder="WiFi password">
            </div>
            <div class="form-group">
                <label for="display_id">Display ID</label>
                <input type="text" id="display_id" name="display_id" required 
                       placeholder="e.g., living-room-display">
                <p class="hint">Unique name for this display (no spaces)</p>
            </div>
            <div class="form-group">
                <label for="server_url">Tronbyt Server URL</label>
                <input type="text" id="server_url" name="server_url" 
                       placeholder="http://192.168.1.100:8000">
                <p class="hint">Optional - defaults to auto-discovery</p>
            </div>
            <button type="submit">Save & Reboot</button>
        </form>
    </div>
    <script>
        document.getElementById('setupForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                const statusEl = document.getElementById('status');
                
                if (result.success) {
                    statusEl.className = 'status success';
                    statusEl.textContent = 'Settings saved! Rebooting...';
                } else {
                    statusEl.className = 'status error';
                    statusEl.textContent = 'Error: ' + result.message;
                }
            } catch (err) {
                const statusEl = document.getElementById('status');
                statusEl.className = 'status error';
                statusEl.textContent = 'Error saving settings';
            }
        });
    </script>
</body>
</html>
"""

SUCCESS_PAGE = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tronbyt - Saved</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: #1a1a2e;
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            padding: 32px;
        }
        h1 { color: #64ffda; margin-bottom: 16px; }
        p { color: #8892b0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Settings Saved!</h1>
        <p>Your Tronbyt is now rebooting...</p>
    </div>
</body>
</html>
"""

print("[PROV] HTML templates defined")


class ProvisioningServer:
    """Simple HTTP server for WiFi provisioning."""
    
    def __init__(self):
        print("[PROV] Creating ProvisioningServer instance...")
        self.ap = None
        self.server_socket = None
        self.configured = False
        print("[PROV] ProvisioningServer initialized")
        
    def start_ap(self):
        """Start the access point for provisioning."""
        print("[PROV] Starting provisioning AP...")
        
        try:
            self.ap = network.WLAN(network.AP_IF)
            print("[PROV] Got AP interface")
            
            print("[PROV] Setting AP active...")
            self.ap.active(True)
            
            print(f"[PROV] Configuring AP with SSID: {AP_SSID}...")
            self.ap.config(essid=AP_SSID, password=AP_PASSWORD, authmode=network.AUTH_WPA_WPA2_PSK)
            
            # Wait for AP to be active
            print("[PROV] Waiting for AP to become active...")
            max_wait = 20
            while max_wait > 0:
                if self.ap.active():
                    print(f"[PROV] AP is active after {20-max_wait} checks")
                    break
                max_wait -= 1
                time.sleep(0.5)
            
            if not self.ap.active():
                raise RuntimeError("AP failed to become active after 10 seconds")
            
            # Configure IP
            print(f"[PROV] Setting AP IP configuration: {AP_IP}...")
            self.ap.ifconfig((AP_IP, AP_NETMASK, AP_IP, AP_IP))
            
            actual_config = self.ap.ifconfig()
            print(f"[PROV] AP started successfully!")
            print(f"[PROV]   SSID: {AP_SSID}")
            print(f"[PROV]   IP: {actual_config[0]}")
            print(f"[PROV]   Connect to this network, then visit http://{AP_IP}")
            
        except Exception as e:
            print(f"[PROV] ERROR starting AP: {e}")
            sys.print_exception(e)
            raise
        
    def start_server(self):
        """Start the HTTP server."""
        print("[PROV] Starting HTTP server...")
        
        try:
            addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
            print(f"[PROV] Server address: {addr}")
            
            print("[PROV] Creating socket...")
            self.server_socket = socket.socket()
            
            print("[PROV] Setting socket options...")
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            print("[PROV] Binding to address...")
            self.server_socket.bind(addr)
            
            print("[PROV] Starting listener...")
            self.server_socket.listen(5)
            
            print(f"[PROV] HTTP server listening on port 80")
            
        except Exception as e:
            print(f"[PROV] ERROR starting HTTP server: {e}")
            sys.print_exception(e)
            raise
        
    def handle_request(self, client):
        """Handle a single HTTP request."""
        client_addr = None
        try:
            # Get client address for logging
            try:
                client_addr = client.getpeername()
                print(f"[PROV] Handling request from {client_addr}")
            except:
                print("[PROV] Handling request from unknown client")
            
            # Receive request
            request = b""
            client.settimeout(2.0)
            
            try:
                while True:
                    chunk = client.recv(1024)
                    if not chunk:
                        break
                    request += chunk
                    if b"\r\n\r\n" in request:
                        break
            except OSError as e:
                print(f"[PROV] Socket receive timeout or error: {e}")
                pass
            
            if not request:
                print("[PROV] Empty request received")
                return
            
            # Parse request line
            request_str = request.decode('utf-8', 'ignore')
            lines = request_str.split('\r\n')
            if not lines:
                print("[PROV] No request lines found")
                return
                
            request_line = lines[0]
            parts = request_line.split()
            if len(parts) < 2:
                print(f"[PROV] Invalid request line: {request_line}")
                return
                
            method = parts[0]
            path = parts[1]
            
            print(f"[PROV] {method} {path}")
            
            # Handle different endpoints
            if path == '/' or path == '/index.html':
                self.send_html(client, SETUP_PAGE)
                
            elif path == '/save' and method == 'POST':
                self.handle_save(request_str, client)
                
            elif path == '/generate_204' or path == '/hotspot-detect.html':
                # Captive portal detection responses
                print("[PROV] Handling captive portal detection")
                self.send_redirect(client, 'http://192.168.4.1/')
                
            else:
                print(f"[PROV] Unknown path, redirecting to /")
                self.send_redirect(client, '/')
                
        except Exception as e:
            print(f"[PROV] Error handling request: {e}")
            sys.print_exception(e)
        finally:
            try:
                client.close()
            except:
                pass
            
    def handle_save(self, request_str, client):
        """Handle the save configuration endpoint."""
        print("[PROV] Handling save configuration request...")
        
        try:
            # Extract JSON body
            if re is None:
                print("[PROV] ERROR: No regex module available")
                self.send_json(client, {'success': False, 'message': 'Server error: no regex'})
                return
                
            body_match = re.search(r'\r\n\r\n(.+)$', request_str, re.DOTALL)
            if not body_match:
                print("[PROV] No body found in request")
                self.send_json(client, {'success': False, 'message': 'No data received'})
                return
                
            body = body_match.group(1)
            print(f"[PROV] Received body: {body[:200]}...")  # Print first 200 chars
            
            try:
                data = json.loads(body)
            except json.JSONDecodeError as e:
                print(f"[PROV] JSON parse error: {e}")
                self.send_json(client, {'success': False, 'message': f'Invalid JSON: {str(e)}'})
                return
            
            print(f"[PROV] Parsed data: {data}")
            
            # Validate required fields
            if not data.get('ssid') or not data.get('display_id'):
                print("[PROV] Missing required fields")
                self.send_json(client, {'success': False, 'message': 'WiFi SSID and Display ID are required'})
                return
            
            # Generate config file content
            server_url = data.get('server_url', '')
            if not server_url:
                server_url = 'http://tronbyt.local:8000'  # Default mDNS discovery
            
            print(f"[PROV] Generating config file...")
            config_content = f'''# Auto-generated config from provisioning
# Generated on boot - edit manually if needed

# WiFi Configuration
WIFI_SSID = {repr(data['ssid'])}
WIFI_PASSWORD = {repr(data.get('password', ''))}

# Tronbyt Server Configuration
TRONBYT_SERVER_URL = {repr(server_url)}
DISPLAY_ID = {repr(data['display_id'])}

# Display Configuration
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32

# Update interval in seconds
UPDATE_INTERVAL = 1.0

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2

# Debug mode
DEBUG = True

# Default brightness
DEFAULT_BRIGHTNESS = 50
'''
            
            # Write config file
            print("[PROV] Writing config_local.py...")
            try:
                with open('config_local.py', 'w') as f:
                    f.write(config_content)
                print("[PROV] Config file written successfully")
            except Exception as e:
                print(f"[PROV] ERROR writing config file: {e}")
                sys.print_exception(e)
                self.send_json(client, {'success': False, 'message': f'Failed to write config: {str(e)}'})
                return
            
            # Verify the file was written
            try:
                with open('config_local.py', 'r') as f:
                    content = f.read()
                print(f"[PROV] Verified config file: {len(content)} bytes")
            except Exception as e:
                print(f"[PROV] WARNING: Could not verify config file: {e}")
            
            print("[PROV] Configuration saved successfully!")
            self.send_json(client, {'success': True})
            self.configured = True
            
        except Exception as e:
            print(f"[PROV] Error saving config: {e}")
            sys.print_exception(e)
            self.send_json(client, {'success': False, 'message': str(e)})
            
    def send_html(self, client, content):
        """Send HTML response."""
        try:
            response = f"HTTP/1.1 200 OK\r\n"
            response += f"Content-Type: text/html\r\n"
            response += f"Content-Length: {len(content)}\r\n"
            response += f"Connection: close\r\n\r\n"
            response += content
            client.send(response.encode())
        except Exception as e:
            print(f"[PROV] Error sending HTML: {e}")
            
    def send_json(self, client, data):
        """Send JSON response."""
        try:
            content = json.dumps(data)
            response = f"HTTP/1.1 200 OK\r\n"
            response += f"Content-Type: application/json\r\n"
            response += f"Content-Length: {len(content)}\r\n"
            response += f"Connection: close\r\n\r\n"
            response += content
            client.send(response.encode())
        except Exception as e:
            print(f"[PROV] Error sending JSON: {e}")
        
    def send_redirect(self, client, url):
        """Send redirect response."""
        try:
            response = f"HTTP/1.1 302 Found\r\n"
            response += f"Location: {url}\r\n"
            response += f"Connection: close\r\n\r\n"
            client.send(response.encode())
        except Exception as e:
            print(f"[PROV] Error sending redirect: {e}")
        
    def run(self):
        """Main provisioning loop."""
        print("\n" + "="*60)
        print("PROVISIONING MODE ACTIVE")
        print("="*60)
        
        try:
            self.start_ap()
        except Exception as e:
            print(f"[PROV] FATAL: Could not start AP: {e}")
            raise
            
        try:
            self.start_server()
        except Exception as e:
            print(f"[PROV] FATAL: Could not start HTTP server: {e}")
            self.cleanup()
            raise
        
        print("\n" + "="*60)
        print("SETUP INSTRUCTIONS:")
        print("="*60)
        print(f"1. Connect your phone/computer to WiFi: {AP_SSID}")
        print(f"   Password: {AP_PASSWORD}")
        print(f"2. Open a web browser")
        print(f"3. Go to: http://{AP_IP}")
        print("4. Enter your WiFi and display settings")
        print("5. Click 'Save & Reboot'")
        print("="*60 + "\n")
        
        request_count = 0
        
        # Main server loop
        while not self.configured:
            try:
                print("[PROV] Waiting for connection...")
                client, addr = self.server_socket.accept()
                request_count += 1
                print(f"[PROV] Connection #{request_count} from {addr}")
                self.handle_request(client)
                
                if self.configured:
                    print("[PROV] Configuration complete!")
                    # Small delay to let response send
                    time.sleep(1)
                    print("[PROV] Rebooting system...")
                    machine.reset()
                    
            except OSError as e:
                # Timeout on accept, continue loop
                if e.args[0] == 11:  # EAGAIN
                    continue
                print(f"[PROV] Server socket error: {e}")
                time.sleep(0.1)
            except Exception as e:
                print(f"[PROV] Server error: {e}")
                sys.print_exception(e)
                time.sleep(0.1)
                
    def cleanup(self):
        """Clean up resources."""
        print("[PROV] Cleaning up...")
        if self.server_socket:
            try:
                self.server_socket.close()
                print("[PROV] Server socket closed")
            except:
                pass
        if self.ap:
            try:
                self.ap.active(False)
                print("[PROV] AP disabled")
            except:
                pass
        print("[PROV] Cleanup complete")


def needs_provisioning():
    """Check if device needs provisioning (no valid config)."""
    print("[PROV] Checking if provisioning is needed...")
    try:
        import config_local
        # Config exists, check if it has valid values
        if (hasattr(config_local, 'WIFI_SSID') and 
            config_local.WIFI_SSID and 
            config_local.WIFI_SSID != "YourWiFiSSID"):
            print("[PROV] Valid configuration found, no provisioning needed")
            return False
        print("[PROV] Config exists but has placeholder values")
        return True
    except ImportError:
        print("[PROV] No config_local.py found, provisioning needed")
        return True


def start_provisioning():
    """Entry point to start provisioning mode."""
    print("[PROV] Starting provisioning mode...")
    server = ProvisioningServer()
    try:
        server.run()
    except KeyboardInterrupt:
        print("[PROV] Provisioning interrupted by user")
        server.cleanup()
        raise
    except Exception as e:
        print(f"[PROV] Provisioning failed with error: {e}")
        sys.print_exception(e)
        server.cleanup()
        raise

print("[PROV] Provisioning module fully loaded")
