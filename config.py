"""
Configuration file for Smart Cane System
All hardware pins, thresholds, and detection parameters
"""

# === ULTRASONIC SENSOR PINS ===
ULTRASONIC_SENSORS = {
    'left': {'trigger': 23, 'echo': 24},
    'center': {'trigger': 17, 'echo': 27},
    'right': {'trigger': 22, 'echo': 10}
}

# Distance threshold in cm - trigger vibration if closer
DISTANCE_THRESHOLD = 100  # 1 meter

# Sensor timeout in seconds
SENSOR_TIMEOUT = 0.1

# === VIBRATION MOTOR PINS ===
VIBRATION_MOTORS = {
    'left': 18,
    'center': 25,
    'right': 8
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
# Model paths (download instructions in setup)
MODEL_PATH = '/home/pi/models/MobileNetSSD_deploy.caffemodel'
PROTOTXT_PATH = '/home/pi/models/MobileNetSSD_deploy.prototxt'

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
LOG_FILE = '/home/pi/smart_cane.log'
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR

# === TTS SETTINGS ===
TTS_SPEED = 150  # Words per minute
TTS_VOLUME = 100  # 0-100
