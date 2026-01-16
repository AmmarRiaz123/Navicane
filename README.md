# 🦯 Smart Cane for the Visually Impaired

**Complete Raspberry Pi-based assistive navigation system**

---

## 🚀 Run From Scratch (Complete Guide)

### Prerequisites

- Raspberry Pi 4 (4GB+ RAM)
- Raspberry Pi OS 64-bit installed
- Internet connection
- MicroSD card (32GB+)
- Pi Camera Module connected
- 3× HC-SR04 sensors, 3× vibration motors (see [WIRING.md](WIRING.md))

---

### Step 1: Flash Raspberry Pi OS

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Flash **Raspberry Pi OS 64-bit (64-bit)** to SD card
3. Boot Pi and complete initial setup (username, password, WiFi)

---

### Step 2: Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages (THIS IS CRITICAL!)
sudo apt install -y \
    python3-opencv \
    python3-numpy \
    python3-rpi.gpio \
    espeak \
    libcamera-apps \
    git \
    python3-pip
```

**Why apt and not pip?** On ARM64, packages like OpenCV and NumPy fail to compile via pip. Use pre-built apt versions.

---

### Step 3: Clone Project

```bash
# Clone repository
cd ~
git clone https://github.com/AmmarRiaz123/Navicane.git
cd Navicane
```

---

### Step 4: Download AI Model

```bash
# Run automated model downloader
bash download_models.sh
```

This downloads YOLOv4-tiny (24MB) to `~/models/`:
- `yolov4-tiny.weights` - Model weights
- `yolov4-tiny.cfg` - Configuration
- `coco.names` - Object class names

**If download fails:**
```bash
# Manual download
mkdir -p ~/models
cd ~/models
wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights
wget https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg
wget https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/coco.names
```

---

### Step 5: Install Python Packages

```bash
cd ~/Navicane
pip3 install -r requirements.txt --break-system-packages
```

*(Only installs RPi.GPIO - everything else is via apt)*

---

### Step 6: Enable Camera

```bash
sudo raspi-config
```

Navigate to: **Interface Options → Camera → Enable**

Reboot:
```bash
sudo reboot
```

---

### Step 7: Verify Installation

```bash
cd ~/Navicane
bash verify_installation.sh
```

Should show all ✓ checks passing.

**If config.py not found:**
```bash
# Copy Python files to working directory
mkdir -p ~/smart_cane
cp ~/Navicane/*.py ~/smart_cane/
cd ~/smart_cane
```

---

### Step 8: Wire Hardware

Follow [WIRING.md](WIRING.md) to connect:

**Ultrasonic Sensors:**
- Left: Trigger=GPIO23, Echo=GPIO24 (with voltage divider!)
- Center: Trigger=GPIO17, Echo=GPIO27
- Right: Trigger=GPIO22, Echo=GPIO10

**Vibration Motors:**
- Left: GPIO18 (via transistor)
- Center: GPIO25 (via transistor)
- Right: GPIO8 (via transistor)

**Camera:** Connect to CSI port

⚠️ **Use voltage dividers on ultrasonic Echo pins!** (1kΩ + 2kΩ resistors)

---

### Step 9: Test Components

```bash
cd ~/Navicane

# Test camera (should show preview for 3 seconds)
rpicam-hello -t 3000

# Test Python modules individually
python3 camera.py      # Should detect objects and create smart_cane.log
python3 ultrasonic.py  # Should show distances
python3 vibration.py   # Should vibrate motors
python3 speech.py      # Should speak
```

**Note:** Tests will create a `smart_cane.log` file in the current directory.

**If you get "No module named 'config'":**
```bash
cd ~/Navicane  # Make sure you're in the directory with the Python files
```

---

### Step 10: Run Complete System

```bash
cd ~/Navicane
python3 main.py
```

**Expected behavior:**
1. Hears: "Smart cane starting"
2. Sensors initialize
3. Camera starts
4. Hears: "Smart cane ready"
5. Walk around → motors vibrate near obstacles
6. Point camera at objects → announces "person ahead", "chair detected", etc.

**Stop:** Press `Ctrl+C`

---

## 🔄 Auto-Start on Boot (Optional)

Make system start automatically when Pi powers on:

```bash
# Option 1: Run install script (copies files + sets up service)
cd ~/Navicane
sudo bash install.sh

# Option 2: Manual setup
mkdir -p ~/smart_cane
cp ~/Navicane/*.py ~/smart_cane/
sudo cp ~/Navicane/smart-cane.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable smart-cane.service
sudo systemctl start smart-cane.service
```

**Control commands:**
```bash
sudo systemctl stop smart-cane     # Stop
sudo systemctl restart smart-cane  # Restart
sudo systemctl disable smart-cane  # Disable auto-start
```

---

## 📁 Project Structure

```plaintext
Navicane/                    # Clone location
├── camera.py                # Camera and object detection
├── config.py                # Configuration settings (uses dynamic paths)
├── download_models.sh       # AI model downloader script
├── install.sh               # Installation script
├── main.py                  # Main program file
├── requirements.txt         # Python package requirements
├── smart-cane.service       # Systemd service file
├── ultrasonic.py            # Ultrasonic sensor handling
├── vibration.py             # Vibration motor control
├── speech.py                # Text-to-speech
├── utils.py                 # Helper functions
├── verify_installation.sh   # System checker
├── smart_cane.log          # Runtime logs (created when running)
└── WIRING.md               # Hardware wiring guide

~/smart_cane/               # Runtime location (created by install.sh)
├── *.py                    # All Python modules copied here
└── smart_cane.log         # Runtime logs

~/models/                   # AI models (auto-detected by config.py)
├── yolov4-tiny.weights
├── yolov4-tiny.cfg
└── coco.names
```

**Note:** Log files are created in the current working directory, so you'll find `smart_cane.log` in whichever directory you run the program from.

---

## 🔧 Troubleshooting

### "No module named 'config'" Error

This means you're not in the correct directory:

```bash
# Run from the directory containing the Python files
cd ~/Navicane     # If running from clone
# OR
cd ~/smart_cane   # If you ran install.sh
```

### config.py Not Found

```bash
# Solution 1: Copy files
mkdir -p ~/smart_cane
cp ~/Navicane/*.py ~/smart_cane/
cd ~/smart_cane

# Solution 2: Run from clone directory
cd ~/Navicane
python3 main.py
```

### FileNotFoundError: '/home/pi/smart_cane.log'

This happens when your username isn't `pi`. The updated config.py now uses dynamic paths.

**Fix:**
```bash
cd ~/Navicane
git pull  # Get latest changes with dynamic paths
python3 camera.py  # Should work now
```

Or manually update `config.py`:
```python
import os
LOG_FILE = os.path.join(os.getcwd(), 'smart_cane.log')
```

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/AmmarRiaz123/Navicane/issues)
- **Logs:** `cat ~/Navicane/smart_cane.log` or `cat ~/smart_cane/smart_cane.log`
- **Verification:** `bash verify_installation.sh`
