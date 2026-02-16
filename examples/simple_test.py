"""
Simple test script for Interstate 75W
Tests basic display functionality without network
"""

from interstate75 import Interstate75, DISPLAY_INTERSTATE75_64X32
import time

# Initialize display
i75 = Interstate75(display=DISPLAY_INTERSTATE75_64X32)
graphics = i75.display

# Clear screen
graphics.set_pen(graphics.create_pen(0, 0, 0))
graphics.clear()

# Test colors
colors = [
    (255, 0, 0, "Red"),
    (0, 255, 0, "Green"),
    (0, 0, 255, "Blue"),
    (255, 255, 0, "Yellow"),
    (255, 0, 255, "Magenta"),
    (0, 255, 255, "Cyan"),
    (255, 255, 255, "White"),
]

for r, g, b, name in colors:
    print(f"Showing {name}")
    
    # Fill screen with color
    graphics.set_pen(graphics.create_pen(r, g, b))
    graphics.clear()
    
    # Draw text
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.text(name, 2, 12, scale=1)
    
    i75.update()
    time.sleep(2)

print("Test complete!")
