#!/bin/bash

# Initialize audio system for smart cane service
# This ensures Bluetooth and PulseAudio are ready

echo "🔊 Initializing audio system for smart-cane..."

# Get user info
USER_NAME=$(whoami)
USER_ID=$(id -u)

echo "👤 User: $USER_NAME (UID: $USER_ID)"

# Wait for user session (max 30 seconds)
echo "⏳ Waiting for user session..."
timeout=30
count=0
while [ ! -d "/run/user/$USER_ID" ] && [ $count -lt $timeout ]; do
    sleep 1
    count=$((count + 1))
done

if [ ! -d "/run/user/$USER_ID" ]; then
    echo "❌ User session timeout - continuing anyway"
else
    echo "✅ User session ready"
fi

# Set audio environment
export XDG_RUNTIME_DIR="/run/user/$USER_ID"
export PULSE_RUNTIME_PATH="/run/user/$USER_ID/pulse"

# Wait for PulseAudio (max 20 seconds)
echo "⏳ Waiting for PulseAudio..."
PULSE_SERVER="/run/user/$USER_ID/pulse/native"
timeout=20
count=0
while [ ! -S "$PULSE_SERVER" ] && [ $count -lt $timeout ]; do
    sleep 1
    count=$((count + 1))
done

if [ -S "$PULSE_SERVER" ]; then
    echo "✅ PulseAudio ready"
    
    # Set volume
    pactl set-sink-volume @DEFAULT_SINK@ 100% 2>/dev/null && echo "🔊 Volume set to 100%" || echo "⚠️ Could not set volume"
    
    # Test audio
    espeak "Audio system ready" -a 200 2>/dev/null && echo "✅ Audio test successful" || echo "⚠️ Audio test failed"
else
    echo "⚠️ PulseAudio not ready - audio may not work"
fi

echo "🏁 Audio initialization complete - starting main program"

# Exit successfully to allow service to continue
exit 0
