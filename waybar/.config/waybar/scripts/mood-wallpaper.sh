#!/usr/bin/env bash
# Mood wallpaper hook — writes hyprpaper config and restarts it.
# Drop images in ~/.config/waybar/wallpapers/mood/<mood-name>.{png,jpg,jpeg,webp}
# Falls back to default wallpaper when no mood image exists.

MOOD_FILE="$HOME/.config/waybar/current_mood"
WALL_DIR="$HOME/.config/waybar/wallpapers/mood"
STATE_FILE="/tmp/waybar_current_wallpaper"
CONFIG_FILE="$HOME/.config/hypr/hyprpaper.conf"

get_monitor() {
    hyprctl monitors -j 2>/dev/null | python3 -c "
import json, sys
try:
    for m in json.load(sys.stdin):
        print(m['name'])
        break
except: pass
"
}

set_wallpaper() {
    local wall="$1"
    local monitor="$2"

    cat > "$CONFIG_FILE" << EOF
preload = $wall
wallpaper = $monitor,$wall
EOF

    pkill -9 hyprpaper 2>/dev/null
    sleep 0.2
    hyprpaper -c "$CONFIG_FILE" &
}

monitor=$(get_monitor)
[[ -z "$monitor" ]] && exit 1

# Init state file if needed
if ! [[ -f "$STATE_FILE" ]] || ! [[ -s "$STATE_FILE" ]]; then
    echo "/home/em/.config/waybar/wallpapers/default.png" > "$STATE_FILE"
fi

# Try mood wallpaper (lowercase the mood name for file matching)
mood_wall=""
if [[ -f "$MOOD_FILE" ]]; then
    mood=$(cat "$MOOD_FILE")
    # Trim whitespace and lowercase
    mood=$(echo "$mood" | tr 'A-Z' 'a-z' | xargs)
    for ext in png jpg jpeg webp; do
        wall="$WALL_DIR/$mood.$ext"
        if [[ -f "$wall" ]]; then
            mood_wall="$wall"
            break
        fi
    done
fi

if [[ -n "$mood_wall" ]]; then
    set_wallpaper "$mood_wall" "$monitor"
    echo "$mood_wall" > "$STATE_FILE"
else
    saved=$(cat "$STATE_FILE")
    if [[ -f "$saved" ]]; then
        set_wallpaper "$saved" "$monitor"
    fi
fi
