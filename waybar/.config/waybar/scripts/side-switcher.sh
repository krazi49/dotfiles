#!/bin/bash

# Configuration paths
BASE_DIR="$HOME/.config/waybar"
TOPSHELF="$BASE_DIR/top-shelf"

options="Standard\nTop-Shelf"

# Get choice
choice=$(echo -e "$options" | wofi --dmenu --prompt "Omniwaybar" --cache-file /dev/null --normal-window)

# SAFETY CHECK: If choice is empty (user pressed ESC or quit bind), exit the script
if [ -z "$choice" ]; then
  exit 0
fi

# Only kill the bar IF we are actually about to start a new one
pkill waybar

case $choice in
"Standard")
  waybar -c "$BASE_DIR/config.jsonc" -s "$BASE_DIR/style.css" &
  ;;
"Top-Shelf")
  waybar -c "$TOPSHELF/config.jsonc" -s "$TOPSHELF/style.css" &
  ;;
esac

disown
