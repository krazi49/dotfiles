#!/bin/bash

# --- Data Gathering ---
BAT_PATH=$(find /sys/class/power_supply/ -name "BAT*" | head -n 1)
CAP=$(cat "$BAT_PATH/capacity" 2>/dev/null || echo "0")
STAT=$(cat "$BAT_PATH/status" 2>/dev/null || echo "Unknown")

# --- Logic for Icons ---
if [[ "$STAT" == "Full" || "$STAT" == "Not charging" ]]; then
  # Full or Plugged but not drawing power (Cable Icon)
  echo "(  $CAP% )"
elif [[ "$STAT" == "Charging" ]]; then
  # Active Charging (Bolt Icon)
  echo "( 󱐋 $CAP% )"
else
  # Unplugged / Discharging (Nothing but the number)
  echo "( 󰁅 $CAP% )"
fi
