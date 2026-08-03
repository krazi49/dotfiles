#!/bin/bash
# Clock module: time & date on bar, week + uptime in tooltip

uptime_human() {
  local s=$1
  local d=$((s / 86400)) h=$(((s % 86400) / 3600)) m=$(((s % 3600) / 60))
  local out=""
  ((d > 0)) && out+="${d}d "
  ((h > 0)) && out+="${h}h "
  out+="${m}m"
  echo "$out"
}

emit() {
  TIME=$(date "+%H:%M")
  DATE=$(date "+%a, %b %d")
  WEEK=$(date "+%V")
  UPTIME=$(uptime_human "$(awk '{printf "%d", $1}' /proc/uptime)")

  TOOLTIP="Week ${WEEK}  •  Up ${UPTIME}"

  printf '{"text":"󰥔  %s 🟆 %s","tooltip":"%s"}\n' "$TIME" "$DATE" "$TOOLTIP"
}

emit
while true; do
  sleep 1
  emit
done
