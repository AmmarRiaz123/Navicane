#!/bin/bash

echo "=" | sed 's/./ /g' | tr ' ' '='
echo "Testing All Running Modes"
echo "=" | sed 's/./ /g' | tr ' ' '='
echo ""

cd ~/Navicane

echo "Test 1: Direct Run"
echo "-" | sed 's/./ /g' | tr ' ' '-'
echo "Running: python3 main.py"
echo "This will run for 10 seconds..."
timeout 10 python3 main.py &
PID=$!
sleep 10
kill $PID 2>/dev/null
wait $PID 2>/dev/null
echo "✓ Direct run test complete"
echo ""

echo "Test 2: Debug Run"
echo "-" | sed 's/./ /g' | tr ' ' '-'
echo "Running: python3 run_main_debug.py"
echo "This will run for 10 seconds..."
timeout 10 python3 run_main_debug.py &
PID=$!
sleep 10
kill $PID 2>/dev/null
wait $PID 2>/dev/null
echo "✓ Debug run test complete"
echo ""

echo "Test 3: Service Status"
echo "-" | sed 's/./ /g' | tr ' ' '-'
sudo systemctl status smart-cane --no-pager
echo ""

echo "Test 4: Recent Service Logs"
echo "-" | sed 's/./ /g' | tr ' ' '-'
tail -20 ~/Navicane/smart_cane.log
echo ""

echo "=" | sed 's/./ /g' | tr ' ' '='
echo "All Tests Complete"
echo "=" | sed 's/./ /g' | tr ' ' '='
echo ""
echo "If all tests passed:"
echo "  • Direct run works"
echo "  • Debug run works"
echo "  • Service is active"
echo "  • Logs show activity"
echo ""
echo "To restart service: sudo systemctl restart smart-cane"
echo "To view live logs: tail -f ~/Navicane/smart_cane.log"
