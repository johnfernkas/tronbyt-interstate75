#!/bin/bash
#
# Tronbyt + Interstate 75W Quick Start Script
# This script helps you get started with the Tronbyt RGB bridge
#
set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Tronbyt + Interstate 75W Quick Start                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker found"
echo ""

# Navigate to RGB bridge directory
cd "$(dirname "$0")/rgb-bridge"

echo "Starting Tronbyt server and RGB bridge..."
echo ""

# Use docker-compose or docker compose depending on version
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

# Pull images
echo "📦 Pulling Docker images..."
$COMPOSE_CMD pull

# Start services
echo "🚀 Starting services..."
$COMPOSE_CMD up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check health
echo ""
echo "🏥 Checking service health..."

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Tronbyt server is running"
else
    echo "⚠️  Tronbyt server might not be ready yet (this is normal on first start)"
fi

if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ RGB bridge is running"
else
    echo "⚠️  RGB bridge might not be ready yet"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Services Started Successfully!                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Tronbyt Web UI:  http://localhost:8000"
echo "📍 RGB Bridge API:  http://localhost:8001"
echo ""
echo "Next steps:"
echo ""
echo "1. Open Tronbyt web UI: http://localhost:8000"
echo "   - Create an account"
echo "   - Add a new device (e.g., 'interstate75_1')"
echo "   - Add an app to the device (Clock, Weather, etc.)"
echo ""
echo "2. Flash Interstate 75W with MicroPython"
echo "   - Download firmware: https://github.com/pimoroni/interstate75/releases"
echo "   - Hold BOOT button, plug in USB, release BOOT"
echo "   - Drag .uf2 file onto the drive"
echo ""
echo "3. Upload client code to Interstate 75W"
echo "   - Edit interstate75-client/main.py with your WiFi and server IP"
echo "   - Use Thonny to upload: https://thonny.org/"
echo "   - Reset the device"
echo ""
echo "4. Enjoy your Tronbyt display!"
echo ""
echo "📚 Full documentation: ./README.md"
echo ""
echo "To view logs:"
echo "  $COMPOSE_CMD logs -f"
echo ""
echo "To stop services:"
echo "  $COMPOSE_CMD down"
echo ""
