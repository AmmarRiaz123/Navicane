# Smart Cane Setup Guide

## ⚠️ Important: Raspberry Pi OS 64-bit Requirements

This project is designed for **Raspberry Pi OS 64-bit (Debian Bookworm/Trixie)** with Python 3.11+.

**Critical:** Heavy Python packages (OpenCV, NumPy) **MUST** be installed via `apt`, not `pip`, to avoid compilation errors on ARM architecture.

---

## ⚠️ Important: Camera System Constraint

**CRITICAL:** This Raspberry Pi system has a hardware/software constraint:

✅ **WORKS:** rpicam-* CLI commands (rpicam-hello, rpicam-still, rpicam-vid)  
❌ **DOES NOT WORK:** Picamera2, cv2.VideoCapture, libcamera Python bindings

The camera can **ONLY** be accessed via `rpicam-*` command-line tools. All camera functionality in this project uses `subprocess` calls to `rpicam-still` to capture frames, which are then processed by OpenCV.

**Why this limitation exists:**
- Specific Raspberry Pi OS build
- libcamera version incompatibility
- Python bindings not functional
- Direct device access hangs or fails

**How this project handles it:**
1. Camera capture: `rpicam-still` via subprocess
2. Frame processing: OpenCV reads saved images
3. Detection: Standard OpenCV DNN on captured frames

---

## Hardware Wiring

### Ultrasonic Sensors (HC-SR04)

| Sensor | VCC | GND | Trigger | Echo |
|--------|-----|-----|---------|------|
| Left   | 5V  | GND | GPIO 23 | GPIO 24 |
| Center | 5V  | GND | GPIO 17 | GPIO 27 |
| Right  | 5V  | GND | GPIO 22 | GPIO 10 |

**Important**: Use voltage divider (1kΩ + 2kΩ resistors) on Echo pins to convert 5V to 3.3V!

### Vibration Motors

| Motor  | Pin     | Ground |
|--------|---------|--------|
| Left   | GPIO 18 | GND    |
| Center | GPIO 25 | GND    |
| Right  | GPIO 8  | GND    |

**Note**: Use transistors (2N2222) if motors draw >20mA

### Camera Module

Connect Raspberry Pi Camera Module v1.3 to CSI port on Raspberry Pi.

---

## Software Installation

### Quick Install (Recommended)

```bash
# Clone repository
cd /home/pi
git clone https://github.com/AmmarRiaz123/Navicane.git
cd Navicane

# Run installation script
sudo bash install.sh
```

The script will automatically:
- Install all system dependencies via apt
- Install minimal pip packages
- Enable camera interface
- Download AI model
- Configure auto-start service

### Manual Installation

### 1. Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install System Dependencies (REQUIRED FIRST!)

**This step is critical for Raspberry Pi OS 64-bit:**

```bash
sudo apt install -y \
    python3-opencv \
    python3-numpy \
    python3-pip \
    python3-dev \
    python3-rpi.gpio \
    espeak \
    libcamera-apps \
    git
```

**DO NOT INSTALL:**
- ❌ `python3-picamera2` (not functional on this system)
- ❌ Any libcamera Python bindings

**Camera access is via rpicam-* CLI tools only!**

### 3. Verify System Packages

```bash
# Test OpenCV (for image processing only)
python3 -c "import cv2; print('OpenCV version:', cv2.__version__)"
# Test NumPy
python3 -c "import numpy; print('NumPy version:', numpy.__version__)"
# Test GPIO
python3 -c "import RPi.GPIO; print('GPIO: OK')"
# Test rpicam (CRITICAL for camera)
rpicam-hello -t 3000
# Test espeak
espeak "System check successful"
```

**Note:** We do NOT test Picamera2 because it doesn't work on this system.

All commands should execute without errors.

### 4. Enable Camera

```bash
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable
# Reboot after enabling
sudo reboot
```

### 5. Install Minimal Python Dependencies

```bash
cd /home/pi/Navicane

# Option 1: System-wide (simple, recommended for single-purpose device)
pip3 install -r requirements.txt --break-system-packages

# Option 2: Virtual environment (better isolation)
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

**Note:** The `requirements.txt` only contains `RPi.GPIO` since all other dependencies are installed via apt.

### 6. Download Object Detection Model

```bash
# Create models directory
mkdir -p /home/pi/models
cd /home/pi/models

# Download MobileNet SSD v2 model (Caffe format)
# Option 1: MobileNet SSD v2 (Recommended)
wget https://github.com/djmv/MobilNet-SSD_RealSense/raw/master/mobilenet_iter_73000.caffemodel -O MobileNetSSD_deploy.caffemodel
wget https://raw.githubusercontent.com/djmv/MobilNet-SSD_RealSense/master/MobileNetSSD_deploy.prototxt

# Option 2: Alternative - MobileNet SSD v1 (if above fails)
wget https://raw.githubusercontent.com/PINTO0309/MobileNet-SSD-RealSense/master/caffemodel/MobileNetSSD/MobileNetSSD_deploy.prototxt
wget https://raw.githubusercontent.com/PINTO0309/MobileNet-SSD-RealSense/master/caffemodel/MobileNetSSD/MobileNetSSD_deploy.caffemodel

# Option 3: Google Drive backup (use gdown)
pip3 install gdown --break-system-packages
gdown 1qSGcBHSBxzOLcKLrzk7BPYF7lEpQGJsB -O MobileNetSSD_deploy.caffemodel
gdown 1MuBB4eJkdlQh6QIg5F2GBfKGc9vUG2jc -O MobileNetSSD_deploy.prototxt

# Verify downloads
ls -lh
# Should show two files around 23MB (caffemodel) and 30KB (prototxt)
```

### 7. Install Smart Cane Code

```bash
# Copy all Python files to /home/pi/smart_cane
mkdir -p /home/pi/smart_cane
cd /home/pi/Navicane

cp *.py /home/pi/smart_cane/
cp requirements.txt /home/pi/smart_cane/
```

### 8. Test Components Individually

Test each module to verify hardware and software:

```bash
cd /home/pi/smart_cane

# Test ultrasonic sensors
python3 ultrasonic.py
# Should show distance readings from 3 sensors

# Test vibration motors
python3 vibration.py
# Motors should vibrate in left-center-right pattern

# Test speech
python3 speech.py
# Should speak test phrases

# Test camera with object detection
python3 camera.py
# Should detect objects if models are downloaded
```

---

## Auto-Start Configuration

### Create systemd Service

Create `/etc/systemd/system/smart-cane.service`:

```ini
[Unit]
Description=Smart Cane for Blind Users
After=multi-user.target network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/smart_cane
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/usr/bin/python3 /home/pi/smart_cane/main.py
Restart=always
RestartSec=10
StandardOutput=append:/home/pi/smart_cane.log
StandardError=append:/home/pi/smart_cane.log

[Install]
WantedBy=multi-user.target
```

### Enable Auto-Start

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable smart-cane.service

# Start service now
sudo systemctl start smart-cane.service

# Check status
sudo systemctl status smart-cane.service

# View logs
tail -f /home/pi/smart_cane.log
```

### Control Commands

```bash
# Start
sudo systemctl start smart-cane.service

# Stop
sudo systemctl stop smart-cane.service

# Restart
sudo systemctl restart smart-cane.service

# Disable auto-start
sudo systemctl disable smart-cane.service

# View logs in real-time
journalctl -u smart-cane -f
```

---

## Troubleshooting

### Camera Not Working

```bash
# Check if camera detected
vcgencmd get_camera
# Should show: supported=1 detected=1

# Test with libcamera
libcamera-hello --timeout 5000

# Check video device
ls -l /dev/video*

# For legacy camera stack
raspistill -o test.jpg
```

If camera still doesn't work, update config:
```bash
sudo raspi-config
# Interface Options > Legacy Camera Support > Enable
sudo reboot
```

### GPIO Permissions

```bash
# Add user to gpio group
sudo usermod -a -G gpio pi

# Verify membership
groups pi

# Reboot to apply
sudo reboot
```

### Speech Not Working

```bash
# Test espeak directly
espeak "Hello world"

# If no audio output
sudo raspi-config
# System Options > Audio > Select correct output (HDMI or headphone jack)

# Test audio system
speaker-test -t wav -c 2

# Check ALSA mixer
alsamixer
```

### ImportError: No module named 'cv2'

```bash
# This means OpenCV wasn't installed via apt
sudo apt install python3-opencv

# Verify
python3 -c "import cv2; print(cv2.__version__)"
```

### ImportError: No module named 'numpy'

```bash
# Install numpy via apt (NOT pip!)
sudo apt install python3-numpy

# Verify
python3 -c "import numpy; print(numpy.__version__)"
```

### Model Download Issues

If wget fails, manually download from browser:

- [Prototxt](https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/MobileNetSSD_deploy.prototxt)
- [Caffemodel](https://github.com/chuanqi305/MobileNet-SSD/raw/master/MobileNetSSD_deploy.caffemodel)

Place both files in `/home/pi/models/`.

### System Crashes or Freezes

```bash
# Check temperature
vcgencmd measure_temp

# If overheating, add heatsinks or reduce load
# In config.py:
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240
CAMERA_LOOP_DELAY = 1.0
```

---

## Performance Tuning

### Optimize for Speed

In `config.py`:

```python
# Reduce camera resolution
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240

# Increase loop delays if CPU overheats
CAMERA_LOOP_DELAY = 1.0  # Run vision at 1Hz instead of 2Hz

# Higher confidence threshold
CONFIDENCE_THRESHOLD = 0.6
```

### Reduce CPU Load

```bash
# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable cups
sudo systemctl disable avahi-daemon
```

### Monitor System Resources

```bash
# Real-time monitoring
htop

# Temperature
watch -n 1 vcgencmd measure_temp

# Check logs for errors
tail -f /home/pi/smart_cane.log
```

---

## Testing End-to-End

```bash
# Run manually (not as service)
cd /home/pi/smart_cane
python3 main.py

# Expected output:
# - "Smart cane starting" (spoken)
# - Sensors initialize
# - Camera starts
# - "Smart cane ready" (spoken)

# Test obstacle detection:
# - Wave hand in front of sensors
# - Motors should vibrate

# Test object detection:
# - Point camera at person/chair/car
# - Should announce detected objects
```

---

## Safety Notes

1. **This is an assistive device, NOT a replacement for a white cane**
2. Always use with traditional mobility aids
3. Test thoroughly before real-world use
4. Keep system charged and maintained
5. Have emergency contact procedures
6. Not intended for medical use without professional supervision

---

## Getting Help

For issues:

1. Check logs:
```bash
tail -100 /home/pi/smart_cane.log
journalctl -u smart-cane -n 100
```

2. Verify system packages:
```bash
python3 --version
dpkg -l | grep python3-opencv
dpkg -l | grep python3-numpy
dpkg -l | grep python3-rpi.gpio
```

3. Test components individually using standalone test modes

4. Open an issue on GitHub with:
   - Error messages from logs
   - Output of `python3 --version`
   - Output of `uname -a`
   - Output of component tests

---

## Support

- `/home/pi/smart_cane.log` - Application logs
- `sudo journalctl -u smart-cane.service` - Service logs
- GitHub Issues: https://github.com/AmmarRiaz123/Navicane/issues
