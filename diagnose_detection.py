"""
Diagnose why camera isn't detecting/speaking
"""

import time
from ultrasonic import UltrasonicArray
from camera import CameraManager
from speech import SmartSpeech
from config import SPEECH_TRIGGER_DISTANCE, CAMERA_TRIGGER_DISTANCE, CONFIDENCE_THRESHOLD

def main():
    print("=" * 70)
    print("DETECTION DIAGNOSTICS")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Camera trigger distance: {CAMERA_TRIGGER_DISTANCE}cm")
    print(f"  Speech trigger distance: {SPEECH_TRIGGER_DISTANCE}cm")
    print(f"  Confidence threshold: {CONFIDENCE_THRESHOLD}")
    print(f"\n" + "=" * 70)
    
    sensor = UltrasonicArray()
    camera = CameraManager()
    speech = SmartSpeech()
    
    print("\nTest 1: Speech System")
    print("-" * 70)
    speech.speak_urgent("Testing speech system")
    time.sleep(2)
    print("✓ If you heard 'Testing speech system', speech works\n")
    
    print("Test 2: Camera Detection")
    print("-" * 70)
    print("Point camera at a person, chair, or object...")
    time.sleep(2)
    
    for i in range(3):
        print(f"\nAttempt {i+1}/3:")
        detections = camera.detect_objects()
        
        if detections:
            print(f"✓ Camera detected {len(detections)} objects:")
            for name, is_center, conf, box in detections:
                position = "AHEAD" if is_center else "SIDE"
                print(f"  • {name} ({position}) - confidence: {conf:.2f}")
        else:
            print("✗ No objects detected")
            print("  Try: Point camera at person, chair, or common object")
        
        time.sleep(2)
    
    print("\n" + "=" * 70)
    print("Test 3: Full System Integration")
    print("-" * 70)
    print("Move your hand near the sensor (< 100cm)...")
    
    for i in range(5):
        distance = sensor.read_distance()
        
        if distance is None:
            print("✗ No sensor reading")
            continue
        
        print(f"\nDistance: {distance:.1f}cm")
        
        if distance > CAMERA_TRIGGER_DISTANCE:
            print(f"  ⚪ Too far for detection (> {CAMERA_TRIGGER_DISTANCE}cm)")
            continue
        
        print(f"  ✓ Within camera range, detecting...")
        detections = camera.detect_objects()
        
        if detections:
            center_objects = [(name, conf) for name, is_center, conf, box 
                            in detections if is_center]
            
            if center_objects:
                best = max(center_objects, key=lambda x: x[1])
                object_name, confidence = best
                
                print(f"  ✓ Detected: {object_name} (conf={confidence:.2f})")
                
                if distance < SPEECH_TRIGGER_DISTANCE:
                    print(f"  🔊 SPEAKING: {object_name}")
                    speech.announce_critical_object(object_name, distance)
                else:
                    print(f"  🔇 Silent (distance {distance:.1f}cm > trigger {SPEECH_TRIGGER_DISTANCE}cm)")
            else:
                print("  ⚠ Objects detected but not in center")
        else:
            print("  ✗ No objects detected")
        
        time.sleep(2)
    
    print("\n" + "=" * 70)
    print("Diagnosis Complete")
    print("=" * 70)
    print("\nIf issues persist:")
    print("  1. Check logs: tail -f ~/Navicane/smart_cane.log")
    print("  2. Check system status: sudo systemctl status smart-cane")
    print("  3. Check volume: amixer get PCM")
    
    camera.cleanup()
    sensor.cleanup()
    speech.cleanup()

if __name__ == "__main__":
    main()
