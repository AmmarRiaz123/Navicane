#!/bin/bash

# Smart Cane Control Script
# Quick commands for managing the service

case "$1" in
    start)
        echo "Starting Smart Cane..."
        sudo systemctl start smart-cane
        ;;
    stop)
        echo "Stopping Smart Cane..."
        sudo systemctl stop smart-cane
        ;;
    restart)
        echo "Restarting Smart Cane..."
        sudo systemctl restart smart-cane
        ;;
    status)
        sudo systemctl status smart-cane --no-pager
        ;;
    logs)
        tail -f ~/Navicane/smart_cane.log
        ;;
    enable)
        echo "Enabling auto-start..."
        sudo systemctl enable smart-cane
        ;;
    disable)
        echo "Disabling auto-start..."
        sudo systemctl disable smart-cane
        ;;
    *)
        echo "Smart Cane Control"
        echo ""
        echo "Usage: bash control_cane.sh [command]"
        echo ""
        echo "Commands:"
        echo "  start    - Start the service"
        echo "  stop     - Stop the service"
        echo "  restart  - Restart the service"
        echo "  status   - Show service status"
        echo "  logs     - Show live logs"
        echo "  enable   - Enable auto-start on boot"
        echo "  disable  - Disable auto-start"
        echo ""
        ;;
esac
