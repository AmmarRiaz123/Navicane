#!/bin/bash

# Initialize audio system for smart cane service
# This ensures Bluetooth and PulseAudio are ready

echo "Initializing audio system for smart-cane..."

# Wait for user session
USER_ID=$(id -u pi1_)
echo "Waiting for user session (UID: $USER_ID)..."
while [ ! -d "/run/user/$USER_ID" ]; do
    sleep 1
done
echo "✓ User session ready"

# Wait for PulseAudio
echo "Waiting for PulseAudio..."
PULSE_SERVER="/run/user/$USER_ID/pulse/native"
timeout=30
count=0
while [ ! -S "$PULSE_SERVER" ] && [ $count -lt $timeout ]; do
    sleep 1
    count=$((count + 1))
done

if [ -S "$PULSE_SERVER" ]; then
    echo "✓ PulseAudio ready"
else
    echo "⚠ PulseAudio socket not found, continuing anyway..."
fi

# Set audio volume to maximum
export XDG_RUNTIME_DIR="/run/user/$USER_ID"
export PULSE_RUNTIME_PATH="/run/user/$USER_ID/pulse"

pactl set-sink-volume @DEFAULT_SINK@ 100% 2>/dev/null || echo "⚠ Could not set volume"

# Test audio
espeak "Audio system ready" -a 200 2>/dev/null && echo "✓ Audio test successful" || echo "⚠ Audio test failed"

echo "Audio initialization complete"
