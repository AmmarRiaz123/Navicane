"""
Vibration motor control module
Manages 3 vibration motors (left, center, right)
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
    """Manages all vibration motors"""
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        self.motors = {}
        for position, pin in VIBRATION_MOTORS.items():
            self.motors[position] = VibrationMotor(pin, position)
        
        logger.info("Vibration controller initialized")
    
    def update_from_obstacles(self, obstacle_status):
        """
        Update motors based on obstacle detection
        obstacle_status: dict with 'left', 'center', 'right' boolean values
        """
        for position, is_obstacle in obstacle_status.items():
            if position in self.motors:
                if is_obstacle:
                    self.motors[position].on()
                else:
                    self.motors[position].off()
    
    def set_motor(self, position, state):
        """
        Manually control a motor
        position: 'left', 'center', or 'right'
        state: True/False or 0-100 for intensity
        """
        if position in self.motors:
            if isinstance(state, bool):
                if state:
                    self.motors[position].on()
                else:
                    self.motors[position].off()
            else:
                self.motors[position].set_intensity(state)
    
    def all_off(self):
        """Turn off all motors"""
        for motor in self.motors.values():
            motor.off()
    
    def test_pattern(self):
        """Run a test pattern"""
        import time
        logger.info("Running test pattern...")
        
        for position in ['left', 'center', 'right']:
            self.motors[position].on()
            time.sleep(0.3)
            self.motors[position].off()
            time.sleep(0.2)
    
    def cleanup(self):
        """Clean up all motors"""
        for motor in self.motors.values():
            motor.cleanup()
        GPIO.cleanup()
        logger.info("Vibration controller cleaned up")

# === STANDALONE TEST ===
if __name__ == "__main__":
    import time
    
    print("Testing Vibration Motors...")
    controller = VibrationController()
    
    try:
        # Test pattern
        print("\nRunning test pattern...")
        controller.test_pattern()
        
        # Test obstacle response
        print("\nTesting obstacle response...")
        test_scenarios = [
            {'left': True, 'center': False, 'right': False},
            {'left': False, 'center': True, 'right': False},
            {'left': False, 'center': False, 'right': True},
            {'left': True, 'center': True, 'right': True},
            {'left': False, 'center': False, 'right': False}
        ]
        
        for scenario in test_scenarios:
            print(f"\nObstacles: {scenario}")
            controller.update_from_obstacles(scenario)
            time.sleep(2)
        
        print("\nTest complete!")
        
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        controller.all_off()
        controller.cleanup()
