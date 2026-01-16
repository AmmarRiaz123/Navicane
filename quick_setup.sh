#!/bin/bash

echo "========================================"
echo "Smart Cane Quick Setup"
echo "Raspberry Pi OS 64-bit"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Do not run as root!${NC}"
    echo "Run as: ./quick_setup.sh"
    exit 1
fi

# Install system packages
echo -e "${YELLOW}Installing system packages...${NC}"
sudo apt update
sudo apt install -y python3-opencv python3-numpy python3-picamera2 \
                    espeak python3-rpi.gpio libcamera-apps python3-pip

echo ""
echo -e "${YELLOW}Verifying installations...${NC}"

# Verify OpenCV
python3 -c "import cv2; print('✓ OpenCV version:', cv2.__version__)" 2>/dev/null && \
    echo -e "${GREEN}OpenCV: OK${NC}" || \
    echo -e "${RED}OpenCV: FAILED${NC}"

# Verify NumPy
python3 -c "import numpy; print('✓ NumPy version:', numpy.__version__)" 2>/dev/null && \
    echo -e "${GREEN}NumPy: OK${NC}" || \
    echo -e "${RED}NumPy: FAILED${NC}"

# Verify picamera2
python3 -c "from picamera2 import Picamera2; print('✓ picamera2: OK')" 2>/dev/null && \
    echo -e "${GREEN}picamera2: OK${NC}" || \
    echo -e "${RED}picamera2: FAILED${NC}"

# Verify GPIO
python3 -c "import RPi.GPIO; print('✓ RPi.GPIO: OK')" 2>/dev/null && \
    echo -e "${GREEN}RPi.GPIO: OK${NC}" || \
    echo -e "${RED}RPi.GPIO: FAILED${NC}"

# Verify espeak
espeak "Setup check" 2>/dev/null && \
    echo -e "${GREEN}espeak: OK${NC}" || \
    echo -e "${RED}espeak: FAILED${NC}"

echo ""
echo -e "${YELLOW}Testing camera...${NC}"
timeout 3 rpicam-hello 2>/dev/null && \
    echo -e "${GREEN}Camera: OK${NC}" || \
    echo -e "${RED}Camera: FAILED - check connection${NC}"

echo ""
echo -e "${YELLOW}Installing pip packages...${NC}"
pip3 install -r requirements.txt --break-system-packages 2>/dev/null || \
    pip3 install -r requirements.txt

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Download AI models:"
echo "     mkdir -p ~/models"
echo "     cd ~/models"
echo "     wget https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/MobileNetSSD_deploy.prototxt"
echo "     wget https://github.com/chuanqi305/MobileNet-SSD/raw/master/MobileNetSSD_deploy.caffemodel"
echo ""
echo "  2. Test components:"
echo "     python3 ultrasonic.py"
echo "     python3 vibration.py"
echo "     python3 speech.py"
echo "     python3 camera.py"
echo ""
echo "  3. Run system:"
echo "     python3 main.py"
