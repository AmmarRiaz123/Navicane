"""
Smart Cane Main Application
Integrates ultrasonic sensors, vibration motors, camera vision, and speech
Runs all modules independently without blocking
"""

import threading
import time
import signal
import sys
from config import (
    ULTRASONIC_LOOP_DELAY, CAMERA_LOOP_DELAY, 
    SPEECH_TRIGGER_DISTANCE, CAMERA_TRIGGER_DISTANCE
)
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
        self.current_distance = None
        self.distance_lock = threading.Lock()
        
        # Component status flags
        self.components_ready = {
            'ultrasonic': False,
            'vibration': False,
            'camera': False,
            'speech': False
        }
        
        # Initialize components
        logger.info("Initializing Smart Cane System...")
        
        try:
            # Initialize ultrasonic sensor
            logger.info("Initializing ultrasonic sensor...")
            self.ultrasonic = UltrasonicArray()
            self.components_ready['ultrasonic'] = True
            logger.info("✓ Ultrasonic sensor ready")
            
            # Initialize vibration controller
            logger.info("Initializing vibration controller...")
            self.vibration = VibrationController()
            self.components_ready['vibration'] = True
            logger.info("✓ Vibration controller ready")
            
            # Initialize camera (may take longer)
            logger.info("Initializing camera system...")
            self.camera = CameraManager()
            self.components_ready['camera'] = True
            logger.info("✓ Camera system ready")
            
            # Initialize speech
            logger.info("Initializing speech system...")
            self.speech = SmartSpeech()
            self.components_ready['speech'] = True
            logger.info("✓ Speech system ready")
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            logger.error(f"Component status: {self.components_ready}")
            self.cleanup()
            raise
        
        # Thread references
        self.ultrasonic_thread = None
        self.camera_thread = None
    
    def start(self):
        """Start all system threads"""
        if self.running:
            logger.warning("System already running")
            return
        
        self.running = True
        logger.info("Starting Smart Cane System...")
        
        # Startup announcement
        try:
            self.speech.speak_urgent("Smart cane starting")
            time.sleep(1)
        except Exception as e:
            logger.error(f"Startup announcement failed: {e}")
        
        # Start ultrasonic + vibration thread (high priority, fast loop)
        if self.components_ready['ultrasonic'] and self.components_ready['vibration']:
            self.ultrasonic_thread = threading.Thread(
                target=self._ultrasonic_vibration_loop,
                daemon=True,
                name="UltrasonicVibrationThread"
            )
            self.ultrasonic_thread.start()
            logger.info("✓ Ultrasonic+Vibration thread started")
        else:
            logger.error("Cannot start ultrasonic thread - components not ready")
        
        # Start camera + speech thread (lower priority, slower loop)
        if self.components_ready['camera'] and self.components_ready['speech']:
            self.camera_thread = threading.Thread(
                target=self._camera_speech_loop,
                daemon=True,
                name="CameraSpeechThread"
            )
            self.camera_thread.start()
            logger.info("✓ Camera+Speech thread started")
        else:
            logger.error("Cannot start camera thread - components not ready")
        
        # Final ready announcement
        time.sleep(0.5)
        try:
            self.speech.speak_urgent("Smart cane ready")
        except Exception as e:
            logger.error(f"Ready announcement failed: {e}")
        
        logger.info("Smart Cane System fully operational")
    
    def stop(self):
        """Stop all system threads gracefully"""
        logger.info("Stopping Smart Cane System...")
        self.running = False
        
        # Announce shutdown
        try:
            self.speech.speak_urgent("Smart cane stopping")
            time.sleep(1)
        except:
            pass
        
        # Wait for threads to finish
        if self.ultrasonic_thread and self.ultrasonic_thread.is_alive():
            logger.info("Waiting for ultrasonic thread...")
            self.ultrasonic_thread.join(timeout=3)
        
        if self.camera_thread and self.camera_thread.is_alive():
            logger.info("Waiting for camera thread...")
            self.camera_thread.join(timeout=3)
        
        # Cleanup resources
        self.cleanup()
        logger.info("Smart Cane System stopped")
    
    def _ultrasonic_vibration_loop(self):
        """
        High-priority loop: ultrasonic sensor + vibration motor
        Runs fast (20Hz) for immediate obstacle feedback
        """
        logger.info("Ultrasonic+Vibration loop started")
        
        consecutive_errors = 0
        max_errors = 10
        
        while self.running:
            try:
                # Read distance
                distance = self.ultrasonic.read_distance()
                
                # Store distance for camera thread (thread-safe)
                with self.distance_lock:
                    self.current_distance = distance
                
                # Update vibration based on distance
                self.vibration.update_from_distance(distance)
                
                # Reset error counter on success
                consecutive_errors = 0
                
                # Sleep for loop delay
                time.sleep(ULTRASONIC_LOOP_DELAY)
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Ultrasonic loop error ({consecutive_errors}/{max_errors}): {e}")
                
                # Turn off vibration on error
                try:
                    self.vibration.off()
                except:
                    pass
                
                # If too many consecutive errors, exit thread
                if consecutive_errors >= max_errors:
                    logger.critical("Too many ultrasonic errors, stopping thread")
                    break
                
                time.sleep(1)
        
        logger.info("Ultrasonic+Vibration loop stopped")
    
    def _camera_speech_loop(self):
        """
        Lower-priority loop: camera detection + speech announcements
        """
        logger.info("Camera+Speech loop started")
        
        consecutive_errors = 0
        max_errors = 5
        last_detection_attempt = 0
        detection_interval = 1.0  # From config.CAMERA_LOOP_DELAY
        
        while self.running:
            try:
                # Get current distance from ultrasonic (thread-safe)
                with self.distance_lock:
                    current_dist = self.current_distance
                
                current_time = time.time()
                
                # Check conditions
                if current_dist is None:
                    time.sleep(0.5)
                    continue
                
                if current_dist > CAMERA_TRIGGER_DISTANCE:
                    time.sleep(0.5)
                    continue
                
                if (current_time - last_detection_attempt) < detection_interval:
                    time.sleep(0.1)
                    continue
                
                last_detection_attempt = current_time
                
                # Log detection attempt
                logger.info(f"🎥 Detection at {current_dist:.1f}cm")
                
                # Detect objects
                detections = self.camera.detect_objects()
                
                if not detections:
                    logger.debug("📷 No objects")
                    consecutive_errors = 0  # Reset on successful detection (even if nothing found)
                    time.sleep(0.1)
                    continue
                
                logger.info(f"📷 {len(detections)} objects total")
                
                # Filter center objects
                center_objects = [
                    (name, conf) for name, is_center, conf, box in detections
                    if is_center
                ]
                
                if not center_objects:
                    logger.debug("📷 Nothing in center")
                    consecutive_errors = 0
                    time.sleep(0.1)
                    continue
                
                # Get best detection
                best_detection = max(center_objects, key=lambda x: x[1])
                object_name, confidence = best_detection
                
                logger.info(f"🎯 {object_name} (conf={confidence:.2f}) at {current_dist:.1f}cm")
                
                # Announce if within trigger distance
                if current_dist < SPEECH_TRIGGER_DISTANCE:
                    # Try to announce (non-blocking)
                    announced = self.speech.announce_critical_object(object_name, current_dist)
                    
                    if announced:
                        logger.info(f"✅ Announced: {object_name}")
                    else:
                        logger.debug(f"🔇 Skipped (cooldown or busy)")
                
                # Reset error counter on success
                consecutive_errors = 0
                
                # Brief sleep
                time.sleep(0.1)
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"❌ Camera error ({consecutive_errors}/{max_errors}): {e}")
                
                # Don't block - just log and continue
                if consecutive_errors >= max_errors:
                    logger.critical("💥 Too many errors, attempting recovery...")
                    try:
                        self.camera.cleanup()
                        time.sleep(1)
                        self.camera = CameraManager()
                        logger.info("✅ Camera recovered")
                        consecutive_errors = 0
                    except:
                        logger.critical("💀 Recovery failed, continuing anyway...")
                        consecutive_errors = 0  # Reset to keep trying
                
                time.sleep(1)
        
        logger.info("Camera+Speech loop stopped")
    
    def cleanup(self):
        """Clean up all resources"""
        logger.info("Cleaning up resources...")
        
        # Stop vibration
        if self.components_ready.get('vibration'):
            try:
                self.vibration.all_off()
                self.vibration.cleanup()
                logger.info("✓ Vibration cleaned up")
            except Exception as e:
                logger.error(f"Vibration cleanup error: {e}")
        
        # Cleanup ultrasonic
        if self.components_ready.get('ultrasonic'):
            try:
                self.ultrasonic.cleanup()
                logger.info("✓ Ultrasonic cleaned up")
            except Exception as e:
                logger.error(f"Ultrasonic cleanup error: {e}")
        
        # Cleanup camera
        if self.components_ready.get('camera'):
            try:
                self.camera.cleanup()
                logger.info("✓ Camera cleaned up")
            except Exception as e:
                logger.error(f"Camera cleanup error: {e}")
        
        # Cleanup speech
        if self.components_ready.get('speech'):
            try:
                self.speech.cleanup()
                logger.info("✓ Speech cleaned up")
            except Exception as e:
                logger.error(f"Speech cleanup error: {e}")
        
        logger.info("Cleanup complete")

# Global instance for signal handler
cane = None

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully (Ctrl+C, SIGTERM)"""
    print("\n\n" + "="*50)
    print("Shutdown signal received...")
    print("="*50)
    
    if cane:
        cane.stop()
    
    print("Goodbye!")
    sys.exit(0)

def main():
    """Main entry point"""
    global cane
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # systemctl stop
    
    try:
        # Create and start system
        logger.info("="*60)
        logger.info("SMART CANE SYSTEM STARTUP")
        logger.info("="*60)
        
        cane = SmartCane()
        cane.start()
        
        # Keep main thread alive
        logger.info("Smart Cane running. Press Ctrl+C to stop.")
        logger.info("="*60)
        
        # Main loop - just keep alive and log status periodically
        last_status_time = time.time()
        status_interval = 300  # Log status every 5 minutes
        
        while True:
            time.sleep(10)
            
            # Periodic status check
            current_time = time.time()
            if current_time - last_status_time >= status_interval:
                with cane.distance_lock:
                    dist = cane.current_distance
                
                logger.info(f"Status: Running | Distance: {dist}cm | Threads: Ultrasonic={'alive' if cane.ultrasonic_thread.is_alive() else 'dead'}, Camera={'alive' if cane.camera_thread.is_alive() else 'dead'}")
                last_status_time = current_time
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        if cane:
            cane.stop()
    
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        
        if cane:
            cane.stop()
        
        sys.exit(1)

if __name__ == "__main__":
    # Ensure proper logging when run directly
    import logging
    
    # Set root logger to INFO for normal operation
    # (DEBUG mode is available via run_main_debug.py)
    logging.getLogger().setLevel(logging.INFO)
    
    print("=" * 70)
    print("SMART CANE SYSTEM")
    print("=" * 70)
    print("\nStarting system...")
    print("Press Ctrl+C to stop\n")
    print("=" * 70)
    
    main()
