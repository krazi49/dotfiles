#!/bin/bash
# Left click — workspace list with "New" option
THEME="$HOME/.config/rofi/config.rasi"

ws_list=$(hyprctl workspaces -j | jq -r '
  sort_by(.id) | .[] |
  "\(.id)  \(.windows)"' | while IFS='  ' read -r id wins; do
    echo "  $id  ·  $wins window"
  done
)

menu="󰄸  New workspace
$ws_list"

choice=$(echo -e "$menu" | rofi -dmenu -theme "$THEME" -i -p "  Workspaces")
[[ -z "$choice" ]] && exit 0

# New workspace → same search bar as right click
if echo "$choice" | grep -q "New workspace"; then
  num=$(rofi -dmenu -theme "$HOME/.config/rofi/config.rasi" -p "  Go to workspace")
  [[ -z "$num" ]] && exit 0
  hyprctl dispatch 'hl.dsp.focus({workspace="'"$num"'"})'
  exit 0
fi

ws_id=$(echo "$choice" | awk '{print $2}')
hyprctl dispatch 'hl.dsp.focus({workspace="'"$ws_id"'"})'
