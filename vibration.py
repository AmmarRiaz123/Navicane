"""
Vibration motor control module
Dynamic intensity based on obstacle distance
Provides haptic feedback with increasing urgency as objects get closer
"""

import RPi.GPIO as GPIO
import time
import threading
from config import VIBRATION_MOTORS, VIBRATION_RANGES, VIBRATION_PULSE_RATES
from utils import setup_logger

logger = setup_logger('vibration')

class VibrationMotor:
    """Single vibration motor with PWM control"""
    
    def __init__(self, pin, name):
        self.pin = pin
        self.name = name
        
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, 100)  # 100Hz base frequency
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
    """Manages vibration motor with dynamic intensity based on distance"""
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Initialize single motor
        pin = VIBRATION_MOTORS['center']
        self.motor = VibrationMotor(pin, 'center')
        
        # Pulsing control
        self.pulse_thread = None
        self.pulse_active = False
        self.current_intensity = 0
        self.pulse_rate = 0
        self.last_distance = None
        
        logger.info("Vibration controller initialized")
    
    def _calculate_intensity(self, distance):
        """
        Calculate vibration intensity based on distance
        Returns: (intensity, pulse_rate, zone_name)
        """
        if distance is None:
            return (0, 0, 'no_reading')
        
        # Determine zone and calculate intensity
        for zone_name, (min_dist, max_dist) in VIBRATION_RANGES.items():
            if min_dist <= distance < max_dist:
                # Linear interpolation within zone
                if zone_name == 'critical':
                    intensity = 100
                elif zone_name == 'danger':
                    # 30-60cm: 100% to 70%
                    intensity = 100 - int((distance - 30) * 30 / 30)
                elif zone_name == 'warning':
                    # 60-100cm: 70% to 40%
                    intensity = 70 - int((distance - 60) * 30 / 40)
                elif zone_name == 'caution':
                    # 100-150cm: 40% to 20%
                    intensity = 40 - int((distance - 100) * 20 / 50)
                else:  # clear
                    intensity = 0
                
                pulse_rate = VIBRATION_PULSE_RATES[zone_name]
                return (intensity, pulse_rate, zone_name)
        
        return (0, 0, 'clear')
    
    def update_from_distance(self, distance):
        """
        Update vibration based on obstacle distance
        distance: distance in cm (None if no reading)
        """
        intensity, pulse_rate, zone = self._calculate_intensity(distance)
        
        # Log only on significant changes
        if self.last_distance is None or abs((distance or 0) - (self.last_distance or 0)) > 10:
            logger.debug(f"Distance: {distance}cm → Zone: {zone} → Intensity: {intensity}% → Pulse: {pulse_rate}Hz")
            self.last_distance = distance
        
        self.current_intensity = intensity
        self.pulse_rate = pulse_rate
        
        # Stop existing pulse thread
        if self.pulse_thread and self.pulse_active:
            self.pulse_active = False
            time.sleep(0.1)
        
        # Handle vibration based on pulse rate
        if intensity == 0:
            # No vibration
            self.motor.off()
        elif pulse_rate == 0:
            # Constant vibration (critical zone)
            self.motor.set_intensity(intensity)
        else:
            # Pulsing vibration
            self.pulse_active = True
            self.pulse_thread = threading.Thread(
                target=self._pulse_loop,
                daemon=True
            )
            self.pulse_thread.start()
    
    def _pulse_loop(self):
        """Internal thread for pulsing vibration"""
        pulse_duration = 1.0 / (self.pulse_rate * 2) if self.pulse_rate > 0 else 0.5
        
        while self.pulse_active:
            # Vibrate ON
            self.motor.set_intensity(self.current_intensity)
            time.sleep(pulse_duration)
            
            # Vibrate OFF
            self.motor.off()
            time.sleep(pulse_duration)
    
    def update_from_obstacle(self, is_obstacle):
        """
        Legacy method for simple on/off (kept for compatibility)
        is_obstacle: boolean - True if obstacle detected
        """
        if is_obstacle:
            self.motor.on()
        else:
            self.motor.off()
    
    def set_intensity(self, intensity):
        """Set motor intensity directly"""
        self.motor.set_intensity(intensity)
    
    def on(self):
        """Turn motor on"""
        self.motor.on()
    
    def off(self):
        """Turn motor off"""
        self.pulse_active = False
        time.sleep(0.1)
        self.motor.off()
    
    def all_off(self):
        """Turn off all motors"""
        self.off()
    
    def pulse(self, duration=0.3):
        """Quick pulse for feedback"""
        self.motor.on()
        time.sleep(duration)
        self.motor.off()
    
    def cleanup(self):
        """Clean up motor"""
        self.pulse_active = False
        time.sleep(0.2)
        self.motor.cleanup()
        GPIO.cleanup()
        logger.info("Vibration controller cleaned up")

# === STANDALONE TEST ===
if __name__ == "__main__":
    import time
    
    print("Testing Vibration Motor - Dynamic Intensity")
    print("=" * 60)
    print("\nVibration Zones:")
    print("  0-30cm:   CRITICAL - 100% constant vibration")
    print("  30-60cm:  DANGER   - 70-100% fast pulses (5Hz)")
    print("  60-100cm: WARNING  - 40-70% medium pulses (2Hz)")
    print("  100-150cm: CAUTION - 20-40% slow pulses (1Hz)")
    print("  150cm+:   CLEAR    - Off")
    print("=" * 60)
    
    controller = VibrationController()
    
    try:
        # Simulate approaching object
        test_distances = [
            200, 180, 160, 140, 120,  # Caution zone
            100, 90, 80, 70, 60,       # Warning zone
            50, 45, 40, 35, 30,        # Danger zone
            25, 20, 15, 10, 5,         # Critical zone
            10, 20, 40, 60, 100, 150, 200  # Moving away
        ]
        
        print("\nSimulating object approach and retreat...")
        print("(Watch motor behavior change)\n")
        
        for distance in test_distances:
            intensity, pulse_rate, zone = controller._calculate_intensity(distance)
            print(f"{distance:3}cm → {zone:8s} → {intensity:3}% intensity → {pulse_rate}Hz pulse")
            
            controller.update_from_distance(distance)
            time.sleep(1.5)  # Hold each distance for 1.5 seconds
        
        print("\n✓ Test complete!")
        
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        controller.off()
        controller.cleanup()
