#!/bin/bash
# Read current mood and output a greeting based on it
FILE="$HOME/.config/waybar/current_mood"

if [ ! -f "$FILE" ]; then
  echo "hey"
  exit 0
fi

MOOD=$(cat "$FILE" | tr '[:upper:]' '[:lower:]')

case "$MOOD" in
  *sleepy*)   echo "tiiiired... just hang in there" ;;
  *irritable*) echo "hey" ;;
  *frenzied*) echo "keep going" ;;
  *"soft spot"*) echo "awww" ;;
  *hyped*)    echo "let's gooo" ;;
  *)          echo "hey" ;;
esac
