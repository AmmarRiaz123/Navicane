# Smart Cane Setup Guide

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

## Software Installation

### 1. Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 2. Enable Camera

```bash
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable
# Reboot after enabling
sudo reboot
```

### 3. Install Dependencies

```bash
# Python libraries
sudo apt-get install -y python3-pip python3-opencv
sudo pip3 install numpy

# Audio/Speech
sudo apt-get install -y espeak

# GPIO
sudo pip3 install RPi.GPIO
```

### 4. Download Object Detection Model

```bash
# Create models directory
mkdir -p /home/pi/models
cd /home/pi/models

# Download MobileNet SSD model
wget https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/MobileNetSSD_deploy.prototxt
wget https://github.com/chuanqi305/MobileNet-SSD/raw/master/MobileNetSSD_deploy.caffemodel
```

### 5. Install Smart Cane Code

```bash
# Copy all Python files to /home/pi/smart_cane
mkdir -p /home/pi/smart_cane
cd /home/pi/smart_cane

# Copy: main.py, camera.py, ultrasonic.py, vibration.py, speech.py, config.py, utils.py
```

### 6. Test Components

Test each module individually:

```bash
cd /home/pi/smart_cane

# Test ultrasonic sensors
python3 ultrasonic.py

# Test vibration motors
python3 vibration.py

# Test speech
python3 speech.py

# Test camera (if model downloaded)
python3 camera.py
```

## Auto-Start Configuration

### Create systemd Service

Create `/etc/systemd/system/smart-cane.service`:

```ini
[Unit]
Description=Smart Cane for Blind Users
After=multi-user.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/smart_cane
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
```

## Troubleshooting

### Camera Not Working

```bash
# Check if camera detected
vcgencmd get_camera

# Should show: supported=1 detected=1

# Test with libcamera
libcamera-hello

# Check video device
ls /dev/video*
```

If using libcamera, may need to adjust `CAMERA_INDEX` in `config.py`.

### GPIO Permissions

```bash
# Add user to gpio group
sudo usermod -a -G gpio pi

# Reboot
sudo reboot
```

### Speech Not Working

```bash
# Test espeak
espeak "Hello world"

# Check ALSA settings
alsamixer

# Set default audio output
sudo raspi-config
# System Options > Audio > Select output
```

### Model Download Issues

If automatic download fails, manually download:

- [Prototxt](https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/MobileNetSSD_deploy.prototxt)
- [Caffemodel](https://github.com/chuanqi305/MobileNet-SSD/raw/master/MobileNetSSD_deploy.caffemodel)

Place in `/home/pi/models/`.

## Performance Tuning

### Optimize for Speed

In `config.py`:

```python
# Reduce camera resolution
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240

# Increase loop delays if CPU overheats
CAMERA_LOOP_DELAY = 1.0  # Run vision at 1Hz instead of 2Hz
```

### Reduce CPU Load

```bash
# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable cups
```

## Testing End-to-End

```bash
# Run manually
cd /home/pi/smart_cane
python3 main.py

# Should hear: "Smart cane starting" then "Smart cane ready"
# Walk around - motors should vibrate when approaching obstacles
# Point camera at objects - should announce detected items
```

## Safety Notes

1. **This is an assistive device, NOT a replacement for a white cane**
2. Always use with traditional mobility aids
3. Test thoroughly before real-world use
4. Keep system charged and maintained
5. Have emergency contact procedures

## Support

For issues, check:
- `/home/pi/smart_cane.log`
- `sudo journalctl -u smart-cane.service`
