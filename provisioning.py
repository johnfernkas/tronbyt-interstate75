"""
WiFi Provisioning Module for Tronbyt RP2350
Handles captive portal setup for first-time device configuration.
"""

import network
import socket
import ure as re
import json
import machine

# AP Configuration
AP_SSID = "Tronbyt-Setup"
AP_PASSWORD = "setup1234"  # Open network would be better but MicroPython AP requires password
AP_IP = "192.168.4.1"
AP_NETMASK = "255.255.255.0"

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


class ProvisioningServer:
    """Simple HTTP server for WiFi provisioning."""
    
    def __init__(self):
        self.ap = None
        self.server_socket = None
        self.configured = False
        
    def start_ap(self):
        """Start the access point for provisioning."""
        print("Starting provisioning AP...")
        
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        self.ap.config(essid=AP_SSID, password=AP_PASSWORD, authmode=network.AUTH_WPA_WPA2_PSK)
        
        # Wait for AP to be active
        import time
        max_wait = 10
        while max_wait > 0:
            if self.ap.active():
                break
            max_wait -= 1
            time.sleep(0.5)
        
        # Configure IP
        self.ap.ifconfig((AP_IP, AP_NETMASK, AP_IP, AP_IP))
        
        print(f"AP started: {AP_SSID}")
        print(f"Connect to this network, then visit http://{AP_IP}")
        
    def start_server(self):
        """Start the HTTP server."""
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(addr)
        self.server_socket.listen(5)
        
        print(f"HTTP server listening on port 80")
        
    def handle_request(self, client):
        """Handle a single HTTP request."""
        try:
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
            except OSError:
                pass
            
            if not request:
                return
            
            # Parse request line
            request_str = request.decode('utf-8', 'ignore')
            lines = request_str.split('\r\n')
            if not lines:
                return
                
            request_line = lines[0]
            parts = request_line.split()
            if len(parts) < 2:
                return
                
            method = parts[0]
            path = parts[1]
            
            # Handle different endpoints
            if path == '/' or path == '/index.html':
                self.send_html(client, SETUP_PAGE)
                
            elif path == '/save' and method == 'POST':
                self.handle_save(request_str, client)
                
            elif path == '/generate_204' or path == '/hotspot-detect.html':
                # Captive portal detection responses
                self.send_redirect(client, 'http://192.168.4.1/')
                
            else:
                self.send_redirect(client, '/')
                
        except Exception as e:
            print(f"Error handling request: {e}")
        finally:
            client.close()
            
    def handle_save(self, request_str, client):
        """Handle the save configuration endpoint."""
        try:
            # Extract JSON body
            body_match = re.search(r'\r\n\r\n(.+)$', request_str, re.DOTALL)
            if not body_match:
                self.send_json(client, {'success': False, 'message': 'No data received'})
                return
                
            body = body_match.group(1)
            data = json.loads(body)
            
            # Validate required fields
            if not data.get('ssid') or not data.get('display_id'):
                self.send_json(client, {'success': False, 'message': 'WiFi SSID and Display ID are required'})
                return
            
            # Generate config file content
            server_url = data.get('server_url', '')
            if not server_url:
                server_url = 'http://tronbyt.local:8000'  # Default mDNS discovery
            
            config_content = f'''# Auto-generated config from provisioning
# Generated on boot - edit manually if needed

# WiFi Configuration
WIFI_SSID = "{data['ssid']}"
WIFI_PASSWORD = "{data.get('password', '')}"

# Tronbyt Server Configuration
TRONBYT_SERVER_URL = "{server_url}"
DISPLAY_ID = "{data['display_id']}"

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
            with open('config_local.py', 'w') as f:
                f.write(config_content)
            
            print("Configuration saved!")
            self.send_json(client, {'success': True})
            self.configured = True
            
        except Exception as e:
            print(f"Error saving config: {e}")
            self.send_json(client, {'success': False, 'message': str(e)})
            
    def send_html(self, client, content):
        """Send HTML response."""
        response = f"HTTP/1.1 200 OK\r\n"
        response += f"Content-Type: text/html\r\n"
        response += f"Content-Length: {len(content)}\r\n"
        response += f"Connection: close\r\n\r\n"
        response += content
        client.send(response.encode())
        
    def send_json(self, client, data):
        """Send JSON response."""
        content = json.dumps(data)
        response = f"HTTP/1.1 200 OK\r\n"
        response += f"Content-Type: application/json\r\n"
        response += f"Content-Length: {len(content)}\r\n"
        response += f"Connection: close\r\n\r\n"
        response += content
        client.send(response.encode())
        
    def send_redirect(self, client, url):
        """Send redirect response."""
        response = f"HTTP/1.1 302 Found\r\n"
        response += f"Location: {url}\r\n"
        response += f"Connection: close\r\n\r\n"
        client.send(response.encode())
        
    def run(self):
        """Main provisioning loop."""
        import time
        
        self.start_ap()
        self.start_server()
        
        print("Provisioning mode active. Waiting for configuration...")
        print("Connect to WiFi network: Tronbyt-Setup")
        print("Then open: http://192.168.4.1")
        
        # Main server loop
        while not self.configured:
            try:
                client, addr = self.server_socket.accept()
                print(f"Connection from {addr}")
                self.handle_request(client)
                
                if self.configured:
                    print("Configuration complete, rebooting...")
                    # Small delay to let response send
                    time.sleep(1)
                    machine.reset()
                    
            except Exception as e:
                print(f"Server error: {e}")
                time.sleep(0.1)
                
    def cleanup(self):
        """Clean up resources."""
        if self.server_socket:
            self.server_socket.close()
        if self.ap:
            self.ap.active(False)


def needs_provisioning():
    """Check if device needs provisioning (no valid config)."""
    try:
        import config_local
        # Config exists, check if it has valid values
        if (hasattr(config_local, 'WIFI_SSID') and 
            config_local.WIFI_SSID and 
            config_local.WIFI_SSID != "YourWiFiSSID"):
            return False
        return True
    except ImportError:
        return True


def start_provisioning():
    """Entry point to start provisioning mode."""
    server = ProvisioningServer()
    try:
        server.run()
    except KeyboardInterrupt:
        print("Provisioning interrupted")
        server.cleanup()
        raise
