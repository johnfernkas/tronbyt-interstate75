# MicroPython module makefile for webpdec

WEBPDEC_MOD_DIR := $(USERMOD_DIR)

# Add source files
SRC_USERMOD += $(WEBPDEC_MOD_DIR)/webpdec.c

# Add include directories
CFLAGS_USERMOD += -I$(WEBPDEC_MOD_DIR)

# If using libwebp (uncomment when integrated)
# CFLAGS_USERMOD += -I$(WEBPDEC_MOD_DIR)/libwebp/src
# SRC_USERMOD += $(wildcard $(WEBPDEC_MOD_DIR)/libwebp/src/dec/*.c)
# SRC_USERMOD += $(wildcard $(WEBPDEC_MOD_DIR)/libwebp/src/dsp/*.c)
# SRC_USERMOD += $(wildcard $(WEBPDEC_MOD_DIR)/libwebp/src/utils/*.c)
