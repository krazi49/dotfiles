#!/bin/bash
# Workspace overview — left click
# Companion to workspace-hook.sh (see setup note at the bottom) which
# populates thumbnails and recency history. Works fine without it too —
# you just lose those two features and fall back to id-sorted, no icons.

THEME="$HOME/.config/rofi/config.rasi"
CACHE_DIR="$HOME/.cache/hypr-ws-overview"
THUMB_DIR="$CACHE_DIR/thumbs"
HISTORY_FILE="$CACHE_DIR/history" # written by workspace-hook.sh, oldest first
mkdir -p "$THUMB_DIR"

# WS_SORT=recency ./workspace-overview.sh  -> order by last-used instead of id
SORT_MODE="${WS_SORT:-id}"

active_ws=$(hyprctl activeworkspace -j | jq -r '.id')

# ── Gather everything in one pass each (avoid re-invoking hyprctl per row) ──
workspaces_json=$(hyprctl workspaces -j)
clients_json=$(hyprctl clients -j)
binds_json=$(hyprctl binds -j 2>/dev/null || echo '[]')

# id -> "Class1, Class2, +N more" (truncated window preview)
declare -A win_preview
while IFS=$'\t' read -r ws_id preview; do
  [[ -n "$ws_id" ]] && win_preview["$ws_id"]="$preview"
done < <(echo "$clients_json" | jq -r '
  group_by(.workspace.id) | .[] |
  "\(.[0].workspace.id)\t\( [ .[].class ] |
      if length > 3 then (.[0:3] | join(", ")) + "  +\(length-3) more"
      else join(", ") end )"
')

# id -> keybind hint, e.g. "SUPER+3"
declare -A keybind_hint
while IFS=$'\t' read -r arg hint; do
  [[ -n "$arg" ]] && keybind_hint["$arg"]="$hint"
done < <(echo "$binds_json" | jq -r '
  .[] | select(.dispatcher == "workspace") |
  "\(.arg)\t\(.modmask|tostring)+\(.key)"
' | sed -E \
  -e 's/^64\+/SUPER+/' -e 's/^8\+/ALT+/' -e 's/^4\+/CTRL+/' -e 's/^1\+/SHIFT+/' \
  -e 's/^0\+//')

# ── Build rows, grouped by monitor ──────────────────────────────────────────
menu="󰄸  New workspace"

monitors=$(echo "$workspaces_json" | jq -r '[.[].monitor] | unique | .[]')

while IFS= read -r mon; do
  [[ -z "$mon" ]] && continue
  menu+=$'\n'"────  $mon  ────"

  ids_on_mon=$(echo "$workspaces_json" | jq -r --arg mon "$mon" '
    [.[] | select(.monitor == $mon and .id >= 0)] |
    sort_by(.id) | .[].id')

  ordered_ids="$ids_on_mon"
  if [[ "$SORT_MODE" == "recency" && -f "$HISTORY_FILE" ]]; then
    # most-recently-visited (from history, deduped, newest first) that are
    # actually on this monitor, then anything left over in id order
    recent=$(tac "$HISTORY_FILE" | awk '!seen[$0]++' | while read -r id; do
      echo "$ids_on_mon" | grep -qx "$id" && echo "$id"
    done)
    leftover=$(comm -23 <(echo "$ids_on_mon" | sort -n) <(echo "$recent" | sort -n))
    ordered_ids=$(printf '%s\n%s\n' "$recent" "$leftover" | awk 'NF')
  fi

  while IFS= read -r id; do
    [[ -z "$id" ]] && continue

    wins=$(echo "$workspaces_json" | jq -r --arg id "$id" '.[] | select((.id|tostring) == $id) | .windows')
    preview="${win_preview[$id]:-empty}"
    hint="${keybind_hint[$id]:+   ${keybind_hint[$id]}}"

    plural="window"
    [[ "$wins" != "1" ]] && plural="windows"

    marker=""
    [[ "$id" == "$active_ws" ]] && marker="   (current)"

    if [[ "$wins" == "0" ]]; then
      row="  $id  ·  empty$marker"
    else
      row="  $id  ·  $wins $plural  —  $preview$marker"
    fi
    row+="$hint"

    thumb="$THUMB_DIR/$id.png"
    if [[ -f "$thumb" ]]; then
      row+=$'\0icon\x1f'"$thumb"
    fi

    menu+=$'\n'"$row"
  done <<<"$ordered_ids"
done <<<"$monitors"

choice=$(echo -e "$menu" | rofi -dmenu -theme "$THEME" -i -show-icons -p "  Workspaces")
[[ -z "$choice" ]] && exit 0

# ── Handle selection ─────────────────────────────────────────────────────
case "$choice" in
*"New workspace"*)
  num=$(rofi -dmenu -theme "$THEME" -p "  Go to workspace")
  [[ -z "$num" ]] && exit 0
  if [[ ! "$num" =~ ^[0-9]+$ ]]; then
    notify-send "Workspace" "\"$num\" isn't a valid workspace number" 2>/dev/null
    exit 1
  fi
  hyprctl dispatch workspace "$num"
  exit 0
  ;;
"────"*)
  # header row selected — no-op, just re-open the menu
  exec "$0"
  ;;
esac

ws_id=$(echo "$choice" | awk '{print $1}')
if [[ "$ws_id" =~ ^[0-9]+$ ]]; then
  hyprctl dispatch workspace "$ws_id"
fi

# ── One-time setup reminder ─────────────────────────────────────────────────
# For thumbnails + recency ordering, wire workspace-hook.sh into hyprland.conf.
# Hyprland doesn't have a built-in "on workspace change" exec hook, so the
# reliable way is to wrap your existing workspace keybinds to call the hook
# right after switching, e.g. replace:
#   bind = SUPER, 1, workspace, 1
# with:
#   bind = SUPER, 1, exec, hyprctl dispatch workspace 1 && ~/.config/hypr/scripts/workspace-hook.sh
#
# Do this for each numbered workspace bind you have. The hook snapshots
# whichever workspace you just left (into $HISTORY_FILE and a grim capture)
# right after hyprctl finishes the switch.
