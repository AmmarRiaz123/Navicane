"""
Test speech timing and critical announcements
"""

import time
from speech import SmartSpeech

def main():
    print("=" * 70)
    print("SPEECH TIMING TEST")
    print("=" * 70)
    print("\nTesting speech behavior:")
    print("  1. Normal cooldown (2 seconds)")
    print("  2. Critical override (< 30cm bypasses cooldown)")
    print("\n" + "=" * 70)
    
    speech = SmartSpeech()
    
    try:
        # Test 1: Normal cooldown
        print("\n--- TEST 1: Normal Cooldown (50cm distance) ---")
        print("Announcing 'person' at 50cm...")
        speech.announce_critical_object('person', 50)
        time.sleep(0.5)
        
        print("Trying to announce again immediately (should skip)...")
        result = speech.announce_critical_object('person', 50)
        if not result:
            print("✓ Correctly skipped (cooldown active)")
        
        print("Waiting 2 seconds for cooldown...")
        time.sleep(2)
        
        print("Announcing again after cooldown...")
        speech.announce_critical_object('person', 50)
        
        time.sleep(3)
        
        # Test 2: Critical override
        print("\n--- TEST 2: Critical Override (< 30cm) ---")
        print("Announcing 'chair' at 25cm...")
        speech.announce_critical_object('chair', 25)
        time.sleep(0.5)
        
        print("Trying critical announcement immediately (should FORCE speak)...")
        speech.announce_critical_object('car', 20)
        time.sleep(0.5)
        
        print("Another critical (should FORCE speak again)...")
        speech.announce_critical_object('person', 15)
        
        time.sleep(3)
        
        # Test 3: Rapid critical announcements
        print("\n--- TEST 3: Rapid Critical Announcements ---")
        critical_distances = [28, 25, 20, 15, 10]
        objects = ['person', 'chair', 'car', 'person', 'chair']
        
        for dist, obj in zip(critical_distances, objects):
            print(f"Critical: {obj} at {dist}cm")
            speech.announce_critical_object(obj, dist)
            time.sleep(1.5)
        
        print("\n✓ Test complete!")
        
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        time.sleep(2)
        speech.cleanup()

if __name__ == "__main__":
    main()
