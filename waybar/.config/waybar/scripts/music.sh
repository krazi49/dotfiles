#!/bin/bash

STATUS=$(playerctl status 2>/dev/null)
if [ -z "$STATUS" ] || [ "$STATUS" = "No players found" ]; then
  echo '{"text": "", "tooltip": "", "class": "stopped"}'
  exit 0
fi

TITLE=$(playerctl metadata title 2>/dev/null)
ARTIST=$(playerctl metadata artist 2>/dev/null)
ALBUM=$(playerctl metadata album 2>/dev/null)
POSITION=$(playerctl position 2>/dev/null)
LENGTH=$(playerctl metadata mpris:length 2>/dev/null)

LENGTH_S=$(echo "$LENGTH / 1000000" | bc -l 2>/dev/null)

BAR=""
if [ -n "$POSITION" ] && [ -n "$LENGTH_S" ] && [ "$(echo "$LENGTH_S > 0" | bc -l)" = "1" ]; then
  FRACTION=$(echo "$POSITION / $LENGTH_S" | bc -l)
  BAR_WIDTH=30
  FILLED=$(echo "($FRACTION * $BAR_WIDTH) / 1" | bc)
  EMPTY=$(($BAR_WIDTH - FILLED))
  for i in $(seq 1 $FILLED); do BAR="${BAR}━"; done
  for i in $(seq 1 $EMPTY); do BAR="${BAR}╌"; done
fi

fmt_time() {
  local s=$(printf "%.0f" "$1")
  printf "%d:%02d" $((s / 60)) $((s % 60))
}

POS_FMT=$(fmt_time "$POSITION")
LEN_FMT=$(fmt_time "$LENGTH_S")

# Scrolling logic
DISPLAY_LEN=12
SPEED=1 # characters per second
TITLE_LEN=${#TITLE}
if [ "$TITLE_LEN" -le "$DISPLAY_LEN" ]; then
  SCROLL_TITLE="$TITLE"
else
  PADDED="${TITLE}   "
  PADDED_LEN=${#PADDED}
  OFFSET=$((($(date +%s) * $SPEED) % PADDED_LEN))
  SCROLL_TITLE="${PADDED:$OFFSET:$DISPLAY_LEN}"
  if [ "${#SCROLL_TITLE}" -lt "$DISPLAY_LEN" ]; then
    SCROLL_TITLE="${SCROLL_TITLE}${PADDED:0:$(($DISPLAY_LEN - ${#SCROLL_TITLE}))}"
  fi
fi

pango_escape() { printf '%s' "$1" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g'; }
json_escape() { printf '%s' "$1" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read())[1:-1])"; }

TITLE_J=$(json_escape "$(pango_escape "$TITLE")")
ARTIST_J=$(json_escape "$(pango_escape "$ARTIST")")
ALBUM_J=$(json_escape "$(pango_escape "$ALBUM")")
TEXT_J=$(json_escape "<span font_family=\"Monaspace Krypton\">$(pango_escape "$SCROLL_TITLE")</span>")

TOOLTIP="<b>${TITLE_J}</b>\\n${ARTIST_J}\\n${ALBUM_J}\\n\\n<span font_family=\\\"Monaspace Krypton\\\" font_features=\\\"tnum\\\">${POS_FMT} ${BAR} ${LEN_FMT}</span>"

echo "{\"text\": \"${TEXT_J}\", \"tooltip\": \"${TOOLTIP}\", \"class\": \"${STATUS}\"}"
