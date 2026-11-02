#!/bin/bash

# Check if any player is currently "Playing"
if playerctl -a status 2>/dev/null | grep -q "Playing"; then
  IS_PLAYING=1
else
  IS_PLAYING=0
fi

# 2. Check Hardware (Force these to be numbers)
# Counts active recording streams
MIC=$(pacmd list-source-outputs 2>/dev/null | grep -c "state: RUNNING")
# Counts processes using video devices
CAM=$(fuser /dev/video* 2>/dev/null | wc -w)

# 3. Logic Gate using double-parentheses (integer safe)
if ((MIC > 0 || CAM > 0)); then
  LABEL=""
  ((MIC > 0)) && LABEL+="󰍬 "
  ((CAM > 0)) && LABEL+="󰄀"

  if ((IS_PLAYING == 1)); then
    # The Dot (Android Style)
    echo "{\"text\": \"\", \"class\": \"dot\", \"tooltip\": \"Active: $LABEL\"}"
  else
    # The Full Pill
    echo "{\"text\": \"$LABEL  Active\", \"class\": \"full\"}"
  fi
else
  # Hide if nothing is happening
  echo "{\"text\": \"\", \"class\": \"none\"}"
fi
