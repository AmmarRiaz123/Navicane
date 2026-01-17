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

# Update service file with correct user and paths
echo "Creating systemd service file..."
cat > /etc/systemd/system/smart-cane.service << EOF
[Unit]
Description=Smart Cane System for Blind Users
Documentation=https://github.com/AmmarRiaz123/Navicane
After=multi-user.target network.target

[Service]
Type=simple
User=$ACTUAL_USER
Group=$ACTUAL_USER
WorkingDirectory=$SCRIPT_DIR
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
Environment="PYTHONIOENCODING=utf-8"
ExecStart=/usr/bin/python3 -u $SCRIPT_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=append:$SCRIPT_DIR/smart_cane.log
StandardError=append:$SCRIPT_DIR/smart_cane.log

# Security settings
NoNewPrivileges=true
PrivateTmp=true

# Resource limits
MemoryMax=2G
CPUQuota=80%

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Service file created"
echo ""

# Add user to gpio group
echo "Adding $ACTUAL_USER to gpio group..."
usermod -a -G gpio $ACTUAL_USER
echo "✓ User added to gpio group"
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
echo "Service commands:"
echo "  Start:   sudo systemctl start smart-cane"
echo "  Stop:    sudo systemctl stop smart-cane"
echo "  Restart: sudo systemctl restart smart-cane"
echo "  Status:  sudo systemctl status smart-cane"
echo "  Logs:    tail -f $SCRIPT_DIR/smart_cane.log"
echo "  Disable: sudo systemctl disable smart-cane"
echo ""
echo "⚠ Reboot recommended to test auto-start:"
echo "   sudo reboot"
echo ""
