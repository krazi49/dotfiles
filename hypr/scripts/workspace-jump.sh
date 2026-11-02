#!/bin/bash
# Right click — clean search bar, no entries
JUMP_THEME="$HOME/.config/rofi/config.rasi"

num=$(rofi -dmenu -theme "$JUMP_THEME" -p "  Go to workspace")
[[ -z "$num" ]] && exit 0

hyprctl dispatch 'hl.dsp.focus({workspace="'"$num"'"})'
