#!/bin/bash
# Read current mood and output JSON for waybar custom/mood module
FILE="$HOME/.config/waybar/current_mood"

if [ ! -f "$FILE" ]; then
  echo '{"text":"󰧨  none","class":"mood-none"}'
  exit 0
fi

MOOD=$(cat "$FILE" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g')
LABEL=$(cat "$FILE")

echo "{\"text\":\"󰧨  $LABEL\",\"class\":\"mood-$MOOD\"}"
