"""
Text-to-speech module
Announces detected objects via espeak
Only speaks when obstacle is critically close
"""

import subprocess
import time
import threading
from config import TTS_SPEED, TTS_VOLUME, SPEECH_COOLDOWN, SPEECH_TRIGGER_DISTANCE
from utils import setup_logger, RateLimiter

logger = setup_logger('speech')

class SmartSpeech:
    """Text-to-speech with intelligent cooldown and priority"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter(SPEECH_COOLDOWN)
        self.speaking = False
        self.speech_lock = threading.Lock()
        
        # Test espeak
        try:
            subprocess.run(['espeak', '--version'], 
                          capture_output=True, 
                          timeout=2)
            logger.info("espeak initialized successfully")
        except Exception as e:
            logger.error(f"espeak not available: {e}")
    
    def _speak_async(self, text):
        """Internal async speech method"""
        try:
            # Mark as speaking
            self.speaking = True
            
            logger.info(f"Speaking: {text}")  # Log before speaking
            
            # Speak via espeak with maximum volume and amplitude
            result = subprocess.run(
                ['espeak', text, 
                 '-s', str(TTS_SPEED),      # Speed
                 '-a', str(TTS_VOLUME),     # Amplitude (volume)
                 '-g', '10',                # Gap between words (ms)
                 '-p', '50'],               # Pitch (50 = default)
                capture_output=True,
                timeout=10  # Increased timeout from 5 to 10 seconds
            )
            
            if result.returncode != 0:
                logger.error(f"espeak failed: {result.stderr}")
            else:
                logger.info(f"✓ Spoke: {text}")
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Speech timeout: {text}")
        except Exception as e:
            logger.error(f"Speech error: {e}")
        finally:
            self.speaking = False
    
    def speak(self, text, force=False):
        """
        Speak text if not already speaking
        text: string to speak
        force: if True, bypass cooldown (for urgent messages)
        """
        with self.speech_lock:
            # Don't speak over existing speech
            if self.speaking and not force:
                logger.debug(f"Already speaking, skipping: {text}")
                return False
            
            # Check cooldown (unless forced)
            if not force and not self.rate_limiter.can_trigger(text):
                logger.debug(f"Cooldown active for: {text}")
                return False
            
            # Speak in background thread
            thread = threading.Thread(
                target=self._speak_async,
                args=(text,),
                daemon=True
            )
            thread.start()
            
            return True
    
    def speak_urgent(self, text):
        """Speak immediately, bypassing cooldown"""
        return self.speak(text, force=True)
    
    def announce_critical_object(self, object_name, distance):
        """
        Announce object when close
        object_name: detected object class name
        distance: distance in cm from ultrasonic sensor
        
        ALWAYS announces in critical zone (< 30cm)
        Uses short cooldown in danger zone (30-60cm)
        """
        # Validate distance
        if distance is None or distance >= SPEECH_TRIGGER_DISTANCE:
            logger.debug(f"Distance {distance}cm exceeds trigger threshold {SPEECH_TRIGGER_DISTANCE}cm")
            return False
        
        # Map object names to natural speech (EXPANDED)
        speech_map = {
            'person': 'person ahead',
            'chair': 'chair',
            'car': 'car',
            'bicycle': 'bicycle',
            'motorbike': 'motorcycle',
            'bus': 'bus',
            'train': 'train',
            'bottle': 'bottle',
            'diningtable': 'table',
            'dining table': 'table',
            'pottedplant': 'plant',
            'potted plant': 'plant',
            'dog': 'dog',
            'cat': 'cat',
            'backpack': 'backpack',
            'handbag': 'bag',
            'suitcase': 'suitcase',
            'laptop': 'laptop',
            'cell phone': 'phone',
            'book': 'book',
            'sofa': 'sofa',
            'bed': 'bed',
            'tv': 'television',
            'bench': 'bench'
        }
        
        speech_text = speech_map.get(object_name, f'{object_name}')
        
        # CRITICAL zone (< 30cm): ALWAYS speak, force override
        if distance < 30:
            speech_text = f"Warning! {speech_text}"
            logger.warning(f"CRITICAL: {speech_text} at {distance}cm")
            with self.speech_lock:
                if self.speaking:
                    logger.info("Interrupting speech for CRITICAL warning")
                self.rate_limiter.reset(speech_text)
                return self.speak(speech_text, force=True)
        
        # Normal announcement
        logger.info(f"Announcing: {speech_text} at {distance}cm")
        return self.speak(speech_text, force=False)
    
    def update_visible_objects(self, objects):
        """
        Legacy method - kept for compatibility
        objects: list of (object_name, is_center) tuples
        """
        # Filter only center objects
        center_objects = [name for name, is_center in objects if is_center]
        
        if not center_objects:
            return
        
        # Announce first priority object
        for obj in ['person', 'car', 'chair']:
            if obj in center_objects:
                self.speak(f'{obj} ahead')
                return
        
        # Announce any other object
        if center_objects:
            self.speak(f'{center_objects[0]} ahead')
    
    def cleanup(self):
        """Clean up resources"""
        # Wait for current speech to finish
        if self.speaking:
            time.sleep(0.5)
        logger.info("Speech system cleaned up")

# === STANDALONE TEST ===
if __name__ == "__main__":
    import time
    
    print("Testing Speech Module...")
    speech = SmartSpeech()
    
    try:
        # Test basic speech
        print("\n1. Basic speech test")
        speech.speak_urgent("Speech system initialized")
        time.sleep(2)
        
        # Test cooldown
        print("\n2. Cooldown test (should skip second)")
        speech.speak("Test message one")
        time.sleep(0.5)
        speech.speak("Test message one")  # Should be skipped
        time.sleep(6)
        speech.speak("Test message one")  # Should work after cooldown
        time.sleep(2)
        
        # Test overlapping speech
        print("\n3. Overlapping speech test (should skip second)")
        speech.speak("This is a longer message to test overlap")
        time.sleep(0.1)
        speech.speak("This should be skipped")  # Should be skipped
        time.sleep(2)
        
        # Test critical announcements
        print("\n4. Critical object announcements")
        speech.announce_critical_object('person', 25)  # Should speak (critical)
        time.sleep(2)
        speech.announce_critical_object('chair', 45)   # Should speak (danger)
        time.sleep(2)
        speech.announce_critical_object('car', 100)    # Should NOT speak (too far)
        time.sleep(2)
        
        print("\n✓ Test complete!")
        
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        speech.cleanup()
