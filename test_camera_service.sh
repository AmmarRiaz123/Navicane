#!/bin/bash

echo "Testing Camera in Service-like Environment"
echo "=" | sed 's/./=/g' | head -c 60; echo "="
echo ""

# Test as the service user with service environment
echo "1. Testing rpicam-still directly"
echo "-" | sed 's/./-/g' | head -c 60; echo "-"
rpicam-still --help 2>&1 | head -3
echo ""

echo "2. Test capture to /tmp"
echo "-" | sed 's/./-/g' | head -c 60; echo "-"
TEST_FILE="/tmp/camera_test_$(date +%s).jpg"
echo "Capturing to: $TEST_FILE"
rpicam-still -o "$TEST_FILE" --width 640 --height 480 --nopreview --timeout 1 --immediate 2>&1
if [ -f "$TEST_FILE" ] && [ -s "$TEST_FILE" ]; then
    SIZE=$(du -h "$TEST_FILE" | cut -f1)
    echo "✓ Capture successful: $SIZE"
    rm "$TEST_FILE"
else
    echo "✗ Capture failed"
fi
echo ""

echo "3. Test with Python"
echo "-" | sed 's/./-/g' | head -c 60; echo "-"
python3 << 'EOF'
import subprocess
import os

try:
    test_file = "/tmp/python_camera_test.jpg"
    result = subprocess.run(
        ['rpicam-still', '-o', test_file, '--width', '640', '--height', '480',
         '--nopreview', '--timeout', '1', '--immediate'],
        capture_output=True,
        timeout=10
    )
    
    if result.returncode == 0 and os.path.exists(test_file) and os.path.getsize(test_file) > 0:
        print(f"✓ Python capture successful: {os.path.getsize(test_file)} bytes")
        os.remove(test_file)
    else:
        print(f"✗ Python capture failed: returncode={result.returncode}")
        if result.stderr:
            print(f"Error: {result.stderr.decode()}")
except Exception as e:
    print(f"✗ Exception: {e}")
EOF

echo ""
echo "=" | sed 's/./=/g' | head -c 60; echo "="
echo "Test Complete"
echo ""
echo "If all tests pass but service fails:"
echo "  1. Camera works but needs delay"
echo "  2. Try increasing ExecStartPre sleep time"
echo "  3. Check service logs: sudo journalctl -u smart-cane -n 50"
