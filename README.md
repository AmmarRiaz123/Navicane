# 🦯 Smart Cane for the Visually Impaired

**Raspberry Pi–Based Assistive Navigation System**

## 🌟 Overview

This project is a smart assistive cane designed to help visually impaired users navigate their surroundings safely and independently. Built around a **Raspberry Pi 4**, the system combines **ultrasonic distance sensors**, a **camera for object recognition**, **vibration feedback**, and **bone-conduction audio** to provide real-time awareness of obstacles and objects in front of the user.

The system continuously monitors the environment, detects nearby obstacles and recognized objects, and communicates this information through **gentle vibration patterns** and **spoken feedback**, allowing the user to make informed navigation decisions without blocking environmental sounds.

---

## 🎯 Project Goals

The main purpose of this project is to create an affordable, portable, and real-world usable mobility aid that:

* Detects obstacles in front of the user
* Identifies common objects (people, doors, vehicles, stairs, etc.)
* Provides intuitive feedback through vibration and voice
* Works automatically when powered on
* Is modular, testable, and easy to extend

This is intended to function as a **true mobility assistant**, not just a technical demo.

---

## 💻 System Requirements

### Hardware
* Raspberry Pi 4 Model B (4GB or 8GB RAM)
* Raspberry Pi Camera Module v1.3 (OV5647) or v2
* 3× HC-SR04 Ultrasonic Distance Sensors
* 3× 3-5V Vibration Motors
* Bone-conduction Bluetooth Headphones
* MicroSD Card (32GB+ recommended)
* 5V 3A USB-C Power Supply

### Software
* **Raspberry Pi OS 64-bit** (Debian 12 "Bookworm" or later)
* Python 3.11+ (comes with Raspberry Pi OS)
* System packages: OpenCV, NumPy, espeak, GPIO libraries
* **libcamera-apps** (for rpicam-* commands)

### ⚠️ Camera System Architecture

**IMPORTANT CONSTRAINT:** This system uses a unique camera architecture due to hardware/OS limitations:

- ✅ **Camera Access:** `rpicam-*` CLI commands ONLY (rpicam-still, rpicam-hello)
- ❌ **NOT Supported:** Picamera2, cv2.VideoCapture, libcamera Python bindings
- 🔧 **How It Works:** Python calls `rpicam-still` via subprocess → captures frame to disk → OpenCV loads image → processes detection

This is **NOT a workaround** - it's the only method that works on this specific Raspberry Pi build.

---

## 📦 Installation Guide

### Step 1: Prepare Raspberry Pi OS

Flash **Raspberry Pi OS 64-bit (Full or Lite)** to your microSD card using [Raspberry Pi Imager](https://www.raspberrypi.com/software/).

Boot your Raspberry Pi and complete the initial setup.

### Step 2: Install System Dependencies

```bash
sudo apt update
sudo apt upgrade -y

# Install system packages (DO THIS FIRST!)
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

**DO NOT install python3-picamera2** - it does not work on this system!

**Why use apt instead of pip?**

On Raspberry Pi OS 64-bit (arm64), packages like `numpy` and `opencv-python` often fail to build from source via pip.

The apt versions are:
- ✅ Pre-compiled for Raspberry Pi hardware
- ✅ Optimized for ARM architecture
- ✅ Install in seconds instead of hours

### Step 3: Clone or Download Project

```bash
cd /home/pi
git clone https://github.com/AmmarRiaz123/Navicane.git
cd Navicane
```

Or download and extract the ZIP file.

### Step 4: Install Python Dependencies

```bash
# Install minimal pip packages (only RPi.GPIO if not already installed)
pip3 install -r requirements.txt --break-system-packages
```

**Note**: The `--break-system-packages` flag is required on Raspberry Pi OS Bookworm+ to install packages outside a virtual environment. This is safe for this project since we're only installing RPi.GPIO.

**Alternative (using venv):**

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### Step 5: Enable Camera Interface

```bash
sudo raspi-config
# Navigate to: Interface Options > Legacy Camera > Enable
# Or for libcamera: Interface Options > Camera > Enable
sudo reboot
```

### Step 6: Download AI Model

⚠️ **This is a critical step!** The camera won't work without the AI model.

**Option 1: Automatic download (recommended)**

```bash
cd ~/Navicane
bash download_models.sh
```

**Option 2: One-line command**

```bash
mkdir -p ~/models && cd ~/models && wget https://github.com/opencv/opencv_zoo/raw/master/models/object_detection_mobilenet/object_detection_mobilenet_2022apr.onnx -O mobilenet_ssd.onnx
```

**Option 3: Using curl (if wget fails)**

```bash
mkdir -p ~/models && cd ~/models && curl -L https://github.com/opencv/opencv_zoo/raw/master/models/object_detection_mobilenet/object_detection_mobilenet_2022apr.onnx -o mobilenet_ssd.onnx
```

**Option 4: Manual download**

1. Open this link in your browser: https://github.com/opencv/opencv_zoo/tree/master/models/object_detection_mobilenet
2. Click on `object_detection_mobilenet_2022apr.onnx`
3. Click the "Download" button
4. Save the file to `/home/pi/models/mobilenet_ssd.onnx`

**Verify download:**
```bash
ls -lh ~/models/mobilenet_ssd.onnx
# Should show a file around 9MB
```

**Update config (if not done automatically):**

```bash
nano ~/Navicane/config.py
```

Change these lines:
```python
MODEL_PATH = '/home/pi/models/mobilenet_ssd.onnx'
PROTOTXT_PATH = ''  # Leave empty for ONNX models
```

### Step 7: Hardware Setup

Follow the [WIRING.md](WIRING.md) guide to connect:
- 3× HC-SR04 ultrasonic sensors
- 3× vibration motors (with transistor circuits)
- Raspberry Pi Camera Module

**Important:** Use voltage dividers on ultrasonic echo pins!

### Step 8: Test Components

```bash
cd /home/pi/Navicane

# Verify system packages are working
python3 -c "import cv2; print('OpenCV:', cv2.__version__)"
python3 -c "import numpy; print('NumPy:', numpy.__version__)"
python3 -c "import RPi.GPIO; print('GPIO: OK')"

# Test individual modules
python3 ultrasonic.py    # Should show distance readings
python3 vibration.py     # Motors should vibrate in pattern
python3 speech.py        # Should speak test phrases
python3 camera.py        # Should detect objects (requires model)
```

### Step 9: Run the System

```bash
python3 main.py
```

You should hear "Smart cane starting" followed by "Smart cane ready".

---

## 🚀 Auto-Start on Boot

To make the system start automatically when Raspberry Pi powers on:

### Option 1: Using Installation Script (Recommended)

```bash
cd /home/pi/Navicane
sudo bash install.sh
```

This will:
- Copy files to `/home/pi/smart_cane`
- Download AI models
- Create systemd service
- Enable auto-start

### Option 2: Manual Setup

```bash
# Copy smart-cane.service to systemd
sudo cp smart-cane.service /etc/systemd/system/

# Edit paths if needed
sudo nano /etc/systemd/system/smart-cane.service

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable smart-cane.service
sudo systemctl start smart-cane.service

# Check status
sudo systemctl status smart-cane.service
```

**Control commands:**
```bash
sudo systemctl start smart-cane    # Start now
sudo systemctl stop smart-cane     # Stop
sudo systemctl restart smart-cane  # Restart
sudo systemctl status smart-cane   # Check status
journalctl -u smart-cane -f        # View live logs
```

---

## 🧩 Modular Architecture

Each subsystem is implemented as a separate Python module so it can be tested individually:

| Module          | Purpose                      | Test Command |
| --------------- | ---------------------------- | ------------ |
| `config.py`     | Configuration settings       | N/A |
| `utils.py`      | Helper functions             | N/A |
| `ultrasonic.py` | Distance sensor control      | `python3 ultrasonic.py` |
| `vibration.py`  | Vibration motor control      | `python3 vibration.py` |
| `speech.py`     | Text-to-speech output        | `python3 speech.py` |
| `camera.py`     | Camera + object detection    | `python3 camera.py` |
| `main.py`       | Main system coordinator      | `python3 main.py` |

---

## 🔧 Troubleshooting

### Import Errors (ModuleNotFoundError)

If you get `ModuleNotFoundError: No module named 'cv2'`:

```bash
# Verify system package is installed
dpkg -l | grep python3-opencv

# If not installed:
sudo apt install python3-opencv

# Test import
python3 -c "import cv2; print(cv2.__version__)"
```

### Camera Not Detected

```bash
# Check camera status with rpicam
rpicam-hello -t 3000

# Should show camera preview for 3 seconds

# DO NOT USE these commands (they won't work):
# - vcgencmd get_camera (shows incorrect info)
# - libcamera-hello (may not work)
# - raspistill (legacy, not supported)
```

**If rpicam-hello works, your camera is fine!**

### GPIO Permission Errors

```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Reboot required
sudo reboot
```

### Speech Not Working

```bash
# Test espeak
espeak "Hello world"

# If no sound, check audio output
sudo raspi-config
# System Options > Audio > Select correct output

# Test audio
speaker-test -t wav -c 2
```

### Python Version Issues

This project requires Python 3.11+:

```bash
python3 --version  # Should show 3.11 or higher
```

---

## 🛠️ Configuration

Edit `config.py` to adjust:

- **Distance threshold** for obstacle detection
- **Camera resolution** and frame rate
- **Detection confidence** threshold
- **Speech cooldown** timing
- **GPIO pin assignments**

---

## ⚙️ Performance Optimization

For better performance on Raspberry Pi 4:

```python
# In config.py:

# Reduce camera resolution
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240

# Slower detection rate (saves CPU)
CAMERA_LOOP_DELAY = 1.0  # 1 FPS instead of 2 FPS

# Higher confidence threshold (fewer false positives)
CONFIDENCE_THRESHOLD = 0.6
```

---

## 📚 Documentation

- [SETUP.md](SETUP.md) - Detailed setup instructions
- [WIRING.md](WIRING.md) - Hardware wiring guide with pin diagrams
- [requirements.txt](requirements.txt) - Python dependencies

---

## 🔒 Safety Notice

⚠️ **Important Safety Information:**

1. This device is an **assistive tool**, NOT a replacement for a white cane
2. Always use with traditional mobility aids
3. Test thoroughly in controlled environments before real-world use
4. Keep the system charged and maintained
5. Have emergency contact procedures in place
6. Not intended for medical use without professional supervision

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test thoroughly on actual Raspberry Pi hardware
4. Submit a pull request

---

## 📄 License

[Add your license here]

---

## 💖 Final Vision

This project is built to be more than a prototype — it is meant to become a **real assistive device** that improves independence, safety, and confidence for visually impaired users.

Every design choice focuses on:

* Simplicity
* Reliability  
* Comfort
* Real-world usability

And most of all… dignity and freedom of movement for the person holding the cane.

---

## 📞 Support

For issues or questions:
- Check the [Troubleshooting](#-troubleshooting) section
- Review logs: `tail -f /home/pi/smart_cane.log`
- Check service status: `sudo systemctl status smart-cane`
- Open an issue on GitHub

**System Information for Support:**
```bash
# Gather system info for bug reports
python3 --version
uname -a
dpkg -l | grep python3-opencv
dpkg -l | grep python3-numpy
vcgencmd get_camera
```
