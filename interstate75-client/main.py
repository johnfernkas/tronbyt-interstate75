"""
Tronbyt Client for Pimoroni Interstate 75W
Fetches raw RGB data from Tronbyt RGB Bridge and displays on HUB75 matrix

Author: Ollie (AI Assistant)
Date: February 15, 2026
License: MIT

Installation:
1. Flash MicroPython to Interstate 75W
2. Copy this file to the device as main.py
3. Update WiFi credentials and server URL below
4. Reset the device

Hardware Tested:
- Pimoroni Interstate 75W (RP2350)
- 64x64 RGB LED Matrix Panel (HUB75)
"""
import network
import urequests
import time
import gc
import machine
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_64X64

# ============================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================

# WiFi credentials
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# Tronbyt RGB Bridge server
SERVER_URL = "http://192.168.1.100:8001"  # Update with your server IP
DEVICE_ID = "interstate75_1"              # Update with your device ID

# Display type - adjust for your panel size
# Options: DISPLAY_INTERSTATE75_32X32, DISPLAY_INTERSTATE75_64X32, 
#          DISPLAY_INTERSTATE75_64X64, DISPLAY_INTERSTATE75_128X64
DISPLAY_TYPE = DISPLAY_INTERSTATE75_64X64

# Network settings
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
WIFI_TIMEOUT = 20  # seconds

# ============================================
# HARDWARE INITIALIZATION
# ============================================

print("\n" + "="*50)
print("Tronbyt Client for Interstate 75W")
print("="*50)

# Initialize display
print(f"Initializing display: {DISPLAY_TYPE}")
i75 = Interstate75(display=DISPLAY_TYPE)
display = i75.display

# Get display dimensions
WIDTH = display.get_width()
HEIGHT = display.get_height()
print(f"Display size: {WIDTH}x{HEIGHT}")

# Initialize buttons
button_a = i75.switch_a
button_b = i75.switch_b

# ============================================
# UTILITY FUNCTIONS
# ============================================

def show_message(text, color=(255, 255, 255)):
    """Display a text message on the screen"""
    display.set_pen(display.create_pen(0, 0, 0))
    display.clear()
    display.set_pen(display.create_pen(*color))
    display.text(text, 5, HEIGHT // 2 - 4, scale=1)
    display.update()


def show_error(text):
    """Display an error message (red)"""
    show_message(text, color=(255, 0, 0))


def show_info(text):
    """Display an info message (blue)"""
    show_message(text, color=(0, 128, 255))


def blink_led(times=3, delay=0.2):
    """Blink the onboard LED"""
    led = machine.Pin("LED", machine.Pin.OUT)
    for _ in range(times):
        led.on()
        time.sleep(delay)
        led.off()
        time.sleep(delay)


# ============================================
# NETWORK FUNCTIONS
# ============================================

def connect_wifi():
    """Connect to WiFi network"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print(f"Already connected: {wlan.ifconfig()[0]}")
        return True
    
    print(f"Connecting to WiFi: {WIFI_SSID}")
    show_info("WiFi...")
    
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    # Wait for connection
    timeout = WIFI_TIMEOUT
    while timeout > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        timeout -= 1
        time.sleep(1)
        print(".", end="")
    
    print()
    
    if wlan.status() != 3:
        show_error("WiFi Failed")
        print(f"WiFi connection failed (status: {wlan.status()})")
        return False
    else:
        ip = wlan.ifconfig()[0]
        print(f"Connected! IP: {ip}")
        show_info(f"IP:{ip[-8:]}")  # Show last 8 chars of IP
        time.sleep(2)
        blink_led(2)
        return True


# ============================================
# IMAGE FETCHING & RENDERING
# ============================================

def fetch_and_display():
    """
    Fetch RGB image from server and display it
    
    Returns:
        int: Dwell time in seconds (how long to show this image)
    """
    url = f"{SERVER_URL}/{DEVICE_ID}/next_rgb"
    
    try:
        # Show activity indicator
        # blink_led(1, 0.1)
        
        print(f"Fetching: {url}")
        response = urequests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"HTTP Error: {response.status_code}")
            response.close()
            return 15  # Default dwell time
        
        # Parse headers
        dwell_secs = int(response.headers.get('Tronbyt-Dwell-Secs', '15'))
        brightness = int(response.headers.get('Tronbyt-Brightness', '50'))
        width = int(response.headers.get('X-Image-Width', str(WIDTH)))
        height = int(response.headers.get('X-Image-Height', str(HEIGHT)))
        
        print(f"Image: {width}x{height}, Dwell: {dwell_secs}s, Brightness: {brightness}%")
        
        # Validate dimensions
        if width != WIDTH or height != HEIGHT:
            print(f"Warning: Image size mismatch (expected {WIDTH}x{HEIGHT})")
        
        # Get raw RGB data
        rgb_data = response.content
        expected_size = width * height * 3  # 3 bytes per pixel (RGB)
        
        if len(rgb_data) != expected_size:
            print(f"Warning: Data size mismatch (expected {expected_size}, got {len(rgb_data)})")
        
        # Set brightness (0-100 scale to 0.0-1.0)
        display.set_backlight(brightness / 100.0)
        
        # Render to display
        # RGB data is packed as R,G,B bytes (3 bytes per pixel, row-major order)
        offset = 0
        for y in range(min(height, HEIGHT)):
            for x in range(min(width, WIDTH)):
                if offset + 2 < len(rgb_data):
                    r = rgb_data[offset]
                    g = rgb_data[offset + 1]
                    b = rgb_data[offset + 2]
                    offset += 3
                    
                    # Create pen and set pixel
                    color = display.create_pen(r, g, b)
                    display.set_pen(color)
                    display.pixel(x, y)
        
        # Update display
        display.update()
        
        # Clean up
        response.close()
        gc.collect()  # Force garbage collection to free memory
        
        print(f"Displayed. Memory free: {gc.mem_free()} bytes")
        
        return dwell_secs
        
    except OSError as e:
        print(f"Network error: {e}")
        show_error("Network Err")
        time.sleep(2)
        return 15
        
    except Exception as e:
        print(f"Error fetching image: {e}")
        show_error("Fetch Error")
        time.sleep(2)
        return 15


# ============================================
# MAIN LOOP
# ============================================

def main():
    """Main application loop"""
    
    # Connect to WiFi
    retry_count = 0
    while retry_count < MAX_RETRIES:
        if connect_wifi():
            break
        retry_count += 1
        print(f"Retry {retry_count}/{MAX_RETRIES} in {RETRY_DELAY}s...")
        time.sleep(RETRY_DELAY)
    else:
        show_error("No WiFi")
        print("Failed to connect to WiFi. Halting.")
        return
    
    print(f"\nFetching from: {SERVER_URL}/{DEVICE_ID}")
    print("Press Button A to force refresh")
    print("Press Button B to reconnect WiFi")
    print("-" * 50)
    
    # Main loop
    last_fetch_time = 0
    dwell_secs = 15
    
    while True:
        current_time = time.time()
        
        # Check buttons
        if button_a.is_pressed:
            print("Button A pressed - forcing refresh")
            last_fetch_time = 0
            time.sleep(0.3)  # Debounce
        
        if button_b.is_pressed:
            print("Button B pressed - reconnecting WiFi")
            connect_wifi()
            last_fetch_time = 0
            time.sleep(0.3)  # Debounce
        
        # Fetch new image if dwell time has elapsed
        if current_time - last_fetch_time >= dwell_secs:
            try:
                dwell_secs = fetch_and_display()
                last_fetch_time = current_time
            except Exception as e:
                print(f"Unexpected error: {e}")
                show_error("Error!")
                time.sleep(5)
        
        # Small delay to prevent tight looping
        time.sleep(0.1)


# ============================================
# ENTRY POINT
# ============================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user")
        show_info("Stopped")
    except Exception as e:
        print(f"\nFatal error: {e}")
        show_error("Fatal Err")
        raise
