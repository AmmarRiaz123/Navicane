"""
Smart Cane Main Application
Integrates ultrasonic sensors, vibration motors, camera vision, and speech
"""

import threading
import time
import signal
import sys
from config import ULTRASONIC_LOOP_DELAY, CAMERA_LOOP_DELAY
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
        """Fast loop for ultrasonic sensors and vibration feedback"""
        logger.info("Ultrasonic loop started")
        
        while self.running:
            try:
                # Read sensors
                obstacle_status = self.ultrasonic.get_obstacle_status()
                
                # Update vibration motors
                self.vibration.update_from_obstacles(obstacle_status)
                
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
                # Detect objects
                detections = self.camera.detect_objects()
                
                if detections:
                    # Filter for center objects (ahead)
                    center_objects = [
                        (name, True) for name, is_center, conf, box in detections
                        if is_center
                    ]
                    
                    # Also include high-priority side objects
                    side_objects = [
                        (name, False) for name, is_center, conf, box in detections
                        if not is_center and name in ['person', 'car']
                    ]
                    
                    all_objects = center_objects + side_objects
                    
                    # Update speech with visible objects
                    self.speech.update_visible_objects(all_objects)
                
                time.sleep(CAMERA_LOOP_DELAY)
                
            except Exception as e:
                logger.error(f"Camera loop error: {e}")
                time.sleep(2)
                
                # Try to recover camera
                try:
                    self.camera.open_camera()
                except:
                    pass
        
        logger.info("Camera loop stopped")
    
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
