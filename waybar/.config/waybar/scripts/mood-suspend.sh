#!/usr/bin/env bash
# Mood-gated suspend — delays with attitude when mood is feral + battery low.
# Bypass with: systemctl suspend (direct)

MOOD_FILE="$HOME/.config/waybar/current_mood"
BAT_DIR="/sys/class/power_supply"

get_mood() {
    [[ -f "$MOOD_FILE" ]] && cat "$MOOD_FILE" | tr 'A-Z' 'a-z' | xargs || echo ""
}

get_battery_cap() {
    for d in "$BAT_DIR"/BAT*; do
        [[ -d "$d" ]] || continue
        cap=$(cat "$d/capacity" 2>/dev/null) && echo "$cap" && return
    done
    echo "100"
}

get_battery_stat() {
    for d in "$BAT_DIR"/BAT*; do
        [[ -d "$d" ]] || continue
        stat=$(cat "$d/status" 2>/dev/null) && echo "$stat" && return
    done
    echo "Unknown"
}

MOOD=$(get_mood)
CAP=$(get_battery_cap)
STAT=$(get_battery_stat)

if [[ "$MOOD" == "feral" ]] && [[ "$CAP" -le 10 ]] && [[ "$STAT" == "Discharging" ]]; then
    MESSAGES=(
        "nice try. plug it in."
        "laptop says no. literally."
        "we're not done here."
        "you wanna lose all that work? really?"
        "i'm not mad. just disappointed. plug it in."
        "your battery is begging you."
    )
    IDX=$((CAP % ${#MESSAGES[@]}))
    MSG="${MESSAGES[$IDX]}"

    notify-send -u critical -t 9000 "🦞 SUSPEND BLOCKED" "$MSG"

    # Wait 10 seconds pretending to block
    for i in $(seq 10 -1 1); do
        sleep 1
        # Check if battery's plugged in now (user learned their lesson)
        NEWSTAT=$(get_battery_stat)
        if [[ "$NEWSTAT" == "Charging" ]]; then
            notify-send -u normal "good choice. carry on."
            systemctl suspend
            exit 0
        fi
    done

    notify-send -u low "fine, go ahead. see if i care."
fi

systemctl suspend
