"""
Configuration file for Smart Cane System
All hardware pins, thresholds, and detection parameters
"""
import os
from pathlib import Path

# Get user's home directory dynamically
USER_HOME = str(Path.home())

# === ULTRASONIC SENSOR PINS ===
# Single HC-SR04 sensor on the left side
ULTRASONIC_SENSORS = {
    'left': {'trigger': 23, 'echo': 24}
}

# Distance threshold in cm - trigger vibration if closer
DISTANCE_THRESHOLD = 60  # 60cm threshold (was 100)

# Sensor timeout in seconds
SENSOR_TIMEOUT = 0.1

# === VIBRATION MOTOR PINS ===
# Single vibration motor
VIBRATION_MOTORS = {
    'center': 25
}

# === VIBRATION INTENSITY SETTINGS ===
# Distance ranges for different vibration intensities (in cm)
VIBRATION_RANGES = {
    'critical': (0, 30),      # 0-30cm: 100% intensity (constant)
    'danger': (30, 60),       # 30-60cm: 70-100% intensity (fast pulses)
    'warning': (60, 100),     # 60-100cm: 40-70% intensity (medium pulses)
    'caution': (100, 150),    # 100-150cm: 20-40% intensity (slow pulses)
    'clear': (150, 400)       # 150cm+: 0% intensity (off)
}

# Pulse frequencies (Hz) for different zones
VIBRATION_PULSE_RATES = {
    'critical': 0,            # Constant vibration (no pulse)
    'danger': 5,              # 5 pulses per second
    'warning': 2,             # 2 pulses per second
    'caution': 1,             # 1 pulse per second
    'clear': 0                # Off
}

# === CAMERA SETTINGS ===
# IMPORTANT: This system uses rpicam-* CLI commands only!
# Picamera2, cv2.VideoCapture, and libcamera do NOT work
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Time between camera captures (seconds)
# Increase if CPU struggles or decrease for faster detection
RPICAM_CAPTURE_INTERVAL = 2.0  # 2 seconds between frames

# Camera timeout for rpicam-still (seconds)
RPICAM_TIMEOUT = 5

# === OBJECT DETECTION ===
# Model paths - use dynamic home directory
MODEL_PATH = os.path.join(USER_HOME, 'models/yolov4-tiny.weights')
PROTOTXT_PATH = os.path.join(USER_HOME, 'models/yolov4-tiny.cfg')

# Detection confidence threshold
CONFIDENCE_THRESHOLD = 0.5

# Objects to detect and announce
PRIORITY_OBJECTS = [
    'person', 'chair', 'car', 'bicycle', 'motorbike',
    'bus', 'train', 'bottle', 'diningtable', 'pottedplant'
]

# Center region for "ahead" detection (percentage of frame width)
CENTER_REGION_START = 0.3
CENTER_REGION_END = 0.7

# Cooldown between same object announcements (seconds)
SPEECH_COOLDOWN = 5.0

# === LOOP TIMING ===
ULTRASONIC_LOOP_DELAY = 0.05  # 50ms = 20Hz
CAMERA_LOOP_DELAY = 2.0  # 2 seconds between captures (adjusted for rpicam)

# === LOGGING ===
# Use current directory or home directory for logs
LOG_FILE = os.path.join(os.getcwd(), 'smart_cane.log')

# Create log directory if needed
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR

# === TTS SETTINGS ===
TTS_SPEED = 150  # Words per minute
TTS_VOLUME = 100  # 0-100
