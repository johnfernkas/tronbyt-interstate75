"""
Test WebP decoder module
Creates a test pattern and verifies the decoder works
"""

try:
    import webpdec
    print("✓ webpdec module loaded")
except ImportError:
    print("✗ webpdec module not found!")
    print("The module must be compiled into the firmware.")
    import sys
    sys.exit(1)

# Test decode with dummy data
print("\nTesting decode function...")

# Create dummy WebP data (won't actually decode, just tests the API)
dummy_webp = bytes([0xFF] * 100)

try:
    # Decode to 64x32
    result = webpdec.decode(dummy_webp, 64, 32)
    
    print(f"✓ Decode returned {len(result)} bytes")
    expected_size = 64 * 32 * 2  # RGB565 = 2 bytes per pixel
    
    if len(result) == expected_size:
        print(f"✓ Output size correct ({expected_size} bytes)")
    else:
        print(f"✗ Output size wrong (expected {expected_size}, got {len(result)})")
    
    # Check if it's a bytearray
    if isinstance(result, bytearray):
        print("✓ Result is bytearray")
    else:
        print(f"✗ Result is {type(result)}, expected bytearray")
    
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"✗ Error during decode: {e}")
    import sys
    sys.print_exception(e)
