#!/bin/bash

# Define paths for clarity
STATE_FILE="/tmp/hypr_transparency_mode"

if [ ! -f "$STATE_FILE" ]; then
  # Opaque Mode
  hyprctl keyword decoration:active_opacity 1.0
  hyprctl keyword decoration:inactive_opacity 1.0
  touch "$STATE_FILE"
else
  # Transparent Mode
  hyprctl keyword decoration:active_opacity 0.95
  hyprctl keyword decoration:inactive_opacity 0.80
  rm "$STATE_FILE"
fi
