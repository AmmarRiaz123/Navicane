#!/bin/bash

echo "========================================"
echo "Model Download (using curl)"
echo "========================================"
echo ""

# Create directory
mkdir -p ~/models
cd ~/models

echo "Downloading OpenCV Zoo ONNX model..."
echo ""

# Use curl with follow redirects
curl -L --progress-bar \
     https://github.com/opencv/opencv_zoo/raw/master/models/object_detection_mobilenet/object_detection_mobilenet_2022apr.onnx \
     -o mobilenet_ssd.onnx

if [ -f "mobilenet_ssd.onnx" ] && [ -s "mobilenet_ssd.onnx" ]; then
    echo ""
    echo "✓ Download successful!"
    echo ""
    echo "File: ~/models/mobilenet_ssd.onnx"
    echo "Size: $(du -h mobilenet_ssd.onnx | cut -f1)"
    echo ""
    echo "Update config.py with:"
    echo "  MODEL_PATH = '/home/pi/models/mobilenet_ssd.onnx'"
    echo "  PROTOTXT_PATH = ''"
    echo ""
    echo "Then test:"
    echo "  cd ~/Navicane"
    echo "  python3 camera.py"
else
    echo ""
    echo "✗ Download failed!"
    echo ""
    echo "Please download manually from browser:"
    echo "https://github.com/opencv/opencv_zoo/raw/master/models/object_detection_mobilenet/object_detection_mobilenet_2022apr.onnx"
    echo ""
    echo "Save as: ~/models/mobilenet_ssd.onnx"
fi
