#!/bin/bash
echo "Clearing Arduino port..."
lsof /dev/ttyACM0 2>/dev/null | grep -v COMMAND | awk '{print $2}' | xargs -r kill -9
sleep 2
echo "Port cleared. Ready to run hand tracker."
