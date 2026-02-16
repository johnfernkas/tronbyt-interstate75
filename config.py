# Configuration for Tronbyt Interstate 75W Client
# Copy this to config_local.py and customize your settings

# WiFi Configuration
WIFI_SSID = "YourWiFiSSID"
WIFI_PASSWORD = "YourWiFiPassword"

# Tronbyt Server Configuration
TRONBYT_SERVER_URL = "http://192.168.1.100:8000"  # Your Tronbyt server address
DISPLAY_ID = "interstate75-001"  # Unique identifier for this display

# Display Configuration
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32

# Update interval in seconds (how often to check for new frames)
UPDATE_INTERVAL = 1.0

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Debug mode (prints extra info)
DEBUG = True

# Default brightness (0-100) - overridden by server header
DEFAULT_BRIGHTNESS = 50
