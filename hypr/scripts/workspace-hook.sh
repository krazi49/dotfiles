#!/bin/bash
# workspace-hook.sh — run once as a background daemon (see autostart note
# at the bottom). Listens to Hyprland's event socket instead of polling,
# so it costs ~nothing at idle.
#
# On every workspace switch it:
#   1. appends the new workspace id to the recency history file
#   2. after a short settle delay, grabs a downscaled grim screenshot of
#      whichever monitor that workspace ended up on, cached as its thumbnail
#
# Requires: grim, jq, and (optional but recommended) imagemagick for
# downscaling — falls back to full-res screenshots if `magick`/`convert`
# aren't found.

CACHE_DIR="$HOME/.cache/hypr-ws-overview"
THUMB_DIR="$CACHE_DIR/thumbs"
HISTORY_FILE="$CACHE_DIR/history"
SETTLE_DELAY="0.35" # seconds to wait after switch before screenshotting
THUMB_WIDTH="240"

mkdir -p "$THUMB_DIR"
touch "$HISTORY_FILE"

SOCK="$XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock"
if [[ ! -S "$SOCK" ]]; then
  echo "workspace-hook: socket2 not found at $SOCK — is Hyprland running?" >&2
  exit 1
fi

resize_cmd() {
  if command -v magick &>/dev/null; then
    echo "magick"
  elif command -v convert &>/dev/null; then
    echo "convert"
  else
    echo ""
  fi
}
RESIZER=$(resize_cmd)

capture_workspace() {
  local ws_id="$1"
  [[ "$ws_id" -lt 0 ]] && return # skip special/scratchpad workspaces

  # Which monitor is this workspace actually showing on right now?
  local mon
  mon=$(hyprctl monitors -j | jq -r --arg id "$ws_id" '
    .[] | select((.activeWorkspace.id|tostring) == $id) | .name' | head -n1)
  [[ -z "$mon" ]] && return # workspace isn't the visible one on any monitor

  local out="$THUMB_DIR/$ws_id.png"
  local tmp="$THUMB_DIR/.$ws_id.tmp.png"

  if grim -o "$mon" "$tmp" 2>/dev/null; then
    if [[ -n "$RESIZER" ]]; then
      "$RESIZER" "$tmp" -resize "${THUMB_WIDTH}x" "$out" 2>/dev/null && rm -f "$tmp"
    else
      mv "$tmp" "$out"
    fi
  fi
}

# Trim history so it doesn't grow forever (keep last 200 entries)
trim_history() {
  tail -n 200 "$HISTORY_FILE" >"$HISTORY_FILE.tmp" && mv "$HISTORY_FILE.tmp" "$HISTORY_FILE"
}

# ── Main event loop ─────────────────────────────────────────────────────────
socat -U - UNIX-CONNECT:"$SOCK" 2>/dev/null | while IFS= read -r line; do
  case "$line" in
  workspace\>\>*)
    ws_id="${line#workspace>>}"
    [[ "$ws_id" =~ ^-?[0-9]+$ ]] || continue

    echo "$ws_id" >>"$HISTORY_FILE"
    trim_history

    # settle delay in background so we don't block the event loop
    (
      sleep "$SETTLE_DELAY"
      capture_workspace "$ws_id"
    ) &
    ;;
  esac
done

# ── Autostart (add to hyprland.conf) ────────────────────────────────────────
#   exec-once = ~/.config/hypr/scripts/workspace-hook.sh
#
# If `socat` isn't installed: `sudo pacman -S socat` (arch) or your distro's
# equivalent — it's the only non-standard dependency here.
