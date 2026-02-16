"""
Example configuration for Tronbyt Interstate 75W Client
Copy this to config_local.py and customize for your setup
"""

# ============================================================================
# WiFi Configuration
# ============================================================================
WIFI_SSID = "MyHomeNetwork"
WIFI_PASSWORD = "SuperSecretPassword123"

# ============================================================================
# Tronbyt Server Configuration
# ============================================================================
# URL of your Tronbyt server (no trailing slash)
TRONBYT_SERVER_URL = "http://192.168.1.100:8000"

# Unique identifier for this display
# This should match a display configured in your Tronbyt server
DISPLAY_ID = "living-room-matrix"

# ============================================================================
# Display Configuration
# ============================================================================
# Matrix dimensions
DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32

# Default brightness (0-100)
# This is overridden by the X-Brightness header from the server
DEFAULT_BRIGHTNESS = 50

# ============================================================================
# Update Configuration
# ============================================================================
# How often to fetch new frames from the server (seconds)
# Lower = more responsive but more network traffic
# Higher = less traffic but slower updates
UPDATE_INTERVAL = 1.0

# ============================================================================
# Error Handling
# ============================================================================
# Maximum consecutive errors before showing error message
MAX_RETRIES = 3

# Delay between retries (seconds)
RETRY_DELAY = 2

# ============================================================================
# Debug Options
# ============================================================================
# Enable debug output (prints to serial console)
# Set to False for production to save memory
DEBUG = True

# ============================================================================
# Advanced Options
# ============================================================================
# HTTP request timeout (seconds)
HTTP_TIMEOUT = 10

# You can add custom settings here
# CUSTOM_SETTING = "value"
