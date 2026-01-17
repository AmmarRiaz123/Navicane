#!/bin/bash

echo "Audio System Diagnostics"
echo "=" | sed 's/./=/g' | head -c 50; echo ""

echo -e "\n1. User ID and Runtime Directory"
echo "Current User: $(whoami)"
echo "User ID: $(id -u)"
echo "Runtime Dir: $XDG_RUNTIME_DIR"
ls -la /run/user/$(id -u)/ 2>/dev/null | head -5

echo -e "\n2. PulseAudio Status"
pactl info 2>&1 | head -5

echo -e "\n3. Audio Sinks"
pactl list short sinks

echo -e "\n4. Default Sink"
pactl get-default-sink

echo -e "\n5. Volume"
pactl get-sink-volume @DEFAULT_SINK@

echo -e "\n6. Bluetooth Status"
bluetoothctl show | grep -E "Powered|Pairable|Discoverable"

echo -e "\n7. Connected Devices"
bluetoothctl devices Connected

echo -e "\n8. Test espeak"
espeak "Audio test" -a 200

echo -e "\nDiagnostics complete"
