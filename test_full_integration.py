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
    print("  • Ultrasonic sensor detecting distance")
    print("  • Vibration motor responding to distance")
    print("  • Camera detecting objects")
    print("  • Speech announcing ONLY when critically close (< 60cm)")
    print("\nInstructions:")
    print("  1. Move object closer to sensor")
    print("  2. When within 60cm, speech will announce what camera sees")
    print("  3. Speech won't repeat same object for 5 seconds")
    print("  4. Speech won't talk over itself")
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
            # Read distance
            distance = sensor.read_distance()
            
            if distance is None:
                print("No sensor reading", end='\r')
                vibration.off()
                time.sleep(0.1)
                continue
            
            # Update vibration
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
                
                # Detect objects
                detections = camera.detect_objects()
                
                if detections:
                    # Filter center objects
                    center_objects = [(name, conf) for name, is_center, conf, box 
                                    in detections if is_center]
                    
                    if center_objects:
                        # Get best detection
                        object_name, confidence = max(center_objects, key=lambda x: x[1])
                        
                        # Announce if critically close (< 60cm)
                        if distance < 60:
                            print(f"\n{zone_icon} {distance:6.2f}cm | {zone:8s} | 🎤 Announcing: {object_name}")
                            speech.announce_critical_object(object_name, distance)
                        else:
                            print(f"{zone_icon} {distance:6.2f}cm | {zone:8s} | 👁️  Detected: {object_name} (too far to announce)", end='\r')
                    else:
                        print(f"{zone_icon} {distance:6.2f}cm | {zone:8s} | No objects ahead", end='\r')
                else:
                    print(f"{zone_icon} {distance:6.2f}cm | {zone:8s} | No detections", end='\r')
            else:
                print(f"{zone_icon} {distance:6.2f}cm | {zone:8s}", end='\r')
            
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
