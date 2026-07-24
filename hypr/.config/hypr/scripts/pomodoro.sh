#!/bin/bash
# Pomodoro timer controller for waybar adaptive module
# Writes state to /tmp/pomodoro_active and start time to /tmp/pomodoro_start

POMODORO_DIR="/tmp"
ACTIVE_FILE="$POMODORO_DIR/pomodoro_active"
START_FILE="$POMODORO_DIR/pomodoro_start"
DURATION=$((25 * 60)) # 25 minutes in seconds

case "$1" in
    start)
        if [ -f "$ACTIVE_FILE" ]; then
            echo "Pomodoro already active"
            exit 1
        fi
        echo "focus" > "$ACTIVE_FILE"
        date +%s > "$START_FILE"
        notify-send "Pomodoro started" "Focus for 25 minutes" -i timer
        ;;
    stop)
        if [ ! -f "$ACTIVE_FILE" ]; then
            echo "No active pomodoro to stop"
            exit 1
        fi
        rm -f "$ACTIVE_FILE" "$START_FILE"
        notify-send "Pomodoro stopped" "Timer cleared" -i timer
        ;;
    status)
        if [ ! -f "$ACTIVE_FILE" ]; then
            echo "No active pomodoro"
            exit 0
        fi
        start_time=$(cat "$START_FILE")
        now=$(date +%s)
        elapsed=$((now - start_time))
        remaining=$((DURATION - elapsed))
        if [ $remaining -lt 0 ]; then
            # Timer expired, clean up
            rm -f "$ACTIVE_FILE" "$START_FILE"
            echo "Pomodoro finished"
            notify-send "Pomodoro finished" "Time to take a break!" -i timer
            exit 0
        fi
        mins=$((remaining / 60))
        secs=$((remaining % 60))
        state=$(cat "$ACTIVE_FILE")
        echo "Pomodoro ($state): ${mins}:$(printf "%02d" $secs) remaining"
        ;;
    reset)
        rm -f "$ACTIVE_FILE" "$START_FILE"
        echo "Pomodoro timer reset"
        ;;
    *)
        echo "Usage: $0 {start|stop|status|reset}"
        exit 1
        ;;
esac