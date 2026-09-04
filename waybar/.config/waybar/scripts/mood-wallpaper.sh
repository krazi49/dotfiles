#!/bin/bash
# Switch wallpaper based on current mood
# Reads ~/.config/waybar/current_mood and applies matching wallpaper
MOOD_FILE="$HOME/.config/waybar/current_mood"
WALL_DIR="$HOME/.config/hypr/wallpapers/moods"

if [ ! -f "$MOOD_FILE" ]; then
  exit 0
fi

MOOD=$(cat "$MOOD_FILE" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g')

# Fall back to a default wallpaper if no mood-specific one exists
WALL="$WALL_DIR/$MOOD.jpg"
[ -f "$WALL" ] || WALL="$WALL_DIR/$MOOD.png"
[ -f "$WALL" ] || WALL="$WALL_DIR/default.jpg"
[ -f "$WALL" ] || WALL="$WALL_DIR/default.png"

if [ -f "$WALL" ]; then
  # Apply via hyprctl (Meridian/hyprland)
  hyprctl hyprpaper wallpaper "eDP-1,$WALL" 2>/dev/null || true
  # Fallback for swww/swaybg if hyprpaper isn't running
  if command -v swww >/dev/null 2>&1; then
    swww img "$WALL" --transition-type simple 2>/dev/null || true
  elif command -v swaybg >/dev/null 2>&1; then
    pkill swaybg 2>/dev/null; swaybg -i "$WALL" -m fill &>/dev/null &
  fi
fi
