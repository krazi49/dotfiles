#!/bin/bash
# caffeine-waybar.sh
# Reads the caffeine state file and outputs waybar JSON

STATEFILE="/tmp/caffeine-state"
PIDFILE="/tmp/caffeine-forever.pid"

if [[ ! -f "$STATEFILE" ]]; then
  # Inactive
  echo '{"text": " 󰅶 Off ", "class": "off", "tooltip": "Caffeine waiting"}'
  exit 0
fi

source "$STATEFILE"
# STATEFILE sets: MODE (timed|forever), END_EPOCH (for timed)

if [[ "$MODE" == "forever" ]]; then
  if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo '{"text": " 󰅶 Forever ", "class": "active", "tooltip": "Caffeine drank indefinitely\nClick to cancel"}'
  else
    rm -f "$STATEFILE"
    echo '{"text": " 󰅶 Off ", "class": "off", "tooltip": "Caffeine waiting"}'
  fi
  exit 0
fi

# Timed mode — calculate remaining
NOW=$(date +%s)
REMAINING=$((END_EPOCH - NOW))

if ((REMAINING <= 0)); then
  rm -f "$STATEFILE"
  echo '{"text": " 󰅶 Off ", "class": "off", "tooltip": "Caffeine wore off\nYour screen will sleep by itself now. Click to configure"}'
  exit 0
fi

HOURS=$((REMAINING / 3600))
MINS=$(((REMAINING % 3600) / 60))

if ((HOURS > 0)); then
  LABEL="${HOURS}h ${MINS}m left"
else
  LABEL="${MINS}m left"
fi

echo "{\"text\": \" 󰅶 ${LABEL} \", \"class\": \"active\", \"tooltip\": \"caffeine active: ${LABEL}\"}"
