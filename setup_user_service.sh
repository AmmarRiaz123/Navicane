#!/bin/bash

echo "========================================"
echo "Smart Cane - User Service Setup"
echo "Runs as user service (better audio)"
echo "========================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
USER_SERVICE_DIR="$HOME/.config/systemd/user"

# Create user service directory
mkdir -p "$USER_SERVICE_DIR"

# Create user service file
cat > "$USER_SERVICE_DIR/smart-cane.service" << EOF
[Unit]
Description=Smart Cane System
After=pulseaudio.service bluetooth.target

[Service]
Type=simple
WorkingDirectory=$SCRIPT_DIR
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStartPre=/bin/sleep 5
ExecStart=/usr/bin/python3 -u $SCRIPT_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=append:$SCRIPT_DIR/smart_cane.log
StandardError=append:$SCRIPT_DIR/smart_cane.log

[Install]
WantedBy=default.target
EOF

echo "✓ User service file created"

# Reload and enable
systemctl --user daemon-reload
systemctl --user enable smart-cane.service

# Enable lingering (service runs even when not logged in)
sudo loginctl enable-linger $USER

echo ""
echo "========================================"
echo "User Service Setup Complete!"
echo "========================================"
echo ""
echo "Commands:"
echo "  Start:   systemctl --user start smart-cane"
echo "  Stop:    systemctl --user stop smart-cane"
echo "  Status:  systemctl --user status smart-cane"
echo "  Logs:    tail -f $SCRIPT_DIR/smart_cane.log"
echo ""
echo "⚠ Note: User service has better audio access"
echo "   This is recommended for Bluetooth headphones"
echo ""
