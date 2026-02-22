# Configuration for Tronbyt RP2350 Client
# Copy this to config_local.py and customize your settings

# WiFi Configuration
WIFI_SSID = "YourWiFiSSID"
WIFI_PASSWORD = "YourWiFiPassword"

# Tronbyt Server Configuration
TRONBYT_SERVER_URL = "http://192.168.1.100:8000"  # Your Tronbyt server address
DISPLAY_ID = "rp2350-001"  # Unique identifier for this display
DEVICE_API_KEY = ""  # Device API key from Tronbyt server (optional but recommended)

# Display Configuration
# Common sizes: 64x32, 64x64, 128x32, 128x64
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32

# Update/Retry configuration
MAX_RETRIES = 3           # Number of fetch retries
RETRY_DELAY = 2           # Seconds between retries

# Debug mode (prints extra info on serial console)
DEBUG = False

# Default brightness (0-100) - overridden by server header if provided
DEFAULT_BRIGHTNESS = 50
