# MicroPython Frozen Module Manifest for Tronbyt RP2350
# This manifest defines which Python modules get frozen into the firmware
# 
# CRITICAL: Use freeze() for frozen modules, not module()
# The freeze() function compiles Python files to bytecode and embeds them

# Include the base board manifest from Interstate75
include("$(PORT_DIR)/boards/manifest.py")

# Include Pimoroni common modules
include("$(PIMORONI_PICO_PATH)/micropython/modules/micropython-common-manifest.cmake")

# Freeze the _boot.py module (runs first before filesystem boot.py)
# This handles filesystem mounting and launches the main app
freeze(".", "_boot.py")

# Freeze provisioning module (used when device needs configuration)
freeze(".", "provisioning.py")

# Freeze default config (will be overridden by config_local.py on filesystem)
freeze(".", "config.py")

# NOTE: main.py is NOT frozen here - it should live on the filesystem
# so users can update it without reflashing firmware
# If main.py is frozen AND on filesystem, filesystem takes precedence
