"""
Test script for integrated ultrasonic sensor + vibration motor
Real-time demonstration of dynamic haptic feedback
"""

import time
from ultrasonic import UltrasonicArray
from vibration import VibrationController
from config import DISTANCE_THRESHOLD

def main():
    print("=" * 70)
    print("INTEGRATED ULTRASONIC + VIBRATION TEST")
    print("=" * 70)
    print("\nVibration Response Zones:")
    print("  🔴 CRITICAL (0-30cm):    Constant 100% vibration")
    print("  🟠 DANGER (30-60cm):     Fast pulses (5Hz), 70-100%")
    print("  🟡 WARNING (60-100cm):   Medium pulses (2Hz), 40-70%")
    print("  🟢 CAUTION (100-150cm):  Slow pulses (1Hz), 20-40%")
    print("  ⚪ CLEAR (150cm+):       Off")
    print("\nMove your hand closer/farther from sensor to feel the response")
    print("Press Ctrl+C to stop\n")
    print("=" * 70)
    
    sensor = UltrasonicArray()
    vibration = VibrationController()
    
    try:
        while True:
            # Read distance
            distance = sensor.read_distance()
            
            if distance is None:
                print("No reading...")
                vibration.off()
                time.sleep(0.1)
                continue
            
            # Update vibration based on distance
            vibration.update_from_distance(distance)
            
            # Calculate intensity for display
            intensity, pulse_rate, zone = vibration._calculate_intensity(distance)
            
            # Visual feedback
            zone_icons = {
                'critical': '🔴',
                'danger': '🟠',
                'warning': '🟡',
                'caution': '🟢',
                'clear': '⚪',
                'no_reading': '❓'
            }
            
            icon = zone_icons.get(zone, '⚪')
            bars = '█' * (intensity // 10)
            
            print(f"{icon} {distance:6.2f}cm | {zone:8s} | {intensity:3}% {bars:<10s} | {pulse_rate}Hz", end='\r')
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("Stopping...")
        print("=" * 70)
    finally:
        vibration.off()
        vibration.cleanup()
        sensor.cleanup()
        print("\n✓ Cleanup complete")

if __name__ == "__main__":
    main()
