#!/bin/bash
USER_NAME=$(whoami)
USER_ID=$(id -u)
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$USER_ID/bus"

# Check if plugging in (1) or unplugging (0)
STATUS=$(cat /sys/class/power_supply/AC/online)

if [ "$STATUS" -eq 1 ]; then
  pw-play "$HOME/sounds/started-charging.wav"
fi
