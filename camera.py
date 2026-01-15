"""
Camera vision module with object detection
Uses OpenCV DNN with MobileNet SSD
"""

import cv2
import numpy as np
from config import (
    CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS,
    MODEL_PATH, PROTOTXT_PATH, CONFIDENCE_THRESHOLD,
    PRIORITY_OBJECTS, CENTER_REGION_START, CENTER_REGION_END
)
from utils import setup_logger, retry_on_failure

logger = setup_logger('camera')

# MobileNet SSD class labels
CLASSES = [
    "background", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
    "sofa", "train", "tvmonitor"
]

class ObjectDetector:
    """Object detection using MobileNet SSD"""
    
    def __init__(self):
        self.net = None
        self.load_model()
    
    @retry_on_failure(max_attempts=3, delay=2)
    def load_model(self):
        """Load the pre-trained model"""
        try:
            logger.info(f"Loading model from {MODEL_PATH}")
            self.net = cv2.dnn.readNetFromCaffe(PROTOTXT_PATH, MODEL_PATH)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
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
                
                if idx >= len(CLASSES):
                    continue
                
                class_name = CLASSES[idx]
                
                # Only report priority objects
                if class_name not in PRIORITY_OBJECTS:
                    continue
                
                # Get bounding box
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                
                results.append((class_name, confidence, (startX, startY, endX, endY)))
        
        return results

class CameraManager:
    """Manages camera and object detection"""
    
    def __init__(self):
        self.cap = None
        self.detector = ObjectDetector()
        self.frame_count = 0
        self.open_camera()
    
    @retry_on_failure(max_attempts=5, delay=1)
    def open_camera(self):
        """Open camera with retry logic"""
        try:
            logger.info(f"Opening camera {CAMERA_INDEX}")
            self.cap = cv2.VideoCapture(CAMERA_INDEX)
            
            if not self.cap.isOpened():
                raise Exception("Failed to open camera")
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
            
            logger.info("Camera opened successfully")
            
        except Exception as e:
            logger.error(f"Camera error: {e}")
            raise
    
    def read_frame(self):
        """Read a frame from camera"""
        if self.cap is None or not self.cap.isOpened():
            self.open_camera()
        
        ret, frame = self.cap.read()
        
        if not ret:
            logger.warning("Failed to read frame")
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
