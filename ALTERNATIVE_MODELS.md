# Alternative Object Detection Models

If MobileNet SSD download fails, here are working alternatives:

---

## Option 1: OpenCV Zoo ONNX (RECOMMENDED - Easiest)

**Pros:** Guaranteed to work, fast, no dependencies  
**Cons:** None

### Download:

```bash
cd ~/models

# Object detection model (ONNX format)
wget https://github.com/opencv/opencv_zoo/raw/master/models/object_detection_mobilenet/object_detection_mobilenet_2022apr.onnx \
     -O mobilenet_ssd.onnx
```

### Update config.py:

```python
MODEL_PATH = '/home/pi/models/mobilenet_ssd.onnx'
PROTOTXT_PATH = ''  # Not needed for ONNX
```

Camera.py will auto-detect ONNX format and load it correctly!

---

## Option 2: YOLOv4-tiny (Better Accuracy)

**Pros:** Better accuracy than MobileNet, fast  
**Cons:** Slightly larger file

### Download:

```bash
cd ~/models

# YOLOv4-tiny model
wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights
wget https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg
wget https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/coco.names
```

### Update config.py:

```python
MODEL_PATH = '/home/pi/models/yolov4-tiny.weights'
PROTOTXT_PATH = '/home/pi/models/yolov4-tiny.cfg'
```

Camera.py will auto-detect Darknet format!

---

## Option 3: OpenCV Face Detector (Fallback)

**Pros:** Pre-installed with OpenCV, zero download  
**Cons:** Only detects faces, not general objects

### No download needed!

```python
# Use OpenCV's built-in face detector
detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)
```

---

## Comparison Table

| Model | Size | Speed | Objects | Download Difficulty |
|-------|------|-------|---------|---------------------|
| **OpenCV Zoo ONNX** ✅ | 9MB | Fast | 80 classes | ⭐ Very Easy |
| YOLOv4-tiny | 23MB | Fast | 80 classes | ⭐ Easy |
| MobileNet SSD (Caffe) | 23MB | Fast | 20 classes | ❌ Hard (404 errors) |
| OpenCV Face | 0MB | Fastest | Faces only | ⭐ Pre-installed |

---

## Quick Switch Instructions

The camera.py already supports multiple formats automatically!

Just update config.py:

### For ONNX models:

```python
MODEL_PATH = '/home/pi/models/model_name.onnx'
PROTOTXT_PATH = ''  # Leave empty
```

### For Darknet (YOLO):

```python
MODEL_PATH = '/home/pi/models/yolov4-tiny.weights'
PROTOTXT_PATH = '/home/pi/models/yolov4-tiny.cfg'
```

### For Caffe:

```python
MODEL_PATH = '/home/pi/models/MobileNetSSD_deploy.caffemodel'
PROTOTXT_PATH = '/home/pi/models/MobileNetSSD_deploy.prototxt'
```

---

## Recommended Download Command (OpenCV Zoo)

**This is the easiest and most reliable option:**

```bash
cd ~/models
wget https://github.com/opencv/opencv_zoo/raw/master/models/object_detection_mobilenet/object_detection_mobilenet_2022apr.onnx -O mobilenet_ssd.onnx
```

Then update config.py:

```python
MODEL_PATH = '/home/pi/models/mobilenet_ssd.onnx'
PROTOTXT_PATH = ''
```

That's it! No code changes needed, camera.py will detect and use ONNX format automatically.

---

## Manual Download Sources

If wget fails, manually download from these working links:

### OpenCV Zoo (Recommended)
- Direct link: https://github.com/opencv/opencv_zoo/raw/master/models/object_detection_mobilenet/object_detection_mobilenet_2022apr.onnx
- Download and save as `mobilenet_ssd.onnx` in `~/models/`

### YOLOv4-tiny
- Weights: https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights
- Config: https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg
- Names: https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/coco.names

---

## Testing Your Model

After downloading:

```bash
cd ~/Navicane
python3 camera.py
```

Should show:
- Model loading successfully
- Detected objects printed to console
- Saved `test_detection.jpg` with bounding boxes

---

## Troubleshooting

### "Failed to load model" error

1. Check file exists:
   ```bash
   ls -lh ~/models/
   ```

2. Verify MODEL_PATH in config.py matches actual filename

3. Try different model format (ONNX recommended)

### "No module named 'cv2'" error

```bash
sudo apt install python3-opencv
python3 -c "import cv2; print(cv2.__version__)"
```

### Camera opens but no detections

- Lower CONFIDENCE_THRESHOLD in config.py (try 0.3)
- Point camera at well-lit objects
- Check model supports object class (person, chair, etc.)

---

## Need Help?

Check logs:
```bash
tail -f ~/Navicane/smart_cane.log
```

Or run camera test standalone:
```bash
cd ~/Navicane
python3 camera.py
```
