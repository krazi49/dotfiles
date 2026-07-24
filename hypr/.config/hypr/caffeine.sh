#!/bin/bash

op1="󰅶  Caffeine for 30m"
op2="󰅶  Caffeine for 1h"
op3="󰅶  Caffeine for 2h"
op4="󰅶  Caffeine stops when I say so"

options="$op1\n$op2\n$op3\n$op4"

choice=$(echo -e "$options" | wofi -d \
  --prompt "Caffeine" \
  --conf ~/.config/wofi/config \
  --style ~/.config/wofi/style.css \
  --normal-window)

STATEFILE="/tmp/caffeine-state"
PIDFILE="/tmp/caffeine-forever.pid"

# ── Caffeine helpers ──────────────────────────────────────
caffeine_for() {
  local seconds=$1
  local label=$2

  # Cancel any existing indefinite caffeine
  if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    kill "$(cat "$PIDFILE")"
    rm -f "$PIDFILE"
  fi

  cookie=$(busctl --user call \
    org.freedesktop.ScreenSaver \
    /org/freedesktop/ScreenSaver \
    org.freedesktop.ScreenSaver \
    Inhibit ss "caffeine" "$label" 2>/dev/null | awk '{print $2}')

  END_EPOCH=$(($(date +%s) + seconds))
  echo "MODE=timed" >"$STATEFILE"
  echo "END_EPOCH=$END_EPOCH" >>"$STATEFILE"

  # Signal waybar to refresh
  pkill -RTMIN+8 waybar

  notify-send "󰅶 Caffeine" "Screen will stay awake for $label" --urgency=low

  sleep "$seconds"

  busctl --user call \
    org.freedesktop.ScreenSaver \
    /org/freedesktop/ScreenSaver \
    org.freedesktop.ScreenSaver \
    UnInhibit u "$cookie" 2>/dev/null

  rm -f "$STATEFILE"
  pkill -RTMIN+8 waybar
  notify-send "󰅶 Caffeine" "Idle inhibit released" --urgency=low
}

caffeine_forever() {
  # Toggle off if already running
  if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    kill "$(cat "$PIDFILE")"
    rm -f "$PIDFILE" "$STATEFILE"
    pkill -RTMIN+8 waybar
    notify-send "󰅶 Caffeine" "Idle inhibit released" --urgency=low
    exit 0
  fi

  (
    cookie=$(busctl --user call \
      org.freedesktop.ScreenSaver \
      /org/freedesktop/ScreenSaver \
      org.freedesktop.ScreenSaver \
      Inhibit ss "caffeine" "indefinite" 2>/dev/null | awk '{print $2}')

    echo $$ >"$PIDFILE"
    echo "MODE=forever" >"$STATEFILE"
    pkill -RTMIN+8 waybar

    notify-send "󰅶 Caffeine" "Screen will stay awake indefinitely\nRun again to cancel" --urgency=low

    sleep infinity

    busctl --user call \
      org.freedesktop.ScreenSaver \
      /org/freedesktop/ScreenSaver \
      org.freedesktop.ScreenSaver \
      UnInhibit u "$cookie" 2>/dev/null

    rm -f "$PIDFILE" "$STATEFILE"
    pkill -RTMIN+8 waybar
  ) &
}

# ── Dispatch ──────────────────────────────────────────────
case "$choice" in
*"Caffeine for 30m"*) caffeine_for 1800 "30 minutes" & ;;
*"Caffeine for 1h"*) caffeine_for 3600 "1 hour" & ;;
*"Caffeine for 2h"*) caffeine_for 7200 "2 hours" & ;;
*"Caffeine stops when I say so"*) caffeine_forever ;;
esac
