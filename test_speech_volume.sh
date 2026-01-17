#!/bin/bash

echo "Testing Speech Volume Levels"
echo "============================="
echo ""

# Set system volume to maximum
echo "Setting system volume to maximum..."
amixer set PCM 100% > /dev/null 2>&1
echo "✓ System volume: 100%"
echo ""

# Test different espeak amplitude levels
echo "Testing espeak amplitude levels:"
echo ""

for amp in 100 150 200; do
    echo "Amplitude $amp:"
    espeak "Testing volume at amplitude $amp" -a $amp -s 150
    sleep 1
done

echo ""
echo "Testing with speech.py (amplitude 200):"
python3 << 'EOF'
from speech import SmartSpeech
speech = SmartSpeech()
speech.speak_urgent("This is maximum volume test")
import time
time.sleep(3)
speech.cleanup()
EOF

echo ""
echo "✓ Test complete!"
echo ""
echo "If still not loud enough, check:"
echo "  1. Physical speaker/headphone volume"
echo "  2. Audio output device: sudo raspi-config → System Options → Audio"
echo "  3. Run: alsamixer (adjust volume manually)"
