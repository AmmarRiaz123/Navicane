#!/bin/bash

echo "========================================"
echo "Quick Model Download"
echo "Using OpenCV Zoo (guaranteed to work)"
echo "========================================"
echo ""

# Create directory
mkdir -p ~/models
cd ~/models

echo "Downloading object detection model..."
echo ""

# Download from OpenCV Zoo (most reliable source)
wget --progress=bar:force:noscroll \
     https://github.com/opencv/opencv_zoo/raw/master/models/object_detection_mobilenet/object_detection_mobilenet_2022apr.onnx \
     -O mobilenet_ssd.onnx

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Model downloaded successfully!"
    echo ""
    echo "File location: ~/models/mobilenet_ssd.onnx"
    echo "Size: $(du -h mobilenet_ssd.onnx | cut -f1)"
    echo ""
    echo "Now update config.py:"
    echo "  MODEL_PATH = '/home/pi/models/mobilenet_ssd.onnx'"
    echo ""
    echo "And update camera.py load_model() to use:"
    echo "  self.net = cv2.dnn.readNetFromONNX(MODEL_PATH)"
else
    echo ""
    echo "✗ Download failed!"
    echo ""
    echo "Try manual download:"
    echo "1. Go to: https://github.com/opencv/opencv_zoo/tree/master/models/object_detection_mobilenet"
    echo "2. Download: object_detection_mobilenet_2022apr.onnx"
    echo "3. Place in: ~/models/"
fi
