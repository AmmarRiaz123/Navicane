# 🦯 Smart Cane for the Visually Impaired

**Complete Raspberry Pi-based assistive navigation system**

---

## 🚀 Run From Scratch (Complete Guide)

### Prerequisites

- Raspberry Pi 4 (4GB+ RAM)
- Raspberry Pi OS 64-bit installed
- Internet connection
- MicroSD Card (32GB+)
- Pi Camera Module connected
- **1× HC-SR04 ultrasonic sensor (LEFT side)**
- **1× vibration motor** (see [WIRING.md](WIRING.md))

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

**Ultrasonic Sensor (LEFT side):**
- Trigger: GPIO23 (Pin 16)
- Echo: GPIO24 (Pin 18) - with voltage divider: 1kΩ + 2kΩ resistors

**Vibration Motor:**
- GPIO25 (Pin 22) - via 2N2222 transistor with 1kΩ base resistor and 1N4001 flyback diode

**Camera:** Connect to CSI port

⚠️ **Use voltage divider on ultrasonic Echo pin (GPIO24)!** (1kΩ + 2kΩ resistors)

---

### Step 9: Test Components

```bash
cd ~/Navicane

# Test camera (should show preview for 3 seconds)
rpicam-hello -t 3000

# Test ultrasonic sensor
python3 ultrasonic.py

# Test vibration motor
python3 vibration.py

# Test speech system
python3 speech.py

# Test camera detection
python3 camera.py

# Test full integration (RECOMMENDED)
python3 test_full_integration.py
```

**Smart Speech System:**
- 🔕 **Silent when far:** No announcements when objects > 60cm away
- 🔊 **Speaks when critical:** Announces objects when < 60cm (danger/critical zone)
- ⏸️  **No overlap:** Won't speak over itself
- 🔄 **Cooldown:** 5-second cooldown between same object announcements
- ⚡ **Urgent prefix:** Adds "Warning!" for objects < 30cm

**Example Behavior:**

*(To be filled based on actual behavior)*

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

## 🔄 Auto-Start on Boot

Make system start automatically when Pi powers on:

### Quick Setup (Recommended)

```bash
cd ~/Navicane
sudo bash setup_autostart.sh
```

This will:
- Create systemd service with correct user and paths
- Add user to GPIO group
- Enable auto-start on boot
- Optionally start service immediately

### Verify Auto-Start

```bash
# Check service status
sudo systemctl status smart-cane

# View logs
tail -f ~/Navicane/smart_cane.log

# Test by rebooting
sudo reboot
```

### Control Commands

```bash
# Use control script
bash ~/Navicane/control_cane.sh start
bash ~/Navicane/control_cane.sh stop
bash ~/Navicane/control_cane.sh status
bash ~/Navicane/control_cane.sh logs

# Or use systemctl directly
sudo systemctl start smart-cane     # Start
sudo systemctl stop smart-cane      # Stop
sudo systemctl restart smart-cane   # Restart
sudo systemctl status smart-cane    # Status
sudo systemctl disable smart-cane   # Disable auto-start
```

### Troubleshooting Auto-Start

**Service won't start:**
```bash
# Check service status
sudo systemctl status smart-cane

# View detailed logs
journalctl -u smart-cane -n 50

# Check permissions
sudo systemctl cat smart-cane
```

**GPIO permission errors:**
```bash
# Verify user in gpio group
groups $USER

# If not, add and reboot
sudo usermod -a -G gpio $USER
sudo reboot
```

**Service starts but crashes:**
```bash
# Check application logs
cat ~/Navicane/smart_cane.log

# Test manually first
cd ~/Navicane
python3 main.py
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
