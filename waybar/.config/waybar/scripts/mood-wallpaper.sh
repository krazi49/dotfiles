#!/bin/bash
# Simple mood wallpaper script - prevents service failures
# Logs mood changes for debugging
MOOD="$1"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
echo "[$TIMESTAMP] Mood changed to: $MOOD" >> /tmp/mood-wallpaper.log
# Actual wallpaper setting would go here
# For now, just log to prevent service failure
exit 0