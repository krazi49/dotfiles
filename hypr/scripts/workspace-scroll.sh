#!/bin/bash
# Throttled workspace scroll — prevents trackpad scroll spam
LOCKFILE="/tmp/workspace-scroll.lock"
COOLDOWN=600  # ms between scrolls

NOW=$(date +%s%N)
if [[ -f "$LOCKFILE" ]]; then
  LAST=$(cat "$LOCKFILE")
  DIFF=$(( (NOW - LAST) / 1000000 ))
  if [[ $DIFF -lt $COOLDOWN ]]; then
    exit 0
  fi
fi
echo "$NOW" > "$LOCKFILE"

hyprctl dispatch "hl.dsp.focus({workspace='$1'})"
