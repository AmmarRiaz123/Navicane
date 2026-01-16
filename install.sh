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
echo "Installing system dependencies..."
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
echo "Verifying installations..."
python3 -c "import cv2; print('✓ OpenCV:', cv2.__version__)" || { echo "✗ OpenCV failed"; exit 1; }
python3 -c "import numpy; print('✓ NumPy:', numpy.__version__)" || { echo "✗ NumPy failed"; exit 1; }
python3 -c "import RPi.GPIO; print('✓ GPIO OK')" || { echo "✗ GPIO failed"; exit 1; }
espeak "Check" 2>/dev/null && echo "✓ espeak OK" || echo "⚠ espeak issues"
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

# Try OpenCV Zoo ONNX model first (most reliable)
echo "  Trying OpenCV Zoo ONNX model..."
if sudo -u $ACTUAL_USER wget -q --show-progress --timeout=30 --tries=2 \
    https://github.com/opencv/opencv_zoo/raw/master/models/object_detection_mobilenet/object_detection_mobilenet_2022apr.onnx \
    -O mobilenet_ssd.onnx 2>/dev/null; then
    
    # Check if file is not empty
    if [ -s "mobilenet_ssd.onnx" ]; then
        echo "  ✓ ONNX model downloaded successfully"
        
        # Update config to use ONNX model
        sed -i "s|MODEL_PATH = '.*'|MODEL_PATH = '$USER_HOME/models/mobilenet_ssd.onnx'|g" "$INSTALL_DIR/config.py"
        sed -i "s|PROTOTXT_PATH = '.*'|PROTOTXT_PATH = ''|g" "$INSTALL_DIR/config.py"
        
        SUCCESS=1
    else
        echo "  ⚠ ONNX download incomplete (0 bytes)"
        rm -f mobilenet_ssd.onnx
        SUCCESS=0
    fi
else
    echo "  ⚠ ONNX download failed"
    rm -f mobilenet_ssd.onnx  # Remove empty file if created
    SUCCESS=0
fi

# Fallback: Try YOLOv4-tiny
if [ $SUCCESS -eq 0 ]; then
    echo "  Trying YOLOv4-tiny as fallback..."
    
    # Download weights
    if sudo -u $ACTUAL_USER wget -q --show-progress --timeout=60 \
        https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights 2>/dev/null && \
       sudo -u $ACTUAL_USER wget -q --show-progress --timeout=30 \
        https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg 2>/dev/null && \
       sudo -u $ACTUAL_USER wget -q --show-progress --timeout=30 \
        https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/coco.names 2>/dev/null; then
        
        # Verify files are not empty
        if [ -s "yolov4-tiny.weights" ] && [ -s "yolov4-tiny.cfg" ]; then
            echo "  ✓ YOLOv4-tiny downloaded successfully"
            
            # Update config to use YOLO model
            sed -i "s|MODEL_PATH = '.*'|MODEL_PATH = '$USER_HOME/models/yolov4-tiny.weights'|g" "$INSTALL_DIR/config.py"
            sed -i "s|PROTOTXT_PATH = '.*'|PROTOTXT_PATH = '$USER_HOME/models/yolov4-tiny.cfg'|g" "$INSTALL_DIR/config.py"
            
            SUCCESS=1
        else
            echo "  ⚠ YOLOv4-tiny download incomplete"
            SUCCESS=0
        fi
    else
        echo "  ⚠ YOLOv4-tiny download failed"
        SUCCESS=0
    fi
fi

# Verify downloads
if [ $SUCCESS -eq 1 ]; then
    echo "  ✓ Model files downloaded successfully"
    ls -lh "$USER_HOME/models"
else
    echo "  ⚠ All download attempts failed"
    echo ""
    echo "  Please download manually:"
    echo "  1. Run: bash download_models.sh"
    echo "  2. Or download from: https://github.com/opencv/opencv_zoo"
    echo "  3. Place in: $USER_HOME/models/"
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
echo "2. If model download failed, run:"
echo "   bash download_models.sh"
echo
echo "3. Test individual components:"
echo "   cd $INSTALL_DIR"
echo "   python3 ultrasonic.py"
echo "   python3 vibration.py"
echo "   python3 speech.py"
echo "   python3 camera.py"
echo
echo "4. Test complete system:"
echo "   python3 main.py"
echo
echo "5. Start auto-start service:"
echo "   sudo systemctl start smart-cane.service"
echo
echo "6. Check service status:"
echo "   sudo systemctl status smart-cane.service"
echo
echo "7. View logs:"
echo "   tail -f $INSTALL_DIR/smart_cane.log"
echo
echo "⚠ IMPORTANT: A reboot is recommended to apply all changes"
echo "   sudo reboot"
echo
