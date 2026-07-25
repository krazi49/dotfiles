#!/bin/bash

# ── Options ───────────────────────────────────────────────
op1="󱓇    Kill session"
op2="󰌾    Lockdown"
op3="󰐥    Power off"
op4="󰑓    Restart"
op5="⏾    Sleep"
op6="󰍃    Log out"

options="$op1\n$op2\n$op3\n$op4\n$op5\n$op6"

paplay ~/.sounds/omniscript.wav &

choice=$(echo -e "$options" | rofi -dmenu \
  -p "System options" \
  -theme "$HOME/.config/rofi/config.rasi")

# ── Dispatch ──────────────────────────────────────────────
case "$choice" in
*"Kill session"*)
  paplay ~/.sounds/logout.wav
  sleep 0.6
  hyprctl dispatch exit
  ;;
*"Lockdown"*) hyprlock ;;
*"Power off"*) systemctl poweroff ;;
*"Restart"*) systemctl reboot ;;
*"Sleep"*) systemctl suspend ;; # Updated to 'suspend' as 'systemctl sleep' is typically invalid syntax
*"Log out"*)
  paplay ~/.sounds/logout.wav
  sleep 0.6
  loginctl terminate-user "$USER"
  ;;
esac
