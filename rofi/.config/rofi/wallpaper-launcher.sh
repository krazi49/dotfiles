#!/bin/bash

# Folder where your wallpapers live
WALL_DIR="$HOME/wallpapers"

# 1. Generate the list for Rofi
# This finds all images in subfolders and tells Rofi to use them as icons
list_walls() {
  find "$WALL_DIR" -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" -o -name "*.webp" \) | while read -r line; do
    # We pass the full path as the icon and the filename as the label
    echo -en "$(basename "$line")\0icon\x1f$line\n"
  done
}

# 2. Launch Rofi and capture the filename
selected_name=$(list_walls | rofi -dmenu -i -theme ~/.config/rofi/cards.rasi -p "Wallpapers")

# 3. If you picked something, find the full path and set it with awww
if [ -n "$selected_name" ]; then
  full_path=$(find "$WALL_DIR" -name "$selected_name" | head -n 1)

  # Using the 'awww' command (same syntax as swww)
  awww img "$full_path" --transition-type grow --transition-duration 2
fi
