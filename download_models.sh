#!/bin/bash

echo "========================================"
echo "Smart Cane - Download AI Models"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Create models directory
MODELS_DIR="$HOME/models"
mkdir -p "$MODELS_DIR"
cd "$MODELS_DIR"

echo -e "${YELLOW}Downloading object detection model...${NC}"
echo ""

SUCCESS=0

# Method 1: OpenCV Zoo ONNX (RECOMMENDED)
echo "Method 1: OpenCV Zoo ONNX model (recommended)"
echo "Downloading from: github.com/opencv/opencv_zoo"
echo ""

wget --progress=bar:force:noscroll \
     https://github.com/opencv/opencv_zoo/raw/master/models/object_detection_mobilenet/object_detection_mobilenet_2022apr.onnx \
     -O mobilenet_ssd.onnx 2>&1

if [ -f "mobilenet_ssd.onnx" ] && [ -s "mobilenet_ssd.onnx" ]; then
    FILE_SIZE=$(du -h mobilenet_ssd.onnx | cut -f1)
    echo ""
    echo -e "${GREEN}✓ ONNX model downloaded successfully!${NC}"
    echo "  File: mobilenet_ssd.onnx"
    echo "  Size: $FILE_SIZE"
    SUCCESS=1
    
    # Update config.py if it exists
    if [ -f "$HOME/Navicane/config.py" ]; then
        echo ""
        echo "Updating config.py..."
        sed -i "s|MODEL_PATH = '.*'|MODEL_PATH = '$MODELS_DIR/mobilenet_ssd.onnx'|g" "$HOME/Navicane/config.py"
        sed -i "s|PROTOTXT_PATH = '.*'|PROTOTXT_PATH = ''|g" "$HOME/Navicane/config.py"
        echo -e "${GREEN}✓ Config updated${NC}"
    fi
fi

# Method 2: YOLOv4-tiny (fallback)
if [ $SUCCESS -eq 0 ]; then
    echo ""
    echo -e "${YELLOW}Method 2: YOLOv4-tiny (fallback)${NC}"
    echo "Downloading from: github.com/AlexeyAB/darknet"
    echo ""
    
    wget --progress=bar:force:noscroll \
         https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights 2>&1 &
    WGET_PID=$!
    
    # Show progress
    wait $WGET_PID
    
    wget --progress=bar:force:noscroll \
         https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg 2>&1
    
    wget --progress=bar:force:noscroll \
         https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/coco.names 2>&1
    
    if [ -f "yolov4-tiny.weights" ] && [ -f "yolov4-tiny.cfg" ]; then
        echo ""
        echo -e "${GREEN}✓ YOLOv4-tiny downloaded successfully!${NC}"
        ls -lh yolov4-tiny.*
        SUCCESS=1
        
        # Update config.py if it exists
        if [ -f "$HOME/Navicane/config.py" ]; then
            echo ""
            echo "Updating config.py..."
            sed -i "s|MODEL_PATH = '.*'|MODEL_PATH = '$MODELS_DIR/yolov4-tiny.weights'|g" "$HOME/Navicane/config.py"
            sed -i "s|PROTOTXT_PATH = '.*'|PROTOTXT_PATH = '$MODELS_DIR/yolov4-tiny.cfg'|g" "$HOME/Navicane/config.py"
            echo -e "${GREEN}✓ Config updated${NC}"
        fi
    fi
fi

# Method 3: Manual instructions
if [ $SUCCESS -eq 0 ]; then
    echo ""
    echo -e "${RED}✗ Automatic download failed${NC}"
    echo ""
    echo "Please download manually:"
    echo ""
    echo "Option A: Direct download (use browser)"
    echo "  1. Go to: https://github.com/opencv/opencv_zoo/tree/master/models/object_detection_mobilenet"
    echo "  2. Click: object_detection_mobilenet_2022apr.onnx"
    echo "  3. Click 'Download' button"
    echo "  4. Save to: $MODELS_DIR/mobilenet_ssd.onnx"
    echo ""
    echo "Option B: Use curl instead of wget"
    echo "  curl -L https://github.com/opencv/opencv_zoo/raw/master/models/object_detection_mobilenet/object_detection_mobilenet_2022apr.onnx -o $MODELS_DIR/mobilenet_ssd.onnx"
    echo ""
    echo "Option C: Use git to clone"
    echo "  git clone --depth 1 --filter=blob:none --sparse https://github.com/opencv/opencv_zoo.git"
    echo "  cd opencv_zoo"
    echo "  git sparse-checkout set models/object_detection_mobilenet"
    echo "  cp models/object_detection_mobilenet/object_detection_mobilenet_2022apr.onnx $MODELS_DIR/mobilenet_ssd.onnx"
else
    echo ""
    echo "========================================"
    echo -e "${GREEN}Model download complete!${NC}"
    echo "========================================"
    echo ""
    echo "Files in $MODELS_DIR:"
    ls -lh "$MODELS_DIR"
    echo ""
    echo "Next steps:"
    echo "  1. Test camera:"
    echo "     cd ~/Navicane"
    echo "     python3 camera.py"
    echo ""
    echo "  2. Run full system:"
    echo "     python3 main.py"
fi

echo ""
