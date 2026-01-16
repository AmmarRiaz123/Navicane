#!/bin/bash

echo "========================================"
echo "Smart Cane - Model Downloader"
echo "========================================"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

MODELS_DIR="$HOME/models"
mkdir -p "$MODELS_DIR"
cd "$MODELS_DIR"

SUCCESS=0

# Try YOLOv4-tiny (most reliable for this system)
echo -e "${YELLOW}Downloading YOLOv4-tiny model...${NC}"
echo ""

wget -q --show-progress --timeout=60 \
     https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights 2>&1

wget -q --show-progress --timeout=30 \
     https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg 2>&1

wget -q --show-progress --timeout=30 \
     https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/coco.names 2>&1

if [ -s "yolov4-tiny.weights" ] && [ -s "yolov4-tiny.cfg" ] && [ -s "coco.names" ]; then
    echo ""
    echo -e "${GREEN}✓ YOLOv4-tiny downloaded successfully!${NC}"
    echo ""
    echo "Files:"
    ls -lh yolov4-tiny.* coco.names
    SUCCESS=1
    
    # Update config.py if exists
    for CONFIG_PATH in "$HOME/Navicane/config.py" "$HOME/smart_cane/config.py"; do
        if [ -f "$CONFIG_PATH" ]; then
            echo ""
            echo "Updating $CONFIG_PATH..."
            sed -i "s|MODEL_PATH = '.*'|MODEL_PATH = '$MODELS_DIR/yolov4-tiny.weights'|g" "$CONFIG_PATH"
            sed -i "s|PROTOTXT_PATH = '.*'|PROTOTXT_PATH = '$MODELS_DIR/yolov4-tiny.cfg'|g" "$CONFIG_PATH"
            echo -e "${GREEN}✓ Config updated${NC}"
        fi
    done
fi

echo ""
if [ $SUCCESS -eq 1 ]; then
    echo -e "${GREEN}Model download complete!${NC}"
    echo ""
    echo "Next: Test camera"
    echo "  cd ~/smart_cane"
    echo "  python3 camera.py"
else
    echo -e "${RED}Download failed!${NC}"
    echo ""
    echo "Manual download:"
    echo "  cd ~/models"
    echo "  curl -L https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights -o yolov4-tiny.weights"
    echo "  curl -L https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg -o yolov4-tiny.cfg"
    echo "  curl -L https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/coco.names -o coco.names"
fi
