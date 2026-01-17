#!/bin/bash

echo "Installing watchdog cron job..."

# Add cron job to run watchdog every minute
(crontab -l 2>/dev/null | grep -v "watchdog.sh"; echo "* * * * * /home/pi1_/Navicane/watchdog.sh") | crontab -

echo "✓ Watchdog installed"
echo ""
echo "Watchdog will check service every minute"
echo "View watchdog logs: tail -f ~/Navicane/watchdog.log"
echo ""
echo "To remove watchdog:"
echo "  crontab -e"
echo "  (delete the line with watchdog.sh)"
