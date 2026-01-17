#!/bin/bash

echo "Fixing smart-cane service..."

# Stop the service
sudo systemctl stop smart-cane

# Copy the simple service file (no audio init script)
sudo cp /home/pi1_/Navicane/smart-cane-simple.service /etc/systemd/system/smart-cane.service

# Reload systemd
sudo systemctl daemon-reload

# Restart service
sudo systemctl restart smart-cane

sleep 3

# Show status
sudo systemctl status smart-cane --no-pager

echo ""
echo "Checking logs..."
tail -20 /home/pi1_/Navicane/smart_cane.log

echo ""
echo "Done! Service should now start properly."
echo "Watch logs: tail -f ~/Navicane/smart_cane.log"
