#!/bin/bash

echo "========================================"
echo "Smart Cane - Auto-Start Setup"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root: sudo bash setup_autostart.sh"
    exit 1
fi

# Detect user
ACTUAL_USER=${SUDO_USER:-$USER}
USER_HOME=$(eval echo ~$ACTUAL_USER)

echo "Setting up auto-start for user: $ACTUAL_USER"
echo "Home directory: $USER_HOME"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Project directory: $SCRIPT_DIR"
echo ""

# Add user to all required groups
echo "Adding $ACTUAL_USER to hardware access groups..."
usermod -a -G gpio $ACTUAL_USER
usermod -a -G video $ACTUAL_USER
usermod -a -G audio $ACTUAL_USER
usermod -a -G bluetooth $ACTUAL_USER
usermod -a -G pulse-access $ACTUAL_USER 2>/dev/null || echo "  (pulse-access group doesn't exist, skipping)"

echo "✓ User added to groups:"
groups $ACTUAL_USER

echo ""

# Copy init_audio.sh script
if [ -f "$SCRIPT_DIR/init_audio.sh" ]; then
    chmod +x "$SCRIPT_DIR/init_audio.sh"
    chown $ACTUAL_USER:$ACTUAL_USER "$SCRIPT_DIR/init_audio.sh"
    echo "✓ Audio init script configured"
fi

# Get user ID for audio environment
USER_ID=$(id -u $ACTUAL_USER)

# Update service file with correct user and paths
echo "Creating systemd service file..."
cat > /etc/systemd/system/smart-cane.service << EOF
[Unit]
Description=Smart Cane System for Blind Users
Documentation=https://github.com/AmmarRiaz123/Navicane
After=multi-user.target network.target sound.target bluetooth.target
Wants=sound.target bluetooth.target

[Service]
Type=simple
User=$ACTUAL_USER
Group=$ACTUAL_USER

# Add user to multiple groups for hardware access
SupplementaryGroups=video audio gpio bluetooth pulse-access

WorkingDirectory=$SCRIPT_DIR

# Environment variables for audio and hardware access
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
Environment="PYTHONIOENCODING=utf-8"
Environment="XDG_RUNTIME_DIR=/run/user/$USER_ID"
Environment="PULSE_RUNTIME_PATH=/run/user/$USER_ID/pulse"
Environment="DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$USER_ID/bus"

# Initialize audio system first
ExecStartPre=$SCRIPT_DIR/init_audio.sh

# Start main program
ExecStart=/usr/bin/python3 -u $SCRIPT_DIR/main.py

Restart=always
RestartSec=10
StandardOutput=append:$SCRIPT_DIR/smart_cane.log
StandardError=append:$SCRIPT_DIR/smart_cane.log

# Security settings (relaxed for hardware access)
NoNewPrivileges=true
PrivateTmp=true

# Allow access to devices
DeviceAllow=/dev/gpiomem rw
DeviceAllow=/dev/video0 rw
DeviceAllow=/dev/snd rw
DevicePolicy=closed

# Resource limits
MemoryMax=2G
CPUQuota=80%

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Service file created"
echo ""

# Reload systemd
echo "Reloading systemd..."
systemctl daemon-reload
echo "✓ Systemd reloaded"
echo ""

# Enable service
echo "Enabling smart-cane service..."
systemctl enable smart-cane.service
echo "✓ Service enabled (will start on boot)"
echo ""

# Ask if user wants to start now
read -p "Start service now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting service..."
    systemctl start smart-cane.service
    sleep 2
    
    echo ""
    echo "Service status:"
    systemctl status smart-cane.service --no-pager
else
    echo "Service will start on next boot"
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "User $ACTUAL_USER is now in these groups:"
groups $ACTUAL_USER
echo ""
echo "Service commands:"
echo "  Start:   sudo systemctl start smart-cane"
echo "  Stop:    sudo systemctl stop smart-cane"
echo "  Restart: sudo systemctl restart smart-cane"
echo "  Status:  sudo systemctl status smart-cane"
echo "  Logs:    tail -f $SCRIPT_DIR/smart_cane.log"
echo "  Disable: sudo systemctl disable smart-cane"
echo ""
echo "⚠ IMPORTANT: You may need to reboot for group changes to take effect:"
echo "   sudo reboot"
echo ""
