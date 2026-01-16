#!/bin/bash

# Smart Cane Installation Script for Raspberry Pi OS 64-bit

set -e

echo "======================================"
echo "Smart Cane Installation Script"
echo "Raspberry Pi OS 64-bit (Debian Trixie)"
echo "======================================"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root: sudo ./install.sh"
    exit 1
fi

# Detect user (not root)
ACTUAL_USER=${SUDO_USER:-$USER}
USER_HOME=$(eval echo ~$ACTUAL_USER)

echo "Installing for user: $ACTUAL_USER"
echo "Home directory: $USER_HOME"
echo

# Update system
echo "Updating system..."
apt-get update -y
apt-get upgrade -y

# Install system dependencies (CRITICAL for arm64!)
echo "Installing system dependencies via apt..."
echo "This installs OpenCV, NumPy, and other heavy packages that won't build via pip on arm64"
apt-get install -y \
    python3-opencv \
    python3-numpy \
    python3-pip \
    python3-dev \
    python3-rpi.gpio \
    espeak \
    libcamera-apps \
    git

# Verify critical packages
echo ""
echo "Verifying system packages..."
python3 -c "import cv2; print('✓ OpenCV version:', cv2.__version__)" || { echo "✗ OpenCV not found!"; exit 1; }
python3 -c "import numpy; print('✓ NumPy version:', numpy.__version__)" || { echo "✗ NumPy not found!"; exit 1; }
python3 -c "import RPi.GPIO; print('✓ RPi.GPIO installed')" || { echo "✗ RPi.GPIO not found!"; exit 1; }
espeak "Installation check" 2>/dev/null && echo "✓ espeak working" || echo "⚠ espeak may have issues"
echo ""

# Install minimal Python packages via pip
echo "Installing Python packages via pip..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    # Install using --break-system-packages for Raspberry Pi OS Bookworm+
    sudo -u $ACTUAL_USER pip3 install -r "$SCRIPT_DIR/requirements.txt" --break-system-packages || \
    sudo -u $ACTUAL_USER pip3 install -r "$SCRIPT_DIR/requirements.txt"
else
    echo "⚠ requirements.txt not found, skipping pip install"
fi

# Enable camera
echo "Enabling camera interface..."
raspi-config nonint do_camera 0 || echo "⚠ Camera enable may have failed, check manually"

# Create directories
INSTALL_DIR="$USER_HOME/smart_cane"
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$USER_HOME/models"

# Copy files
echo "Copying project files from $SCRIPT_DIR"

for file in main.py camera.py ultrasonic.py vibration.py speech.py config.py utils.py; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        cp "$SCRIPT_DIR/$file" "$INSTALL_DIR/"
        echo "  ✓ Copied $file"
    else
        echo "  ⚠ $file not found"
    fi
done

# Copy requirements.txt for reference
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"
fi

# Set ownership
chown -R $ACTUAL_USER:$ACTUAL_USER "$INSTALL_DIR"
chown -R $ACTUAL_USER:$ACTUAL_USER "$USER_HOME/models"

# Download model
echo "Downloading object detection model..."
cd "$USER_HOME/models"

if [ ! -f "MobileNetSSD_deploy.prototxt" ]; then
    echo "  Downloading prototxt..."
    sudo -u $ACTUAL_USER wget -q --show-progress \
        https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/MobileNetSSD_deploy.prototxt || \
        echo "  ⚠ Prototxt download failed, download manually"
fi

if [ ! -f "MobileNetSSD_deploy.caffemodel" ]; then
    echo "  Downloading caffemodel (this may take a while)..."
    sudo -u $ACTUAL_USER wget -q --show-progress \
        https://github.com/chuanqi305/MobileNet-SSD/raw/master/MobileNetSSD_deploy.caffemodel || \
        echo "  ⚠ Caffemodel download failed, download manually"
fi

# Verify downloads
if [ -f "MobileNetSSD_deploy.prototxt" ] && [ -f "MobileNetSSD_deploy.caffemodel" ]; then
    echo "  ✓ Model files downloaded successfully"
else
    echo "  ⚠ Model files incomplete, object detection may not work"
fi

# Update config with correct paths
echo "Updating configuration..."
sed -i "s|/home/pi/models|$USER_HOME/models|g" "$INSTALL_DIR/config.py"
sed -i "s|/home/pi/smart_cane.log|$INSTALL_DIR/smart_cane.log|g" "$INSTALL_DIR/config.py"

# Install systemd service
echo "Installing systemd service..."
cat > /etc/systemd/system/smart-cane.service << EOF
[Unit]
Description=Smart Cane System for Blind Users
After=multi-user.target network.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/usr/bin/python3 $INSTALL_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=append:$INSTALL_DIR/smart_cane.log
StandardError=append:$INSTALL_DIR/smart_cane.log

[Install]
WantedBy=multi-user.target
EOF

# Add user to gpio group
echo "Adding $ACTUAL_USER to gpio group..."
usermod -a -G gpio $ACTUAL_USER

# Reload systemd
systemctl daemon-reload

# Enable service (but don't start yet)
systemctl enable smart-cane.service

echo
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo
echo "✓ System dependencies installed via apt"
echo "✓ Python packages installed via pip"
echo "✓ Camera interface enabled"
echo "✓ Object detection model downloaded"
echo "✓ Auto-start service configured"
echo
echo "Next steps:"
echo
echo "1. Connect hardware (sensors, motors, camera)"
echo "   - See WIRING.md for pin connections"
echo
echo "2. Test individual components:"
echo "   cd $INSTALL_DIR"
echo "   python3 ultrasonic.py"
echo "   python3 vibration.py"
echo "   python3 speech.py"
echo "   python3 camera.py"
echo
echo "3. Test complete system:"
echo "   python3 main.py"
echo
echo "4. Start auto-start service:"
echo "   sudo systemctl start smart-cane.service"
echo
echo "5. Check service status:"
echo "   sudo systemctl status smart-cane.service"
echo
echo "6. View logs:"
echo "   tail -f $INSTALL_DIR/smart_cane.log"
echo
echo "⚠ IMPORTANT: A reboot is recommended to apply all changes"
echo "   sudo reboot"
echo
