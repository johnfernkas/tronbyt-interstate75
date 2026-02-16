"""
Configuration file for Tronbyt Interstate 75W Client

Copy this file to config.py and update with your settings
"""

# WiFi credentials
WIFI_SSID = "YourWiFiNetwork"
WIFI_PASSWORD = "YourWiFiPassword"

# Tronbyt RGB Bridge server
# This is the address of the RGB bridge service (not the main Tronbyt server)
SERVER_URL = "http://192.168.1.100:8001"  # Update with your server IP/hostname

# Device ID (must match a device configured in Tronbyt server)
DEVICE_ID = "interstate75_1"

# Display type - uncomment the one that matches your panel
# DISPLAY_TYPE = "32x32"   # 32x32 panel
# DISPLAY_TYPE = "64x32"   # 64x32 panel (single panel)
DISPLAY_TYPE = "64x64"     # 64x64 panel
# DISPLAY_TYPE = "128x64"  # 128x64 panel (two 64x32 panels)

# Network settings
MAX_RETRIES = 3           # Number of WiFi connection retries
RETRY_DELAY = 5           # Seconds between retries
WIFI_TIMEOUT = 20         # WiFi connection timeout (seconds)

# Debug mode (shows more info on display)
DEBUG = False
