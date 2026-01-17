"""
Full system integration test
Tests ultrasonic + vibration + camera + speech working together
"""

import time
import threading
from ultrasonic import UltrasonicArray
from vibration import VibrationController
from camera import CameraManager
from speech import SmartSpeech

def main():
    print("=" * 70)
    print("FULL SYSTEM INTEGRATION TEST")
    print("=" * 70)
    print("\nThis test demonstrates:")
    print("  • Ultrasonic sensor detecting distance (ALWAYS used for distance)")
    print("  • Vibration motor responding to distance")
    print("  • Camera detecting objects (identifies WHAT is there)")
    print("  • Speech announcing when critically close:")
    print("    - CRITICAL (< 30cm): Immediate warning (bypasses cooldown)")
    print("    - DANGER (30-60cm): Announces with 2s cooldown")
    print("\nInstructions:")
    print("  1. Move object closer to sensor")
    print("  2. Within 60cm: speech announces what camera sees")
    print("  3. Within 30cm: URGENT warning, always speaks")
    print("\nPress Ctrl+C to stop\n")
    print("=" * 70)
    
    # Initialize components
    sensor = UltrasonicArray()
    vibration = VibrationController()
    camera = CameraManager()
    speech = SmartSpeech()
    
    speech.speak_urgent("System ready")
    time.sleep(2)
    
    try:
        last_detection_time = 0
        
        while True:
            # Read distance from ULTRASONIC (only source of distance)
            distance = sensor.read_distance()
            
            if distance is None:
                print("No sensor reading", end='\r')
                vibration.off()
                time.sleep(0.1)
                continue
            
            # Update vibration based on ULTRASONIC distance
            vibration.update_from_distance(distance)
            
            # Get zone info
            intensity, pulse_rate, zone = vibration._calculate_intensity(distance)
            zone_icon = {'critical': '🔴', 'danger': '🟠', 'warning': '🟡', 
                        'caution': '🟢', 'clear': '⚪'}.get(zone, '⚪')
            
            # Only run detection if obstacle is close (< 100cm)
            # And only every 2 seconds to save CPU
            current_time = time.time()
            if distance < 100 and (current_time - last_detection_time) > 2:
                last_detection_time = current_time
                
                # Camera detects WHAT is there
                detections = camera.detect_objects()
                
                if detections:
                    # Filter center objects
                    center_objects = [(name, conf) for name, is_center, conf, box 
                                    in detections if is_center]
                    
                    if center_objects:
                        # Get best detection
                        object_name, confidence = max(center_objects, key=lambda x: x[1])
                        
                        # Announce based on ULTRASONIC distance
                        if distance < 60:
                            urgency = "⚠️ CRITICAL" if distance < 30 else "🎤"
                            print(f"\n{zone_icon} {distance:6.2f}cm (ultrasonic) | {zone:8s} | {urgency} Announcing: {object_name}")
                            # Pass ULTRASONIC distance to speech
                            speech.announce_critical_object(object_name, distance)
                        else:
                            print(f"{zone_icon} {distance:6.2f}cm (ultrasonic) | {zone:8s} | 👁️  Detected: {object_name} (too far)", end='\r')
                    else:
                        print(f"{zone_icon} {distance:6.2f}cm (ultrasonic) | {zone:8s} | No objects ahead", end='\r')
                else:
                    print(f"{zone_icon} {distance:6.2f}cm (ultrasonic) | {zone:8s} | No detections", end='\r')
            else:
                print(f"{zone_icon} {distance:6.2f}cm (ultrasonic) | {zone:8s}", end='\r')
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("Stopping...")
        print("=" * 70)
    finally:
        speech.speak_urgent("Shutting down")
        time.sleep(2)
        vibration.off()
        vibration.cleanup()
        sensor.cleanup()
        camera.cleanup()
        speech.cleanup()
        print("\n✓ Cleanup complete")

if __name__ == "__main__":
    main()
