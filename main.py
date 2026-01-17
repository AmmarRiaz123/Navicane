"""
Smart Cane Main Application
Integrates ultrasonic sensors, vibration motors, camera vision, and speech
"""

import threading
import time
import signal
import sys
from config import ULTRASONIC_LOOP_DELAY, CAMERA_LOOP_DELAY, SPEECH_TRIGGER_DISTANCE, CAMERA_TRIGGER_DISTANCE
from ultrasonic import UltrasonicArray
from vibration import VibrationController
from camera import CameraManager
from speech import SmartSpeech
from utils import setup_logger

logger = setup_logger('main')

class SmartCane:
    """Main smart cane system controller"""
    
    def __init__(self):
        self.running = False
        self.current_distance = None  # Share distance between threads
        self.distance_lock = threading.Lock()
        
        # Initialize components
        logger.info("Initializing Smart Cane System...")
        
        try:
            self.ultrasonic = UltrasonicArray()
            self.vibration = VibrationController()
            self.camera = CameraManager()
            self.speech = SmartSpeech()
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            self.cleanup()
            raise
        
        # Threads
        self.ultrasonic_thread = None
        self.camera_thread = None
    
    def start(self):
        """Start all system threads"""
        if self.running:
            return
        
        self.running = True
        logger.info("Starting Smart Cane System...")
        
        # Startup announcement
        self.speech.speak_urgent("Smart cane starting")
        
        # Start ultrasonic loop (fast)
        self.ultrasonic_thread = threading.Thread(
            target=self._ultrasonic_loop,
            daemon=True,
            name="UltrasonicThread"
        )
        self.ultrasonic_thread.start()
        
        # Start camera loop (slower)
        self.camera_thread = threading.Thread(
            target=self._camera_loop,
            daemon=True,
            name="CameraThread"
        )
        self.camera_thread.start()
        
        logger.info("All threads started")
        self.speech.speak_urgent("Smart cane ready")
    
    def stop(self):
        """Stop all system threads"""
        logger.info("Stopping Smart Cane System...")
        self.running = False
        
        # Wait for threads
        if self.ultrasonic_thread:
            self.ultrasonic_thread.join(timeout=2)
        if self.camera_thread:
            self.camera_thread.join(timeout=2)
        
        self.speech.speak_urgent("Smart cane stopping")
        time.sleep(1)
        
        self.cleanup()
        logger.info("Smart Cane System stopped")
    
    def _ultrasonic_loop(self):
        """Fast loop for ultrasonic sensor and vibration feedback"""
        logger.info("Ultrasonic loop started")
        
        while self.running:
            try:
                # Read distance
                distance = self.ultrasonic.read_distance()
                
                # Store distance for camera thread
                with self.distance_lock:
                    self.current_distance = distance
                
                # Update vibration based on distance (dynamic intensity)
                self.vibration.update_from_distance(distance)
                
                time.sleep(ULTRASONIC_LOOP_DELAY)
                
            except Exception as e:
                logger.error(f"Ultrasonic loop error: {e}")
                time.sleep(1)
        
        logger.info("Ultrasonic loop stopped")
    
    def _camera_loop(self):
        """Slower loop for camera vision and speech"""
        logger.info("Camera loop started")
        
        while self.running:
            try:
                # Get current distance from ultrasonic
                with self.distance_lock:
                    current_dist = self.current_distance
                
                # Only run detection if obstacle is close (< 100cm)
                if current_dist is None or current_dist > 100:
                    logger.debug("No close obstacle, skipping detection")
                    time.sleep(CAMERA_LOOP_DELAY)
                    continue
                
                # Detect objects
                detections = self.camera.detect_objects()
                
                if detections:
                    # Filter for center objects (ahead)
                    center_objects = [
                        (name, conf) for name, is_center, conf, box in detections
                        if is_center
                    ]
                    
                    if center_objects:
                        # Get highest confidence detection
                        best_detection = max(center_objects, key=lambda x: x[1])
                        object_name, confidence = best_detection
                        
                        # Announce if critically close (< 60cm)
                        if current_dist < 60:
                            logger.info(f"Critical detection: {object_name} at {current_dist}cm")
                            self.speech.announce_critical_object(object_name, current_dist)
                        else:
                            logger.debug(f"Detected {object_name} but not critical ({current_dist}cm)")
                
                time.sleep(CAMERA_LOOP_DELAY)
                
            except Exception as e:
                logger.error(f"Camera loop error: {e}")
                time.sleep(2)
        
        logger.info("Camera loop stopped")
    
    def _camera_speech_loop(self):
        """
        Lower-priority loop: camera detection + speech announcements
        Runs slower (0.5Hz) to save CPU and avoid constant speech
        Only activates when obstacles are nearby
        Distance is ALWAYS from ultrasonic sensor, never estimated from camera
        """
        logger.info("Camera+Speech loop started")
        
        consecutive_errors = 0
        max_errors = 5
        
        while self.running:
            try:
                # Get current distance from ultrasonic (thread-safe)
                # Distance is ALWAYS from ultrasonic sensor, NOT camera
                with self.distance_lock:
                    current_dist = self.current_distance
                
                # Only run detection if obstacle is nearby (saves CPU)
                if current_dist is None or current_dist > CAMERA_TRIGGER_DISTANCE:
                    logger.debug(f"No nearby obstacle ({current_dist}cm), skipping detection")
                    time.sleep(CAMERA_LOOP_DELAY)
                    continue
                
                # Log detection attempt
                logger.debug(f"Running detection (obstacle at {current_dist}cm from ultrasonic)")
                
                # Detect objects
                detections = self.camera.detect_objects()
                
                if not detections:
                    logger.debug("No objects detected by camera")
                    time.sleep(CAMERA_LOOP_DELAY)
                    continue
                
                # Filter for center objects (objects directly ahead)
                center_objects = [
                    (name, conf) for name, is_center, conf, box in detections
                    if is_center
                ]
                
                if not center_objects:
                    logger.debug("Objects detected but not in center")
                    time.sleep(CAMERA_LOOP_DELAY)
                    continue
                
                # Get highest confidence detection
                best_detection = max(center_objects, key=lambda x: x[1])
                object_name, confidence = best_detection
                
                logger.info(f"Best detection: {object_name} (conf={confidence:.2f})")
                logger.info(f"Distance from ultrasonic: {current_dist}cm")
                
                # Announce based on ULTRASONIC distance (not camera estimation)
                if current_dist < SPEECH_TRIGGER_DISTANCE:
                    if current_dist < 30:
                        # CRITICAL: Force immediate announcement
                        logger.warning(f"CRITICAL: {object_name} at {current_dist}cm - forcing announcement")
                    else:
                        # DANGER: Normal announcement
                        logger.info(f"Danger: {object_name} at {current_dist}cm - announcing")
                    
                    # Always pass ULTRASONIC distance to speech
                    self.speech.announce_critical_object(object_name, current_dist)
                else:
                    logger.debug(f"Detected {object_name} but not critical (ultrasonic: {current_dist}cm >= {SPEECH_TRIGGER_DISTANCE}cm)")
                
                # Reset error counter on success
                consecutive_errors = 0
                
                # Sleep for loop delay
                time.sleep(CAMERA_LOOP_DELAY)
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Camera loop error ({consecutive_errors}/{max_errors}): {e}")
                
                # If too many consecutive errors, try to recover
                if consecutive_errors >= max_errors:
                    logger.critical("Too many camera errors, attempting recovery...")
                    try:
                        self.camera.cleanup()
                        time.sleep(2)
                        self.camera = CameraManager()
                        logger.info("Camera recovery successful")
                        consecutive_errors = 0
                    except Exception as recovery_error:
                        logger.critical(f"Camera recovery failed: {recovery_error}")
                        break
                
                time.sleep(2)
        
        logger.info("Camera+Speech loop stopped")
    
    def cleanup(self):
        """Clean up all resources"""
        logger.info("Cleaning up resources...")
        
        try:
            self.vibration.all_off()
            self.vibration.cleanup()
        except:
            pass
        
        try:
            self.ultrasonic.cleanup()
        except:
            pass
        
        try:
            self.camera.cleanup()
        except:
            pass
        
        try:
            self.speech.cleanup()
        except:
            pass
        
        logger.info("Cleanup complete")

# Global instance for signal handler
cane = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nShutdown signal received...")
    if cane:
        cane.stop()
    sys.exit(0)

def main():
    """Main entry point"""
    global cane
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create and start system
        cane = SmartCane()
        cane.start()
        
        # Keep main thread alive
        logger.info("Smart Cane running. Press Ctrl+C to stop.")
        
        while True:
            time.sleep(1)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        if cane:
            cane.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
