"""
Vibration motor control module
Manages 1 vibration motor (center)
"""

import RPi.GPIO as GPIO
from config import VIBRATION_MOTORS
from utils import setup_logger

logger = setup_logger('vibration')

class VibrationMotor:
    """Single vibration motor with PWM control"""
    
    def __init__(self, pin, name):
        self.pin = pin
        self.name = name
        
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, 100)  # 100Hz frequency
        self.pwm.start(0)
        
        logger.info(f"Initialized {name} vibration motor on pin {pin}")
    
    def set_intensity(self, intensity):
        """
        Set vibration intensity
        intensity: 0-100 (0=off, 100=maximum)
        """
        intensity = max(0, min(100, intensity))
        self.pwm.ChangeDutyCycle(intensity)
    
    def on(self):
        """Turn on at full intensity"""
        self.set_intensity(100)
    
    def off(self):
        """Turn off"""
        self.set_intensity(0)
    
    def cleanup(self):
        """Stop PWM and clean up"""
        self.pwm.stop()

class VibrationController:
    """Manages vibration motor"""
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Initialize single motor
        pin = VIBRATION_MOTORS['center']
        self.motor = VibrationMotor(pin, 'center')
        
        logger.info("Vibration controller initialized")
    
    def update_from_obstacle(self, is_obstacle):
        """
        Update motor based on obstacle detection
        is_obstacle: boolean - True if obstacle detected
        """
        if is_obstacle:
            self.motor.on()
        else:
            self.motor.off()
    
    def set_intensity(self, intensity):
        """
        Set motor intensity
        intensity: 0-100
        """
        self.motor.set_intensity(intensity)
    
    def on(self):
        """Turn motor on"""
        self.motor.on()
    
    def off(self):
        """Turn motor off"""
        self.motor.off()
    
    def pulse(self, duration=0.3):
        """Quick pulse for feedback"""
        import time
        self.motor.on()
        time.sleep(duration)
        self.motor.off()
    
    def cleanup(self):
        """Clean up motor"""
        self.motor.cleanup()
        GPIO.cleanup()
        logger.info("Vibration controller cleaned up")

# === STANDALONE TEST ===
if __name__ == "__main__":
    import time
    
    print("Testing Vibration Motor...")
    controller = VibrationController()
    
    try:
        # Test pattern
        print("\nTest 1: On/Off pattern")
        for i in range(3):
            print(f"  Pulse {i+1}")
            controller.on()
            time.sleep(0.5)
            controller.off()
            time.sleep(0.5)
        
        # Test intensity levels
        print("\nTest 2: Intensity levels")
        for intensity in [25, 50, 75, 100]:
            print(f"  Intensity: {intensity}%")
            controller.set_intensity(intensity)
            time.sleep(1)
        
        controller.off()
        
        # Test pulse
        print("\nTest 3: Quick pulses")
        for i in range(5):
            print(f"  Pulse {i+1}")
            controller.pulse(0.2)
            time.sleep(0.3)
        
        print("\nTest complete!")
        
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        controller.off()
        controller.cleanup()
