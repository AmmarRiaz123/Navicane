#!/bin/bash

# Watchdog script to ensure smart-cane service stays running
# Run this as a cron job every minute

SERVICE="smart-cane"
LOG_FILE="/home/pi1_/Navicane/watchdog.log"

# Check if service is active
if ! systemctl is-active --quiet $SERVICE; then
    echo "$(date): Service $SERVICE is not running, restarting..." >> $LOG_FILE
    systemctl start $SERVICE
    sleep 5
    
    if systemctl is-active --quiet $SERVICE; then
        echo "$(date): Service $SERVICE restarted successfully" >> $LOG_FILE
    else
        echo "$(date): Failed to restart service $SERVICE" >> $LOG_FILE
    fi
else
    # Service is running, check if it's responsive
    LAST_LOG_TIME=$(stat -c %Y /home/pi1_/Navicane/smart_cane.log 2>/dev/null || echo 0)
    CURRENT_TIME=$(date +%s)
    TIME_DIFF=$((CURRENT_TIME - LAST_LOG_TIME))
    
    # If no log activity for 5 minutes, restart
    if [ $TIME_DIFF -gt 300 ]; then
        echo "$(date): Service $SERVICE appears frozen (no logs for ${TIME_DIFF}s), restarting..." >> $LOG_FILE
        systemctl restart $SERVICE
    fi
fi
