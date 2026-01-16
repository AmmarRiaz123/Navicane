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
# Camera backend selection
# 'opencv' - Use OpenCV VideoCapture (works with V4L2)
# 'picamera2' - Use libcamera via picamera2 library (recommended for Pi Camera)
CAMERA_BACKEND = 'picamera2'  # Change to 'opencv' if picamera2 not available

CAMERA_INDEX = 0  # Use 0 for /dev/video0, adjust if needed
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 10

# Camera retry settings
CAMERA_RETRY_ATTEMPTS = 5
CAMERA_RETRY_DELAY = 2  # seconds between retries

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
CAMERA_LOOP_DELAY = 0.5  # 500ms = 2Hz

# === LOGGING ===
LOG_FILE = '/home/pi/smart_cane.log'
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR

# === TTS SETTINGS ===
TTS_SPEED = 150  # Words per minute
TTS_VOLUME = 100  # 0-100
