#!/bin/bash

echo "==================================="
echo "Smart Cane Camera Setup"
echo "==================================="
echo ""

# Install picamera2 if not already installed
echo "Installing picamera2..."
sudo apt update
sudo apt install -y python3-picamera2

# Verify installation
echo ""
echo "Verifying picamera2..."
python3 -c "from picamera2 import Picamera2; print('✓ picamera2 installed successfully')" 2>/dev/null || {
    echo "✗ picamera2 installation failed"
    exit 1
}

# Test camera
echo ""
echo "Testing camera with rpicam-hello..."
timeout 3 rpicam-hello || {
    echo "✗ Camera test failed"
    exit 1
}

echo ""
echo "✓ Camera setup complete!"
echo ""
echo "To test camera with Python:"
echo "  cd ~/Navicane"
echo "  python3 camera.py"
echo ""
