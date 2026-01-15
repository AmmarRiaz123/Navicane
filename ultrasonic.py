"""
Ultrasonic distance sensor module
Manages 3 HC-SR04 sensors (left, center, right)
"""

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
            
            # Wait for echo start
            timeout_start = time.time()
            while GPIO.input(self.echo_pin) == GPIO.LOW:
                pulse_start = time.time()
                if pulse_start - timeout_start > SENSOR_TIMEOUT:
                    return None
            
            # Wait for echo end
            timeout_start = time.time()
            while GPIO.input(self.echo_pin) == GPIO.HIGH:
                pulse_end = time.time()
                if pulse_end - timeout_start > SENSOR_TIMEOUT:
                    return None
            
            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150  # Speed of sound = 343m/s
            distance = round(distance, 2)
            
            # Validate range (HC-SR04: 2cm - 400cm)
            if 2 <= distance <= 400:
                return distance
            return None
            
        except Exception as e:
            logger.error(f"Error reading {self.name} sensor: {e}")
            return None

class UltrasonicArray:
    """Manages all three ultrasonic sensors"""
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        self.sensors = {}
        for position, pins in ULTRASONIC_SENSORS.items():
            self.sensors[position] = UltrasonicSensor(
                pins['trigger'], 
                pins['echo'], 
                position
            )
        
        logger.info("Ultrasonic array initialized")
    
    def read_all(self):
        """
        Read all sensors and return distances
        Returns: dict with 'left', 'center', 'right' distances in cm
        """
        distances = {}
        for position, sensor in self.sensors.items():
            distance = sensor.get_distance()
            distances[position] = distance
            if distance is not None:
                logger.debug(f"{position}: {distance}cm")
        
        return distances
    
    def get_obstacle_status(self):
        """
        Check which sensors detect obstacles within threshold
        Returns: dict with boolean values for each position
        """
        distances = self.read_all()
        status = {}
        
        for position, distance in distances.items():
            if distance is None:
                status[position] = False
            else:
                status[position] = distance < DISTANCE_THRESHOLD
        
        return status
    
    def cleanup(self):
        """Clean up GPIO pins"""
        GPIO.cleanup()
        logger.info("Ultrasonic array cleaned up")

# === STANDALONE TEST ===
if __name__ == "__main__":
    print("Testing Ultrasonic Sensors...")
    print(f"Threshold: {DISTANCE_THRESHOLD}cm\n")
    
    array = UltrasonicArray()
    
    try:
        while True:
            distances = array.read_all()
            obstacles = array.get_obstacle_status()
            
            print("\n" + "="*50)
            for pos in ['left', 'center', 'right']:
                dist = distances.get(pos)
                obst = obstacles.get(pos)
                
                if dist is None:
                    print(f"{pos.upper():8} - No reading")
                else:
                    alert = " ⚠ OBSTACLE" if obst else ""
                    print(f"{pos.upper():8} - {dist:6.2f}cm{alert}")
            
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        array.cleanup()
