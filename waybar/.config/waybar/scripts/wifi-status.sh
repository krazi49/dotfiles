#!/bin/bash

# Get signal strength (0-100)
STRENGTH=$(nmcli -t -f IN-USE,SIGNAL dev wifi | grep '^\*' | cut -d: -f2)

if [ -z "$STRENGTH" ]; then
  echo "󰖪" # Disconnected icon
elif [ "$STRENGTH" -gt 75 ]; then
  echo "󰤨" # Strong
elif [ "$STRENGTH" -gt 50 ]; then
  echo "󰤥" # Medium
elif [ "$STRENGTH" -gt 25 ]; then
  echo "󰤢" # Weak
else
  echo "󰤟" # Very Weak
fi
