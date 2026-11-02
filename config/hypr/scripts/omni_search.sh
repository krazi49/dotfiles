#!/bin/bash

# --- 1. Data Generation ---
if command -v fd >/dev/null 2>&1; then
  FD_CMD="fd . $HOME --maxdepth 3 --type f"
else
  FD_CMD="find $HOME -maxdepth 3 -type f -not -path '*/.*'"
fi

# Windows
windows=$(hyprctl clients -j | jq -r '.[] | "\(.title)|\(.address)"' | while read -r line; do
  title=$(echo "$line" | cut -d'|' -f1)
  addr=$(echo "$line" | cut -d'|' -f2)
  echo -e "${title}\0icon\x1fwindow\x1finfo\x1fwin|${addr}"
done)

# Tabs
tabs=$(dbus-send --print-reply --dest=org.kde.plasma.browser_integration /Tabs org.kde.plasma.browser_integration.Tabs.GetTabs 2>/dev/null |
  grep "string" | cut -d '"' -f 2 | while read -r title; do
  echo -e "${title}\0icon\x1fbrowser\x1finfo\x1ftab|${title}"
done)

# Files
files=$($FD_CMD | head -n 100 | while read -r path; do
  echo -e "$(basename "$path")\0icon\x1fdocument\x1finfo\x1ffile|${path}"
done)

# Apps
apps=$(compgen -c | sort -u | while read -r app; do
  echo -e "${app}\0icon\x1fsystem-run\x1finfo\x1frun|${app}"
done)

# --- 2. The Launcher ---
# We use -mesg for the calculator result if you want to add that later
selected=$(echo -e "$tabs\n$windows\n$apps\n$files" | rofi -dmenu -i -p "󰭎 Search" -theme-str '@import "~/.cache/matugen/colors.css"')

# --- 3. The Action ---
[[ -z "$selected" ]] && exit

# Rofi returns the "info" string if we set it up right, but here we'll parse the selection
# We use the 'info' field we passed (\x1finfo\x1f...)
# Since rofi-wayland supports -dump-extra-data or custom scripts, we'll keep it simple:
type=$(echo "$selected" | xargs -0 rofi -dump-extra-data -selected-row 2>/dev/null | awk -F'|' '{print $1}') # This is getting technical, let's stick to simple parsing:

# Fallback parsing if extra-data is tricky:
metadata=$(echo -e "$tabs\n$windows\n$apps\n$files" | grep -F "$selected" | awk -F'\x1f' '{print $4}')
action=$(echo "$metadata" | cut -d'|' -f1)
target=$(echo "$metadata" | cut -d'|' -f2)

case "$action" in
win) hyprctl dispatch focuswindow address:"$target" ;;
tab) dbus-send --dest=org.kde.plasma.browser_integration /Tabs org.kde.plasma.browser_integration.Tabs.ActivateTab string:"$target" ;;
file) xdg-open "$target" ;;
run) hyprctl dispatch exec "$target" ;;
esac
