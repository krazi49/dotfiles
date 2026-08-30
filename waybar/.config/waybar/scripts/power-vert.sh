#!/bin/bash

# File to track toggle state (0 = show bar, 1 = show percentage)
TOGGLE_FILE="/tmp/waybar_battery_toggle"

# Check if script was called by a click to toggle view mode
if [[ "$1" == "--toggle" ]]; then
  if [[ -f "$TOGGLE_FILE" ]]; then
    rm -f "$TOGGLE_FILE"
  else
    echo "1" >"$TOGGLE_FILE"
  fi
  # Signal waybar to refresh immediately
  pkill -RTMIN+8 waybar
  exit 0
fi

BAT_PATH=$(find /sys/class/power_supply/ -name "BAT*" | head -n 1)
CAP=$(cat "$BAT_PATH/capacity" 2>/dev/null || echo "0")
STAT=$(cat "$BAT_PATH/status" 2>/dev/null || echo "Unknown")
VOLT=$(awk '{printf "%.2fV", $1/1000000}' "$BAT_PATH/voltage_now" 2>/dev/null || echo "N/A")
WATT=$(awk '{printf "%.2fW", $1/1000000}' "$BAT_PATH/power_now" 2>/dev/null || echo "N/A")

# --- Calculate time remaining ---
CHARGE_NOW=$(cat "$BAT_PATH/charge_now" 2>/dev/null || echo "")
CHARGE_FULL=$(cat "$BAT_PATH/charge_full" 2>/dev/null || echo "")
CURRENT_NOW=$(cat "$BAT_PATH/current_now" 2>/dev/null || echo "")
TIME_STR="N/A"

if [[ -n "$CURRENT_NOW" && "$CURRENT_NOW" -gt 0 ]]; then
  if [[ "$STAT" == "Discharging" && -n "$CHARGE_NOW" ]]; then
    TIME_STR=$(awk -v c="$CHARGE_NOW" -v i="$CURRENT_NOW" 'BEGIN {
      h = c / i; hrs = int(h); mins = int((h - hrs) * 60)
      printf "%dh %02dm", hrs, mins
    }')
  elif [[ "$STAT" == "Charging" && -n "$CHARGE_FULL" && -n "$CHARGE_NOW" ]]; then
    TIME_STR=$(awk -v f="$CHARGE_FULL" -v c="$CHARGE_NOW" -v i="$CURRENT_NOW" 'BEGIN {
      h = (f - c) / i; hrs = int(h); mins = int((h - hrs) * 60)
      printf "%dh %02dm", hrs, mins
    }')
  fi
fi

# --- Progress bar ---
BAR_WIDTH=10
FILLED=$(echo "($CAP * $BAR_WIDTH) / 100" | bc)
EMPTY=$(($BAR_WIDTH - FILLED))
BAR=""
for i in $(seq 1 $FILLED); do BAR="${BAR}━"; done
for i in $(seq 1 $EMPTY); do BAR="${BAR}╌"; done

# --- Flash Event Handlers ---
FLASH_FILE="/tmp/waybar_battery_flash"
PREV_STAT_FILE="/tmp/waybar_battery_prev_stat"
PREV_STAT=$(cat "$PREV_STAT_FILE" 2>/dev/null || echo "")
FLASH_ACTIVE=0
FLASH_ICON=""

if [[ -n "$PREV_STAT" && "$PREV_STAT" != "$STAT" ]]; then
  if [[ "$STAT" == "Charging" ]]; then
    echo "$(date +%s) plug" >"$FLASH_FILE"
  elif [[ "$STAT" == "Discharging" ]]; then
    if [[ "$PREV_STAT" == "Full" || "$CAP" -eq 100 ]]; then
      echo "$(date +%s) unplug_full" >"$FLASH_FILE" # Unplugged from full event
    else
      echo "$(date +%s) unplug" >"$FLASH_FILE"
    fi
  fi
fi
echo "$STAT" >"$PREV_STAT_FILE"

# Process temporary transitions (Plugs / Unplugs)
if [[ -f "$FLASH_FILE" ]]; then
  read -r FLASH_TS FLASH_TYPE <"$FLASH_FILE"
  AGE=$(($(date +%s) - FLASH_TS))
  if [[ "$AGE" -lt 2 ]]; then
    FLASH_ACTIVE=1
    if [[ "$FLASH_TYPE" == "plug" ]]; then
      FLASH_ICON="󱐋"
    elif [[ "$FLASH_TYPE" == "unplug_full" ]]; then
      FLASH_ICON="󰚧" # Crossed-out plug icon
    else
      FLASH_ICON="󰚦"
    fi
  else
    rm -f "$FLASH_FILE"
  fi
fi

# Low battery flashing logic (Constant cycle alert when < 20%)
if [[ "$FLASH_ACTIVE" -eq 0 && "$STAT" == "Discharging" && "$CAP" -lt 20 ]]; then
  # Alternates visibility every 2 seconds based on system clock timestamp
  if [[ $(($(date +%s) % 2)) -eq 0 ]]; then
    FLASH_ACTIVE=1
    FLASH_ICON="󰚦"
  fi
fi

# --- Icon & State Determinations ---
if [[ "$STAT" == "Full" ]]; then
  ICON="󰄬"
  STATE="full"
elif [[ "$STAT" == "Charging" ]]; then
  ICON="󱐋"
  STATE="charging"
elif [[ "$STAT" == "Not charging" || "$CAP" -eq 100 ]]; then
  ICON="󰐧"
  STATE="plugged"
elif [[ "$CAP" -lt 20 ]]; then
  ICON="󰁃"
  STATE="critical"
else
  ICON="󰁅"
  STATE="discharging"
fi

# --- Content Engine (Bar vs Percentage Toggle) ---
SYMBOL="<span font_weight='black' size='small' rise='-600' alpha='65%'>%</span>"
BAR_SPAN="<span font_family='Monaspace Krypton' font_features='tnum'>$BAR</span>"

if [[ "$FLASH_ACTIVE" == "1" ]]; then
  DISPLAY_TEXT=" $FLASH_ICON "
elif [[ -f "$TOGGLE_FILE" ]]; then
  DISPLAY_TEXT="$ICON $CAP$SYMBOL" # Swapped style on click
else
  DISPLAY_TEXT="$ICON $BAR_SPAN" # Clean default style
fi

# --- Build JSON with python to handle all escaping safely ---
[[ "$STAT" == "Charging" ]] && TIME_LABEL="Time to full" || TIME_LABEL="Time remaining"

python3 -c "
import json, sys
display = sys.argv[1]
state   = sys.argv[2]
stat    = sys.argv[3]
cap     = sys.argv[4]
volt    = sys.argv[5]
watt    = sys.argv[6]
time_label = sys.argv[7]
time_str   = sys.argv[8]

# Create list items and join them with escaped newline characters
tooltip_lines = [
    f'<b>Status:</b> {stat}',
    f'<b>Charge:</b> {cap}%',
    f'<b>Voltage:</b> {volt}',
    f'<b>Power:</b> {watt}',
    f'<b>{time_label}:</b> {time_str}'
]
tooltip_text = '\\n'.join(tooltip_lines)

print(json.dumps({'text': display, 'class': state, 'tooltip': tooltip_text}))
" "$DISPLAY_TEXT" "$STATE" "$STAT" "$CAP" "$VOLT" "$WATT" "$TIME_LABEL" "$TIME_STR"
