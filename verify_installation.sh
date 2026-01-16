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
python3 -c "import cv2; print('  ✓ OpenCV:', cv2.__version__)" 2>/dev/null || { echo -e "  ${RED}✗ OpenCV not found - run: sudo apt install python3-opencv${NC}"; ERRORS=$((ERRORS+1)); }
python3 -c "import numpy; print('  ✓ NumPy:', numpy.__version__)" 2>/dev/null || { echo -e "  ${RED}✗ NumPy not found - run: sudo apt install python3-numpy${NC}"; ERRORS=$((ERRORS+1)); }
python3 -c "import RPi.GPIO; print('  ✓ RPi.GPIO installed')" 2>/dev/null || { echo -e "  ${RED}✗ RPi.GPIO not found - run: sudo apt install python3-rpi.gpio${NC}"; ERRORS=$((ERRORS+1)); }

echo ""
echo "Checking camera (rpicam-based system)..."
timeout 3 rpicam-hello 2>/dev/null && echo -e "  ${GREEN}✓ Camera working (rpicam-hello)${NC}" || echo -e "  ${YELLOW}⚠ Camera may not be connected${NC}"

echo ""
echo "Checking model files..."
if [ -f "$HOME/models/yolov4-tiny.weights" ] && [ -s "$HOME/models/yolov4-tiny.weights" ]; then
    SIZE=$(du -h "$HOME/models/yolov4-tiny.weights" | cut -f1)
    echo -e "  ${GREEN}✓ yolov4-tiny.weights ($SIZE)${NC}"
else
    echo -e "  ${RED}✗ yolov4-tiny.weights missing or empty${NC}"
    ERRORS=$((ERRORS+1))
fi

[ -f "$HOME/models/yolov4-tiny.cfg" ] && echo -e "  ${GREEN}✓ yolov4-tiny.cfg${NC}" || { echo -e "  ${RED}✗ yolov4-tiny.cfg missing${NC}"; ERRORS=$((ERRORS+1)); }

[ -f "$HOME/models/coco.names" ] && echo -e "  ${GREEN}✓ coco.names${NC}" || echo -e "  ${YELLOW}⚠ coco.names missing (recommended)${NC}"

# Remove empty ONNX file if exists
if [ -f "$HOME/models/mobilenet_ssd.onnx" ] && [ ! -s "$HOME/models/mobilenet_ssd.onnx" ]; then
    echo -e "  ${YELLOW}⚠ Removing empty mobilenet_ssd.onnx${NC}"
    rm "$HOME/models/mobilenet_ssd.onnx"
fi

echo ""
echo "Checking project files..."
# Check for config.py in current directory OR ~/smart_cane
CONFIG_FOUND=0
for CONFIG_PATH in "config.py" "$HOME/smart_cane/config.py" "$HOME/Navicane/config.py"; do
    if [ -f "$CONFIG_PATH" ]; then
        echo -e "  ${GREEN}✓ Found config.py at: $CONFIG_PATH${NC}"
        MODEL_PATH=$(grep "^MODEL_PATH" "$CONFIG_PATH" | cut -d"'" -f2)
        echo "  Model path: $MODEL_PATH"
        [ -f "$MODEL_PATH" ] && echo -e "  ${GREEN}✓ Model file exists${NC}" || { echo -e "  ${RED}✗ Model file not found${NC}"; ERRORS=$((ERRORS+1)); }
        CONFIG_FOUND=1
        break
    fi
done

if [ $CONFIG_FOUND -eq 0 ]; then
    echo -e "  ${RED}✗ config.py not found${NC}"
    echo -e "  ${YELLOW}  Run: cp ~/Navicane/*.py ~/smart_cane/ OR run install.sh${NC}"
    ERRORS=$((ERRORS+1))
fi

# Check for other Python modules
echo ""
echo "Checking Python modules..."
for MODULE in camera.py ultrasonic.py vibration.py speech.py main.py utils.py; do
    if [ -f "$MODULE" ] || [ -f "$HOME/smart_cane/$MODULE" ] || [ -f "$HOME/Navicane/$MODULE" ]; then
        echo -e "  ${GREEN}✓ $MODULE found${NC}"
    else
        echo -e "  ${RED}✗ $MODULE missing${NC}"
        ERRORS=$((ERRORS+1))
    fi
done

echo ""
echo "========================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Ready to run:"
    echo "  cd ~/Navicane && python3 main.py"
    echo "  OR"
    echo "  cd ~/smart_cane && python3 main.py"
else
    echo -e "${RED}✗ Found $ERRORS error(s)${NC}"
    echo ""
    echo "Quick fixes:"
    echo "  1. Copy Python files:"
    echo "     mkdir -p ~/smart_cane"
    echo "     cp ~/Navicane/*.py ~/smart_cane/"
    echo ""
    echo "  2. Download models:"
    echo "     cd ~/Navicane && bash download_models.sh"
    echo ""
    echo "  3. Install missing packages:"
    echo "     sudo apt install python3-opencv python3-numpy python3-rpi.gpio libcamera-apps espeak"
fi
echo "========================================"
