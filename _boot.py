# Tronbyt RP2350 Frozen Boot Module (_boot.py)
# This is the FIRST code to run - mounted as frozen module
# It mounts the filesystem, then launches the main application

import sys
import machine

# Early debug - this MUST print to serial
print("\n" + "="*60)
print("TRONBYT RP2350 BOOT")
print("="*60)
print("[BOOT] _boot.py starting...")

# Mount filesystem
try:
    print("[BOOT] Mounting filesystem...")
    import os
    from flashbdev import bdev
    
    try:
        vfs = os.VfsLFS2(bdev)
        os.mount(vfs, '/')
        print("[BOOT] Filesystem mounted successfully")
    except Exception as e:
        print(f"[BOOT] Filesystem mount failed: {e}")
        print("[BOOT] Attempting filesystem creation...")
        try:
            os.VfsLFS2.mkfs(bdev)
            vfs = os.VfsLfs2(bdev)
            os.mount(vfs, '/')
            print("[BOOT] Filesystem created and mounted")
        except Exception as e2:
            print(f"[BOOT] Filesystem creation failed: {e2}")
            sys.print_exception(e2)
except ImportError as e:
    print(f"[BOOT] Filesystem module import error: {e}")
except Exception as e:
    print(f"[BOOT] Unexpected error mounting filesystem: {e}")
    sys.print_exception(e)

# Now check if there's a boot.py on the filesystem and run it
print("[BOOT] Checking for filesystem boot.py...")
try:
    import os
    files = os.listdir('/')
    print(f"[BOOT] Filesystem contents: {files}")
    
    if 'boot.py' in files:
        print("[BOOT] Executing filesystem boot.py...")
        try:
            with open('boot.py', 'r') as f:
                code = f.read()
            exec(code)
            print("[BOOT] Filesystem boot.py completed")
        except Exception as e:
            print(f"[BOOT] Error in filesystem boot.py: {e}")
            sys.print_exception(e)
    else:
        print("[BOOT] No filesystem boot.py found")
except Exception as e:
    print(f"[BOOT] Error checking filesystem: {e}")
    sys.print_exception(e)

# Finally, launch main.py from filesystem or frozen
print("[BOOT] Preparing to launch main application...")
try:
    # Try filesystem main.py first
    import os
    try:
        files = os.listdir('/')
        if 'main.py' in files:
            print("[BOOT] Found main.py on filesystem, executing...")
            with open('main.py', 'r') as f:
                code = f.read()
            exec(code)
        else:
            print("[BOOT] No main.py on filesystem, trying frozen...")
            import main
            print("[BOOT] Frozen main module imported successfully")
    except NameError:
        # os not available, try frozen main directly
        print("[BOOT] Filesystem not available, using frozen main...")
        import main
        print("[BOOT] Frozen main module imported successfully")
except Exception as e:
    print("="*60)
    print("CRITICAL ERROR: Failed to start main application")
    print("="*60)
    print(f"Error: {e}")
    sys.print_exception(e)
    print("\n[BOOT] Entering emergency mode - system halted")
    print("Connect to serial console and check errors above")
    print("="*60)
    
    # Blink onboard LED to indicate error
    try:
        led = machine.Pin("LED", machine.Pin.OUT)
        while True:
            led.value(1)
            machine.sleep_ms(200)
            led.value(0)
            machine.sleep_ms(200)
    except:
        while True:
            machine.sleep_ms(1000)
