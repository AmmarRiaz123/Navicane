#!/bin/bash

echo "========================================"
echo "Smart Cane Installation Verification"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

# Check Python packages
echo "Checking Python packages..."
python3 -c "import cv2; print('  ✓ OpenCV:', cv2.__version__)" 2>/dev/null || { echo -e "  ${RED}✗ OpenCV not found${NC}"; ERRORS=$((ERRORS+1)); }
python3 -c "import numpy; print('  ✓ NumPy:', numpy.__version__)" 2>/dev/null || { echo -e "  ${RED}✗ NumPy not found${NC}"; ERRORS=$((ERRORS+1)); }
python3 -c "from picamera2 import Picamera2; print('  ✓ picamera2 installed')" 2>/dev/null || { echo -e "  ${RED}✗ picamera2 not found${NC}"; ERRORS=$((ERRORS+1)); }
python3 -c "import RPi.GPIO; print('  ✓ RPi.GPIO installed')" 2>/dev/null || { echo -e "  ${RED}✗ RPi.GPIO not found${NC}"; ERRORS=$((ERRORS+1)); }

echo ""
echo "Checking camera..."
timeout 3 rpicam-hello 2>/dev/null && echo -e "  ${GREEN}✓ Camera working${NC}" || echo -e "  ${YELLOW}⚠ Camera may not be connected${NC}"

echo ""
echo "Checking model files..."
if [ -f "$HOME/models/yolov4-tiny.weights" ]; then
    SIZE=$(du -h "$HOME/models/yolov4-tiny.weights" | cut -f1)
    if [ -s "$HOME/models/yolov4-tiny.weights" ]; then
        echo -e "  ${GREEN}✓ yolov4-tiny.weights ($SIZE)${NC}"
    else
        echo -e "  ${RED}✗ yolov4-tiny.weights is empty${NC}"
        ERRORS=$((ERRORS+1))
    fi
else
    echo -e "  ${RED}✗ yolov4-tiny.weights not found${NC}"
    ERRORS=$((ERRORS+1))
fi

if [ -f "$HOME/models/yolov4-tiny.cfg" ]; then
    echo -e "  ${GREEN}✓ yolov4-tiny.cfg${NC}"
else
    echo -e "  ${RED}✗ yolov4-tiny.cfg not found${NC}"
    ERRORS=$((ERRORS+1))
fi

if [ -f "$HOME/models/coco.names" ]; then
    echo -e "  ${GREEN}✓ coco.names${NC}"
else
    echo -e "  ${YELLOW}⚠ coco.names not found (recommended)${NC}"
fi

# Remove empty ONNX file if it exists
if [ -f "$HOME/models/mobilenet_ssd.onnx" ] && [ ! -s "$HOME/models/mobilenet_ssd.onnx" ]; then
    echo -e "  ${YELLOW}⚠ Removing empty mobilenet_ssd.onnx${NC}"
    rm "$HOME/models/mobilenet_ssd.onnx"
fi

echo ""
echo "Checking configuration..."
if [ -f "$HOME/smart_cane/config.py" ]; then
    MODEL_PATH=$(grep "^MODEL_PATH" "$HOME/smart_cane/config.py" | cut -d"'" -f2)
    echo "  Model path: $MODEL_PATH"
    
    if [ -f "$MODEL_PATH" ]; then
        echo -e "  ${GREEN}✓ Model file exists${NC}"
    else
        echo -e "  ${RED}✗ Model file not found at configured path${NC}"
        ERRORS=$((ERRORS+1))
    fi
else
    echo -e "  ${RED}✗ config.py not found${NC}"
    ERRORS=$((ERRORS+1))
fi

echo ""
echo "========================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Test components:"
    echo "     cd ~/smart_cane"
    echo "     python3 camera.py"
    echo "     python3 ultrasonic.py"
    echo "     python3 vibration.py"
    echo "     python3 speech.py"
    echo ""
    echo "  2. Run full system:"
    echo "     python3 main.py"
else
    echo -e "${RED}✗ Found $ERRORS error(s)${NC}"
    echo ""
    echo "To fix issues:"
    echo "  bash download_models.sh"
fi
echo "========================================"
