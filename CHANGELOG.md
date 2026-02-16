# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- Full libwebp integration for production use
- OTA firmware updates
- Multiple display size support
- Image caching
- FPS display in debug mode
- Configuration via web interface

## [0.1.0] - 2026-02-15

### Added
- Initial release
- MicroPython firmware for Interstate 75W (RP2350)
- WiFi connectivity
- HTTP client for Tronbyt server
- WebP decoder module (placeholder implementation)
- Configurable display settings
- Automatic brightness control from server headers
- Error handling and retry logic
- RGB565 display output
- Build system with Makefile
- Comprehensive documentation
- Example scripts
- Test utilities

### Features
- **Hardware Support**
  - Pimoroni Interstate 75W (RP2350)
  - 64x32 HUB75 LED matrices
  
- **Connectivity**
  - WiFi (2.4GHz)
  - HTTP/1.1 client
  - Configurable update intervals
  
- **Display**
  - RGB565 color format
  - Brightness control (0-100)
  - Text message display
  
- **Configuration**
  - Simple Python config files
  - Local override support (config_local.py)
  - Debug mode
  
- **Build System**
  - Makefile for easy building
  - Automated firmware compilation
  - Module integration

### Documentation
- README.md with quick start guide
- BUILD.md with detailed build instructions
- API.md with full API documentation
- Example configurations
- Test scripts

### Known Limitations
- WebP decoder is currently a placeholder (test pattern)
- Requires manual firmware build for WebP support
- Only supports 64x32 displays (configurable)
- No OTA updates yet
- Limited error recovery

## [0.0.1] - 2026-02-15

### Added
- Project structure created
- Basic documentation
- Placeholder code

[Unreleased]: https://github.com/johnfernkas/tronbyt-interstate75/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/johnfernkas/tronbyt-interstate75/releases/tag/v0.1.0
[0.0.1]: https://github.com/johnfernkas/tronbyt-interstate75/releases/tag/v0.0.1
