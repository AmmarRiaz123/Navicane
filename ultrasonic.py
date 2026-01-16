import RPi.GPIO as GPIO
import time
from config import ULTRASONIC_SENSORS, DISTANCE_THRESHOLD, SENSOR_TIMEOUT
from utils import setup_logger

logger = setup_logger('ultrasonic')

class UltrasonicSensor:
    """Single HC-SR04 ultrasonic sensor"""
    
    def __init__(self, trigger_pin, echo_pin, name):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.name = name
        
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        GPIO.output(self.trigger_pin, GPIO.LOW)
        
        logger.info(f"Initialized {name} sensor: Trigger={trigger_pin}, Echo={echo_pin}")
    
    def get_distance(self):
        """
        Measure distance in centimeters
        Returns None if measurement fails
        """
        try:
            # Send 10us pulse
            GPIO.output(self.trigger_pin, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(self.trigger_pin, GPIO.LOW)
            
            # Wait for echo start with timeout
            pulse_start = time.time()
            timeout_start = time.time()
            while GPIO.input(self.echo_pin) == GPIO.LOW:
                pulse_start = time.time()
                if pulse_start - timeout_start > SENSOR_TIMEOUT:
                    logger.debug(f"{self.name}: Timeout waiting for echo start")
                    return None
            
            # Wait for echo end with timeout
            pulse_end = time.time()
            timeout_start = time.time()
            while GPIO.input(self.echo_pin) == GPIO.HIGH:
                pulse_end = time.time()
                if pulse_end - timeout_start > SENSOR_TIMEOUT:
                    logger.debug(f"{self.name}: Timeout waiting for echo end")
                    return None
            
            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150  # Speed of sound = 343m/s
            distance = round(distance, 2)
            
            # Validate range (HC-SR04: 2cm - 400cm)
            if 2 <= distance <= 400:
                return distance
            else:
                logger.debug(f"{self.name}: Distance {distance}cm out of valid range")
                return None
            
        except Exception as e:
            logger.error(f"Error reading {self.name} sensor: {e}")
            return None

class UltrasonicArray:
    """Manages the ultrasonic sensor"""
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Initialize left sensor
        pins = ULTRASONIC_SENSORS['left']
        self.sensor = UltrasonicSensor(
            pins['trigger'], 
            pins['echo'], 
            'left'
        )
        
        logger.info("Left ultrasonic sensor initialized")
    
    def read_distance(self):
        """
        Read sensor and return distance
        Returns: distance in cm or None
        """
        distance = self.sensor.get_distance()
        if distance is not None:
            logger.debug(f"Distance: {distance}cm")
        return distance
    
    def is_obstacle_detected(self):
        """
        Check if obstacle is within threshold
        Returns: True if obstacle detected, False otherwise
        """
        distance = self.read_distance()
        
        # If no valid reading, assume no obstacle
        if distance is None:
            logger.debug("No valid distance reading")
            return False
        
        # Check if distance is less than threshold
        is_obstacle = distance < DISTANCE_THRESHOLD
        
        if is_obstacle:
            logger.debug(f"Obstacle detected: {distance}cm < {DISTANCE_THRESHOLD}cm")
        
        return is_obstacle
    
    def cleanup(self):
        """Clean up GPIO pins"""
        GPIO.cleanup()
        logger.info("Ultrasonic sensor cleaned up")

# === STANDALONE TEST ===
if __name__ == "__main__":
    print("Testing Ultrasonic Sensor (LEFT side)...")
    print(f"Threshold: {DISTANCE_THRESHOLD}cm")
    print("Distances LESS than threshold will trigger warning\n")
    
    sensor = UltrasonicArray()
    
    try:
        while True:
            distance = sensor.read_distance()
            obstacle = sensor.is_obstacle_detected()
            
            print("="*60)
            if distance is None:
                print("No reading (sensor timeout or out of range)")
            else:
                status = "⚠️  OBSTACLE!" if obstacle else "✓ Clear"
                comparison = f"{distance:.2f}cm < {DISTANCE_THRESHOLD}cm" if obstacle else f"{distance:.2f}cm >= {DISTANCE_THRESHOLD}cm"
                print(f"Distance: {distance:6.2f}cm  |  {comparison}  |  {status}")
            
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        sensor.cleanup()
