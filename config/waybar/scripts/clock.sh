#!/bin/bash
# Clock module: time (with faint seconds) + compact date on bar
# Tooltip: full date, ISO week, uptime, boot time

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
  SEC=$(date "+%S")
  DATE=$(date "+%a %d" | tr '[:lower:]' '[:upper:]')
  WEEK=$(date "+%V")
  UPTIME=$(uptime_human "$(awk '{printf "%d", $1}' /proc/uptime)")
  BOOT=$(uptime -s | cut -d' ' -f2 | cut -d: -f1,2)

  TOOLTIP="<span size='large' weight='bold'>$(date '+%A')</span>\n"
  TOOLTIP+="<span alpha='75%'>$(date '+%B %d, %Y')</span>\n"
  TOOLTIP+="\n"
  TOOLTIP+="<span alpha='25%'>─────────────</span>\n"
  TOOLTIP+="<span alpha='45%' size='small'>Week ${WEEK}   ·   Up ${UPTIME}   ·   Boot ${BOOT}</span>"

  printf '{"text":"󰥔  %s<span alpha='"'"'35%%'"'"'>:%s</span> · %s","tooltip":"%s"}\n' \
    "$TIME" "$SEC" "$DATE" "$TOOLTIP"
}

emit
while true; do
  sleep 1
  emit
done
