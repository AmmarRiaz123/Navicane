"""
Test speech in isolation
"""

from speech import SmartSpeech
import time

print("Testing Speech System")
print("=" * 50)

speech = SmartSpeech()

print("\nTest 1: Basic speech")
speech.speak_urgent("Test one")
time.sleep(2)

print("\nTest 2: Critical announcement at 25cm")
result = speech.announce_critical_object('person', 25)
print(f"Result: {result}")
time.sleep(3)

print("\nTest 3: Normal announcement at 50cm")
result = speech.announce_critical_object('chair', 50)
print(f"Result: {result}")
time.sleep(3)

print("\nTest 4: Rapid announcements")
for i in range(3):
    result = speech.announce_critical_object('person', 20)
    print(f"Attempt {i+1}: {result}")
    time.sleep(1)

print("\n✓ Test complete")
speech.cleanup()
