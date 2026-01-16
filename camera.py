"""
Camera vision module with object detection
Uses rpicam-* CLI commands (subprocess) + OpenCV DNN for processing
IMPORTANT: This system CANNOT use Picamera2 or cv2.VideoCapture!
"""

import cv2
import numpy as np
import subprocess
import time
import tempfile
import os
from pathlib import Path
from config import (
    CAMERA_WIDTH, CAMERA_HEIGHT,
    MODEL_PATH, PROTOTXT_PATH, CONFIDENCE_THRESHOLD,
    PRIORITY_OBJECTS, CENTER_REGION_START, CENTER_REGION_END,
    RPICAM_CAPTURE_INTERVAL
)
from utils import setup_logger, retry_on_failure

logger = setup_logger('camera')

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
        self.classes = CLASSES
        self.model_type = None
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
                    logger.info(f"Loaded {len(self.classes)} class names")
                except Exception as e:
                    logger.warning(f"Could not load COCO names: {e}")
                
            else:
                logger.info("Using Caffe format (default)")
                self.net = cv2.dnn.readNetFromCaffe(PROTOTXT_PATH, MODEL_PATH)
                self.model_type = 'caffe'
            
            logger.info(f"Model loaded successfully (type: {self.model_type})")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def detect(self, frame):
        """Detect objects in frame"""
        if self.net is None:
            return []
        
        (h, w) = frame.shape[:2]
        
        if self.model_type == 'darknet':
            return self._detect_yolo(frame, w, h)
        else:
            return self._detect_ssd(frame, w, h)
    
    def _detect_ssd(self, frame, w, h):
        """Detection for SSD models"""
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)), 
            0.007843, 
            (300, 300), 
            127.5
        )
        
        self.net.setInput(blob)
        detections = self.net.forward()
        
        results = []
        
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence > CONFIDENCE_THRESHOLD:
                idx = int(detections[0, 0, i, 1])
                
                if idx >= len(self.classes):
                    continue
                
                class_name = self.classes[idx]
                
                if class_name not in PRIORITY_OBJECTS:
                    continue
                
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                
                results.append((class_name, confidence, (startX, startY, endX, endY)))
        
        return results
    
    def _detect_yolo(self, frame, w, h):
        """Detection for YOLO models"""
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        
        self.net.setInput(blob)
        
        layer_names = self.net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
        
        outputs = self.net.forward(output_layers)
        
        results = []
        
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > CONFIDENCE_THRESHOLD:
                    if class_id >= len(self.classes):
                        continue
                    
                    class_name = self.classes[class_id]
                    
                    if class_name not in PRIORITY_OBJECTS:
                        continue
                    
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
    """Manages camera via rpicam CLI and object detection"""
    
    def __init__(self):
        self.detector = ObjectDetector()
        self.frame_count = 0
        self.temp_dir = tempfile.mkdtemp(prefix='smart_cane_')
        logger.info(f"Using temp directory: {self.temp_dir}")
        
        # Test rpicam availability
        self.test_camera()
    
    def test_camera(self):
        """Test if rpicam-still works"""
        try:
            logger.info("Testing rpicam-still availability...")
            result = subprocess.run(
                ['rpicam-still', '--help'],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("✓ rpicam-still is available")
            else:
                logger.error("✗ rpicam-still failed")
                raise Exception("rpicam-still not working")
        except subprocess.TimeoutExpired:
            logger.error("✗ rpicam-still timed out")
            raise
        except FileNotFoundError:
            logger.error("✗ rpicam-still not found - install libcamera-apps")
            raise
    
    def capture_frame(self, timeout=5):
        """
        Capture a single frame using rpicam-still
        Returns: numpy array (BGR image) or None
        """
        temp_file = os.path.join(self.temp_dir, f'frame_{self.frame_count}.jpg')
        
        try:
            # Capture image using rpicam-still
            cmd = [
                'rpicam-still',
                '-o', temp_file,
                '--width', str(CAMERA_WIDTH),
                '--height', str(CAMERA_HEIGHT),
                '--nopreview',
                '--timeout', '1',  # Minimal timeout
                '--immediate'  # Capture immediately
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=timeout,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"rpicam-still failed: {result.stderr}")
                return None
            
            # Load image with OpenCV
            frame = cv2.imread(temp_file)
            
            if frame is None:
                logger.error(f"Failed to load image from {temp_file}")
                return None
            
            self.frame_count += 1
            
            # Clean up temp file
            try:
                os.remove(temp_file)
            except:
                pass
            
            return frame
            
        except subprocess.TimeoutExpired:
            logger.error("rpicam-still timed out")
            return None
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None
    
    def detect_objects(self):
        """
        Capture frame and detect objects
        Returns: list of (name, is_center, confidence, box) tuples
        """
        frame = self.capture_frame()
        
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
            
            obj_center_x = (startX + endX) / 2
            is_center = center_start <= obj_center_x <= center_end
            
            results.append((class_name, is_center, confidence, box))
            logger.debug(f"Detected: {class_name} ({confidence:.2f}) - Center: {is_center}")
        
        return results
    
    def capture_frame_with_boxes(self, save_path=None):
        """Capture frame and draw detection boxes (for debugging)"""
        frame = self.capture_frame()
        
        if frame is None:
            return None
        
        detections = self.detect_objects()
        
        for class_name, is_center, confidence, box in detections:
            (startX, startY, endX, endY) = box
            
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
        """Clean up temp directory"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.info(f"Cleaned up temp directory: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"Could not clean temp directory: {e}")


# === STANDALONE TEST ===
if __name__ == "__main__":
    import time
    
    print("Testing Camera Module (rpicam-based)...")
    print("Note: Model files must be downloaded first!\n")
    
    try:
        camera = CameraManager()
        
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
            else:
                print(f"Frame {camera.frame_count}: No objects detected")
            
            time.sleep(2)  # Wait between captures
        
        # Save final frame with boxes
        print("\nSaving final frame with boxes...")
        camera.capture_frame_with_boxes("test_detection.jpg")
        
        print("\nTest complete!")
        
    except KeyboardInterrupt:
        print("\n\nStopping...")
    except Exception as e:
        print(f"\n\nError: {e}")
    finally:
        try:
            camera.cleanup()
        except:
            pass
