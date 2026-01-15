#!/bin/bash

# Smart Cane Installation Script

set -e

echo "======================================"
echo "Smart Cane Installation Script"
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

# Install dependencies
echo "Installing dependencies..."
apt-get install -y python3-pip python3-opencv espeak git

# Install Python packages
echo "Installing Python packages..."
pip3 install RPi.GPIO numpy

# Enable camera
echo "Enabling camera interface..."
raspi-config nonint do_camera 0

# Create directory
INSTALL_DIR="$USER_HOME/smart_cane"
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$USER_HOME/models"

# Copy files (assumes script is in source directory)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Copying files from $SCRIPT_DIR"

cp "$SCRIPT_DIR/main.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/camera.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/ultrasonic.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/vibration.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/speech.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/config.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/utils.py" "$INSTALL_DIR/"

# Set ownership
chown -R $ACTUAL_USER:$ACTUAL_USER "$INSTALL_DIR"
chown -R $ACTUAL_USER:$ACTUAL_USER "$USER_HOME/models"

# Download model
echo "Downloading object detection model..."
cd "$USER_HOME/models"

if [ ! -f "MobileNetSSD_deploy.prototxt" ]; then
    sudo -u $ACTUAL_USER wget -q https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/MobileNetSSD_deploy.prototxt
fi

if [ ! -f "MobileNetSSD_deploy.caffemodel" ]; then
    sudo -u $ACTUAL_USER wget -q https://github.com/chuanqi305/MobileNet-SSD/raw/master/MobileNetSSD_deploy.caffemodel
fi

# Update config with correct paths
sed -i "s|/home/pi/models|$USER_HOME/models|g" "$INSTALL_DIR/config.py"

# Install systemd service
echo "Installing systemd service..."
cat > /etc/systemd/system/smart-cane.service << EOF
[Unit]
Description=Smart Cane System for Blind Users
After=multi-user.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=append:$INSTALL_DIR/smart_cane.log
StandardError=append:$INSTALL_DIR/smart_cane.log

[Install]
WantedBy=multi-user.target
EOF

# Add user to gpio group
usermod -a -G gpio $ACTUAL_USER

# Reload systemd
systemctl daemon-reload

# Enable service
systemctl enable smart-cane.service

echo
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo
echo "To start the service now:"
echo "  sudo systemctl start smart-cane.service"
echo
echo "To check status:"
echo "  sudo systemctl status smart-cane.service"
echo
echo "To view logs:"
echo "  tail -f $INSTALL_DIR/smart_cane.log"
echo
echo "To test manually:"
echo "  cd $INSTALL_DIR"
echo "  python3 main.py"
echo
echo "A reboot is recommended to apply all changes."
echo
