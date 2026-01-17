#!/bin/bash

echo "=" | sed 's/./=/g' | head -c 60; echo "="
echo "Smart Cane - Permission Verification"
echo "=" | sed 's/./=/g' | head -c 60; echo "="
echo ""

USER=${1:-$USER}

echo "Checking permissions for user: $USER"
echo ""

echo "1. User Groups"
echo "-" | sed 's/./-/g' | head -c 60; echo "-"
groups $USER
echo ""

echo "2. GPIO Access"
echo "-" | sed 's/./-/g' | head -c 60; echo "-"
if [ -r /dev/gpiomem ]; then
    echo "✓ /dev/gpiomem is readable"
else
    echo "✗ /dev/gpiomem is NOT readable"
fi
ls -l /dev/gpiomem
echo ""

echo "3. Video/Camera Access"
echo "-" | sed 's/./-/g' | head -c 60; echo "-"
if [ -r /dev/video0 ]; then
    echo "✓ /dev/video0 is readable"
    ls -l /dev/video0
else
    echo "⚠ /dev/video0 not found (camera may not be connected)"
fi
echo ""

echo "4. Audio Access"
echo "-" | sed 's/./-/g' | head -c 60; echo "-"
if [ -d /dev/snd ]; then
    echo "✓ /dev/snd exists"
    ls -l /dev/snd/ | head -5
else
    echo "✗ /dev/snd not found"
fi
echo ""

echo "5. PulseAudio Runtime"
echo "-" | sed 's/./-/g' | head -c 60; echo "-"
USER_ID=$(id -u $USER)
if [ -d "/run/user/$USER_ID/pulse" ]; then
    echo "✓ PulseAudio runtime directory exists"
    ls -la "/run/user/$USER_ID/pulse/" | head -5
else
    echo "⚠ PulseAudio runtime not found for user $USER"
fi
echo ""

echo "6. Bluetooth Access"
echo "-" | sed 's/./-/g' | head -c 60; echo "-"
if command -v bluetoothctl &> /dev/null; then
    echo "✓ bluetoothctl is available"
    bluetoothctl show | grep -E "Powered|Name" || echo "Bluetooth controller info unavailable"
else
    echo "✗ bluetoothctl not found"
fi
echo ""

echo "7. Service Status"
echo "-" | sed 's/./-/g' | head -c 60; echo "-"
systemctl is-enabled smart-cane 2>/dev/null && echo "✓ Service is enabled" || echo "✗ Service is not enabled"
systemctl is-active smart-cane 2>/dev/null && echo "✓ Service is running" || echo "✗ Service is not running"
echo ""

echo "=" | sed 's/./=/g' | head -c 60; echo "="
echo "Verification Complete"
echo "=" | sed 's/./=/g' | head -c 60; echo "="
echo ""

if ! groups $USER | grep -q gpio; then
    echo "⚠ User not in gpio group. Run: sudo usermod -a -G gpio $USER"
fi

if ! groups $USER | grep -q video; then
    echo "⚠ User not in video group. Run: sudo usermod -a -G video $USER"
fi

if ! groups $USER | grep -q audio; then
    echo "⚠ User not in audio group. Run: sudo usermod -a -G audio $USER"
fi

echo ""
echo "If groups were added, reboot is required:"
echo "  sudo reboot"
