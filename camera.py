"""
Camera vision module with object detection
Uses OpenCV DNN with MobileNet SSD
Supports both OpenCV VideoCapture and picamera2
"""

import cv2
import numpy as np
from config import (
    CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS, CAMERA_BACKEND,
    MODEL_PATH, PROTOTXT_PATH, CONFIDENCE_THRESHOLD,
    PRIORITY_OBJECTS, CENTER_REGION_START, CENTER_REGION_END
)
from utils import setup_logger, retry_on_failure

logger = setup_logger('camera')

# Try to import picamera2
try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
    logger.info("picamera2 library available")
except ImportError:
    PICAMERA2_AVAILABLE = False
    logger.warning("picamera2 not available, will use OpenCV only")

# MobileNet SSD class labels (for Caffe models)
CLASSES = [
    "background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
    "sofa", "train", "tvmonitor"
]

class ObjectDetector:
    """Object detection using MobileNet SSD or YOLO"""
    
    def __init__(self):
        self.net = None
        self.classes = CLASSES  # Default classes
        self.model_type = None  # 'caffe', 'onnx', 'darknet', etc.
        self.load_model()
    
    @retry_on_failure(max_attempts=3, delay=2)
    def load_model(self):
        """Load the pre-trained model"""
        try:
            logger.info(f"Loading model from {MODEL_PATH}")
            
            # Auto-detect model format
            if MODEL_PATH.endswith('.onnx'):
                logger.info("Detected ONNX format")
                self.net = cv2.dnn.readNetFromONNX(MODEL_PATH)
                self.model_type = 'onnx'
                
            elif MODEL_PATH.endswith('.caffemodel'):
                logger.info("Detected Caffe format")
                self.net = cv2.dnn.readNetFromCaffe(PROTOTXT_PATH, MODEL_PATH)
                self.model_type = 'caffe'
                
            elif MODEL_PATH.endswith('.pb'):
                logger.info("Detected TensorFlow format")
                self.net = cv2.dnn.readNetFromTensorflow(MODEL_PATH)
                self.model_type = 'tensorflow'
                
            elif MODEL_PATH.endswith('.weights'):
                logger.info("Detected Darknet (YOLO) format")
                cfg_path = PROTOTXT_PATH if PROTOTXT_PATH else MODEL_PATH.replace('.weights', '.cfg')
                self.net = cv2.dnn.readNetFromDarknet(cfg_path, MODEL_PATH)
                self.model_type = 'darknet'
                
                # Load COCO class names for YOLO
                coco_names_path = MODEL_PATH.replace('yolov4-tiny.weights', 'coco.names')
                try:
                    with open(coco_names_path, 'r') as f:
                        self.classes = [line.strip() for line in f.readlines()]
                    logger.info(f"Loaded {len(self.classes)} class names from {coco_names_path}")
                except Exception as e:
                    logger.warning(f"Could not load COCO names: {e}, using default classes")
                
            else:
                # Default to Caffe
                logger.info("Using Caffe format (default)")
                self.net = cv2.dnn.readNetFromCaffe(PROTOTXT_PATH, MODEL_PATH)
                self.model_type = 'caffe'
            
            logger.info(f"Model loaded successfully (type: {self.model_type})")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            logger.error("=" * 60)
            logger.error("MODEL LOADING FAILED")
            logger.error("=" * 60)
            logger.error("Possible solutions:")
            logger.error("1. Download model using: bash download_models.sh")
            logger.error("2. Check MODEL_PATH in config.py")
            logger.error("3. See ALTERNATIVE_MODELS.md for other options")
            logger.error("=" * 60)
            raise
    
    def detect(self, frame):
        """
        Detect objects in frame
        Returns: list of (class_name, confidence, box) tuples
        box = (startX, startY, endX, endY)
        """
        if self.net is None:
            return []
        
        (h, w) = frame.shape[:2]
        
        # Use different detection methods based on model type
        if self.model_type == 'darknet':
            return self._detect_yolo(frame, w, h)
        else:
            return self._detect_ssd(frame, w, h)
    
    def _detect_ssd(self, frame, w, h):
        """Detection for SSD models (MobileNet, etc.)"""
        # Prepare blob
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)), 
            0.007843, 
            (300, 300), 
            127.5
        )
        
        # Run detection
        self.net.setInput(blob)
        detections = self.net.forward()
        
        results = []
        
        # Parse detections
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence > CONFIDENCE_THRESHOLD:
                idx = int(detections[0, 0, i, 1])
                
                if idx >= len(self.classes):
                    continue
                
                class_name = self.classes[idx]
                
                # Only report priority objects
                if class_name not in PRIORITY_OBJECTS:
                    continue
                
                # Get bounding box
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                
                results.append((class_name, confidence, (startX, startY, endX, endY)))
        
        return results
    
    def _detect_yolo(self, frame, w, h):
        """Detection for YOLO models"""
        # Prepare blob for YOLO
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        
        # Run detection
        self.net.setInput(blob)
        
        # Get output layer names
        layer_names = self.net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
        
        # Forward pass
        outputs = self.net.forward(output_layers)
        
        results = []
        
        # Parse YOLO outputs
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > CONFIDENCE_THRESHOLD:
                    if class_id >= len(self.classes):
                        continue
                    
                    class_name = self.classes[class_id]
                    
                    # Only report priority objects
                    if class_name not in PRIORITY_OBJECTS:
                        continue
                    
                    # Get bounding box
                    center_x = int(detection[0] * w)
                    center_y = int(detection[1] * h)
                    width = int(detection[2] * w)
                    height = int(detection[3] * h)
                    
                    startX = int(center_x - width / 2)
                    startY = int(center_y - height / 2)
                    endX = int(center_x + width / 2)
                    endY = int(center_y + height / 2)
                    
                    results.append((class_name, float(confidence), (startX, startY, endX, endY)))
        
        return results

class CameraManager:
    """Manages camera and object detection"""
    
    def __init__(self):
        self.cap = None
        self.picam2 = None
        self.backend = CAMERA_BACKEND
        self.detector = ObjectDetector()
        self.frame_count = 0
        
        # Auto-fallback if picamera2 requested but not available
        if self.backend == 'picamera2' and not PICAMERA2_AVAILABLE:
            logger.warning("picamera2 requested but not available, falling back to opencv")
            self.backend = 'opencv'
        
        self.open_camera()
    
    @retry_on_failure(max_attempts=5, delay=1)
    def open_camera(self):
        """Open camera with retry logic"""
        try:
            if self.backend == 'picamera2':
                self._open_picamera2()
            else:
                self._open_opencv()
                
        except Exception as e:
            logger.error(f"Camera error: {e}")
            raise
    
    def _open_picamera2(self):
        """Open camera using picamera2 (libcamera backend)"""
        logger.info("Opening camera with picamera2 (libcamera)")
        
        self.picam2 = Picamera2()
        
        # Configure camera
        config = self.picam2.create_preview_configuration(
            main={"size": (CAMERA_WIDTH, CAMERA_HEIGHT), "format": "RGB888"}
        )
        self.picam2.configure(config)
        
        # Start camera
        self.picam2.start()
        
        # Wait for camera to warm up
        import time
        time.sleep(2)
        
        # Test capture
        test_frame = self.picam2.capture_array()
        if test_frame is None or test_frame.size == 0:
            raise Exception("picamera2 cannot capture frames")
        
        logger.info(f"Camera opened with picamera2: {CAMERA_WIDTH}x{CAMERA_HEIGHT}")
    
    def _open_opencv(self):
        """Open camera using OpenCV VideoCapture (V4L2 backend)"""
        logger.info(f"Opening camera {CAMERA_INDEX} with OpenCV")
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        
        if not self.cap.isOpened():
            # Provide detailed error message
            logger.error("=" * 60)
            logger.error("CAMERA FAILED TO OPEN WITH OPENCV")
            logger.error("=" * 60)
            logger.error("Possible causes:")
            logger.error("1. Camera not accessible via V4L2 (/dev/video*)")
            logger.error("2. Try using picamera2 backend instead")
            logger.error("   Set CAMERA_BACKEND = 'picamera2' in config.py")
            logger.error("3. Install: sudo apt install python3-picamera2")
            logger.error("")
            logger.error("Check available devices:")
            logger.error("  ls -l /dev/video*")
            logger.error("=" * 60)
            raise Exception("Failed to open camera with OpenCV")
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
        
        # Verify camera is actually working
        ret, test_frame = self.cap.read()
        if not ret or test_frame is None:
            logger.error("Camera opened but cannot read frames")
            raise Exception("Camera cannot capture frames")
        
        logger.info(f"Camera opened with OpenCV: {CAMERA_WIDTH}x{CAMERA_HEIGHT} @ {CAMERA_FPS}fps")
    
    def read_frame(self):
        """Read a frame from camera"""
        if self.backend == 'picamera2':
            if self.picam2 is None:
                self.open_camera()
            
            try:
                # Capture frame from picamera2
                frame = self.picam2.capture_array()
                
                if frame is None:
                    logger.warning("Failed to read frame from picamera2")
                    return None
                
                # picamera2 returns RGB, OpenCV expects BGR
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                self.frame_count += 1
                return frame
                
            except Exception as e:
                logger.error(f"Error reading frame from picamera2: {e}")
                return None
        
        else:  # opencv backend
            if self.cap is None or not self.cap.isOpened():
                self.open_camera()
            
            ret, frame = self.cap.read()
            
            if not ret:
                logger.warning("Failed to read frame from OpenCV")
                return None
            
            self.frame_count += 1
            return frame
    
    def detect_objects(self, frame=None):
        """
        Detect objects in frame (or capture new frame)
        Returns: list of (name, is_center, confidence, box) tuples
        """
        if frame is None:
            frame = self.read_frame()
        
        if frame is None:
            return []
        
        detections = self.detector.detect(frame)
        
        # Determine if objects are in center region
        frame_width = frame.shape[1]
        center_start = frame_width * CENTER_REGION_START
        center_end = frame_width * CENTER_REGION_END
        
        results = []
        for class_name, confidence, box in detections:
            (startX, startY, endX, endY) = box
            
            # Check if object center is in center region
            obj_center_x = (startX + endX) / 2
            is_center = center_start <= obj_center_x <= center_end
            
            results.append((class_name, is_center, confidence, box))
            logger.debug(f"Detected: {class_name} ({confidence:.2f}) - Center: {is_center}")
        
        return results
    
    def capture_frame_with_boxes(self, save_path=None):
        """
        Capture frame and draw detection boxes (for debugging)
        """
        frame = self.read_frame()
        if frame is None:
            return None
        
        detections = self.detect_objects(frame)
        
        for class_name, is_center, confidence, box in detections:
            (startX, startY, endX, endY) = box
            
            # Color: red if center, blue otherwise
            color = (0, 0, 255) if is_center else (255, 0, 0)
            
            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
            
            label = f"{class_name}: {confidence:.2f}"
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, label, (startX, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        if save_path:
            cv2.imwrite(save_path, frame)
            logger.info(f"Saved frame to {save_path}")
        
        return frame
    
    def cleanup(self):
        """Release camera resources"""
        if self.backend == 'picamera2' and self.picam2 is not None:
            try:
                self.picam2.stop()
                self.picam2.close()
                logger.info("picamera2 cleaned up")
            except:
                pass
        
        if self.cap is not None:
            self.cap.release()
        
        cv2.destroyAllWindows()
        logger.info("Camera cleaned up")

# === STANDALONE TEST ===
if __name__ == "__main__":
    import time
    
    print("Testing Camera Module...")
    print("Note: Model files must be downloaded first!\n")
    
    camera = CameraManager()
    
    try:
        print("Running detection for 30 seconds...")
        print("Press Ctrl+C to stop\n")
        
        start_time = time.time()
        
        while time.time() - start_time < 30:
            detections = camera.detect_objects()
            
            if detections:
                print(f"\nFrame {camera.frame_count}:")
                for name, is_center, conf, box in detections:
                    loc = "AHEAD" if is_center else "side"
                    print(f"  {name} ({loc}) - {conf:.2f}")
            
            time.sleep(1)
        
        # Save final frame with boxes
        print("\nSaving final frame with boxes...")
        camera.capture_frame_with_boxes("test_detection.jpg")
        
        print("\nTest complete!")
        
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        camera.cleanup()
