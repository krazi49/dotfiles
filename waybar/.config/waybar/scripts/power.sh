#!/bin/bash

BAT_PATH=$(find /sys/class/power_supply/ -name "BAT*" | head -n 1)
CAP=$(cat "$BAT_PATH/capacity" 2>/dev/null || echo "0")
STAT=$(cat "$BAT_PATH/status" 2>/dev/null || echo "Unknown")

# Get extra data for the tooltip
VOLT=$(awk '{printf "%.2fV", $1/1000000}' "$BAT_PATH/voltage_now")
WATT=$(awk '{printf "%.2fW", $1/1000000}' "$BAT_PATH/power_now")

# Logic for Icon & State
if [[ "$STAT" == "Charging" ]]; then
  ICONCHG="󱐋"
  STATE="charging"
elif [[ "$STAT" == "Full" || "$STAT" == "Not charging" ]]; then
  ICON=""
  STATE="plugged"
else
  ICON="󰁹"
  STATE="discharging"
fi

# Tooltip content (using \n for new lines)
TOOLTIP="<b>Status:</b> $STAT\n<b>Health:</b> $CAP%\n<b>Voltage:</b> $VOLT"

# Output JSON with the tooltip field
if [[ "$STAT" == "Full" ]] || [[ "$STAT" == "Not charging" ]]; then
  echo "{\"text\": \" $ICON  $CAP \", \"class\": \"$STATE\", \"tooltip\": \"$TOOLTIP\"}"
elif [[ "$STAT" == "Charging" ]]; then
  echo "{\"text\": \" $ICONCHG $CAP \", \"class\": \"$STATE\", \"tooltip\": \"$TOOLTIP\"}"
else
  echo "{\"text\": \" $CAP \", \"class\": \"$STATE\", \"tooltip\": \"$TOOLTIP\"}"
fi
