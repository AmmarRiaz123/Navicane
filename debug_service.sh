#!/bin/bash

echo "=" | sed 's/./=/g' | head -c 70; echo "="
echo "Smart Cane Service Debugging"
echo "=" | sed 's/./=/g' | head -c 70; echo "="
echo ""

echo "1. Service Status"
echo "-" | sed 's/./-/g' | head -c 70; echo "-"
sudo systemctl status smart-cane --no-pager
echo ""

echo "2. Last 30 Lines of Service Logs"
echo "-" | sed 's/./-/g' | head -c 70; echo "-"
tail -30 ~/Navicane/smart_cane.log
echo ""

echo "3. Systemd Journal (Last 20 Lines)"
echo "-" | sed 's/./-/g' | head -c 70; echo "-"
sudo journalctl -u smart-cane -n 20 --no-pager
echo ""

echo "4. Check for Errors"
echo "-" | sed 's/./-/g' | head -c 70; echo "-"
grep -i "error\|critical\|fatal" ~/Navicane/smart_cane.log | tail -10
echo ""

echo "5. Thread Status Check"
echo "-" | sed 's/./-/g' | head -c 70; echo "-"
ps aux | grep -E "python3.*main.py" | grep -v grep
echo ""

echo "6. Memory/CPU Usage"
echo "-" | sed 's/./-/g' | head -c 70; echo "-"
ps aux | grep -E "python3.*main.py" | grep -v grep | awk '{print "CPU: "$3"% MEM: "$4"%"}'
echo ""

echo "=" | sed 's/./=/g' | head -c 70; echo "="
echo "Debug Complete"
echo "=" | sed 's/./=/g' | head -c 70; echo "="
