"""
Speech output module using espeak
Non-blocking text-to-speech with queue management
"""

import subprocess
import threading
import queue
from config import TTS_SPEED, TTS_VOLUME
from utils import setup_logger, RateLimiter

logger = setup_logger('speech')

class SpeechEngine:
    """Non-blocking text-to-speech engine"""
    
    def __init__(self):
        self.speech_queue = queue.Queue()
        self.is_running = False
        self.worker_thread = None
        
        # Test if espeak is available
        try:
            subprocess.run(['espeak', '--version'], 
                         capture_output=True, check=True)
            logger.info("Speech engine initialized (espeak)")
        except Exception as e:
            logger.error(f"espeak not found: {e}")
            raise
    
    def start(self):
        """Start the speech worker thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        logger.info("Speech worker started")
    
    def stop(self):
        """Stop the speech worker thread"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2)
        logger.info("Speech worker stopped")
    
    def _worker(self):
        """Worker thread that processes speech queue"""
        while self.is_running:
            try:
                text = self.speech_queue.get(timeout=0.5)
                self._speak_blocking(text)
                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Speech worker error: {e}")
    
    def _speak_blocking(self, text):
        """Actually speak the text (blocking call)"""
        try:
            cmd = [
                'espeak',
                '-s', str(TTS_SPEED),
                '-a', str(TTS_VOLUME),
                text
            ]
            subprocess.run(cmd, check=False, capture_output=True)
            logger.info(f"Spoke: '{text}'")
        except Exception as e:
            logger.error(f"Error speaking '{text}': {e}")
    
    def speak(self, text):
        """
        Queue text to be spoken (non-blocking)
        """
        if not self.is_running:
            self.start()
        
        self.speech_queue.put(text)
        logger.debug(f"Queued: '{text}'")
    
    def speak_now(self, text):
        """
        Speak immediately, bypassing queue (blocking)
        """
        self._speak_blocking(text)
    
    def clear_queue(self):
        """Clear all pending speech"""
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break

class SmartSpeech:
    """
    Intelligent speech manager with cooldown and priority
    """
    
    def __init__(self, cooldown_seconds=5.0):
        self.engine = SpeechEngine()
        self.engine.start()
        self.rate_limiter = RateLimiter(cooldown_seconds)
        self.current_objects = set()
        
        logger.info(f"Smart speech initialized (cooldown: {cooldown_seconds}s)")
    
    def announce_object(self, object_name, is_center=False):
        """
        Announce object with smart filtering
        - Only speaks if object is new or cooldown expired
        - Adds "ahead" for center objects
        """
        key = f"object_{object_name}"
        
        if self.rate_limiter.can_trigger(key):
            location = "ahead" if is_center else "detected"
            message = f"{object_name} {location}"
            self.engine.speak(message)
            return True
        
        return False
    
    def update_visible_objects(self, objects):
        """
        Update currently visible objects and announce new ones
        objects: list of (name, is_center) tuples
        """
        new_objects = set(obj[0] for obj in objects)
        
        # Announce newly appeared objects
        for name, is_center in objects:
            if name not in self.current_objects:
                self.announce_object(name, is_center)
        
        # Reset cooldown for disappeared objects
        disappeared = self.current_objects - new_objects
        for name in disappeared:
            self.rate_limiter.reset(f"object_{name}")
        
        self.current_objects = new_objects
    
    def speak_urgent(self, text):
        """Speak immediately without cooldown"""
        self.engine.speak(text)
    
    def cleanup(self):
        """Stop speech engine"""
        self.engine.stop()
        logger.info("Smart speech cleaned up")

# === STANDALONE TEST ===
if __name__ == "__main__":
    import time
    
    print("Testing Speech Module...\n")
    
    speech = SmartSpeech(cooldown_seconds=3.0)
    
    try:
        # Test basic speech
        print("Test 1: Basic announcements")
        speech.announce_object("person", is_center=True)
        time.sleep(1)
        speech.announce_object("chair", is_center=False)
        time.sleep(4)
        
        # Test cooldown
        print("\nTest 2: Cooldown (should not repeat)")
        speech.announce_object("person", is_center=True)
        time.sleep(1)
        speech.announce_object("person", is_center=True)  # Should be blocked
        time.sleep(3)
        
        # Test object tracking
        print("\nTest 3: Object tracking")
        speech.update_visible_objects([
            ("car", True),
            ("bicycle", False)
        ])
        time.sleep(2)
        
        speech.update_visible_objects([
            ("car", True),  # Still there, won't announce
            ("person", True)  # New, will announce
        ])
        time.sleep(3)
        
        # Test urgent
        print("\nTest 4: Urgent message")
        speech.speak_urgent("Warning, obstacle detected")
        time.sleep(2)
        
        print("\nTest complete!")
        
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        speech.cleanup()
