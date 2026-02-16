# Makefile for Tronbyt Interstate 75W Client

# Configuration
MICROPYTHON_DIR ?= ../micropython
BOARD ?= PIMORONI_INTERSTATE75W
PORT ?= /dev/ttyACM0

# Paths
PROJECT_DIR := $(shell pwd)
MODULE_DIR := $(PROJECT_DIR)/webpdec
BUILD_DIR := $(MICROPYTHON_DIR)/ports/rp2/build-$(BOARD)

.PHONY: all clean flash deploy setup help

help:
	@echo "Tronbyt Interstate 75W Build System"
	@echo ""
	@echo "Targets:"
	@echo "  setup       - Clone and setup MicroPython"
	@echo "  firmware    - Build custom firmware with webpdec module"
	@echo "  flash       - Flash firmware to device"
	@echo "  deploy      - Copy Python files to device"
	@echo "  all         - Build and flash everything"
	@echo "  clean       - Clean build artifacts"
	@echo ""
	@echo "Variables:"
	@echo "  MICROPYTHON_DIR - Path to MicroPython repo (default: ../micropython)"
	@echo "  BOARD           - Board type (default: PIMORONI_INTERSTATE75W)"
	@echo "  PORT            - Serial port (default: /dev/ttyACM0)"

setup:
	@echo "Setting up MicroPython..."
	@if [ ! -d "$(MICROPYTHON_DIR)" ]; then \
		git clone https://github.com/micropython/micropython.git $(MICROPYTHON_DIR); \
	fi
	cd $(MICROPYTHON_DIR) && git submodule update --init
	cd $(MICROPYTHON_DIR)/mpy-cross && make
	@echo "MicroPython setup complete!"

firmware:
	@echo "Building firmware with webpdec module..."
	@mkdir -p $(MICROPYTHON_DIR)/ports/rp2/modules
	@cp -r $(MODULE_DIR) $(MICROPYTHON_DIR)/ports/rp2/modules/
	cd $(MICROPYTHON_DIR)/ports/rp2 && \
		make BOARD=$(BOARD) USER_C_MODULES=$(MODULE_DIR)/micropython.mk
	@echo "Firmware built: $(BUILD_DIR)/firmware.uf2"

flash: firmware
	@echo "Flashing firmware to device..."
	@echo "Put your Interstate 75W into bootloader mode (hold BOOT, tap RST)"
	@echo "Waiting for RP2350 drive..."
	@while [ ! -d "/Volumes/RP2350" ] && [ ! -d "/media/$(USER)/RP2350" ]; do \
		sleep 1; \
	done
	@if [ -d "/Volumes/RP2350" ]; then \
		cp $(BUILD_DIR)/firmware.uf2 /Volumes/RP2350/; \
	else \
		cp $(BUILD_DIR)/firmware.uf2 /media/$(USER)/RP2350/; \
	fi
	@echo "Firmware flashed! Device should reboot."

deploy:
	@echo "Deploying Python files to device..."
	@if [ ! -f "config_local.py" ]; then \
		echo "WARNING: config_local.py not found, using config.py"; \
		mpremote cp config.py :config.py; \
	else \
		mpremote cp config_local.py :config_local.py; \
	fi
	mpremote cp main.py :main.py
	@echo "Files deployed!"

all: firmware flash deploy
	@echo "Build complete! Device should start running."

clean:
	@echo "Cleaning build artifacts..."
	cd $(MICROPYTHON_DIR)/ports/rp2 && make BOARD=$(BOARD) clean
	rm -rf $(MICROPYTHON_DIR)/ports/rp2/modules/webpdec
	@echo "Clean complete!"

# Development helpers
repl:
	mpremote repl

reset:
	mpremote reset

ls:
	mpremote fs ls

test:
	@echo "Running basic tests..."
	mpremote exec "import main; print('Import successful')"
