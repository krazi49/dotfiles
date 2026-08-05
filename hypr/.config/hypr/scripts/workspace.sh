#!/bin/bash

# ── Workspace switcher — all 12 workspaces + special ──────
# Module text: compact summary (active WS, occupied count, window count)
# Tooltip: full workspace list with icons + apps

LOCKFILE="/tmp/waybar-workspace.lock"

if [ -f "$LOCKFILE" ]; then
  OLD_PID=$(cat "$LOCKFILE")
  if kill -0 "$OLD_PID" 2>/dev/null; then
    kill "$OLD_PID" 2>/dev/null
    sleep 0.3
  fi
fi

echo $$ >"$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT
trap '' PIPE

# ── Icon classifier ───────────────────────────────────────
classify_class() {
  local cls="${1,,}"
  case "$cls" in
  *zen*) echo "󰾔" ;;
  *firefox* | *librewolf* | *waterfox*) echo "󰈹" ;;
  *chromium* | *helium* | *chrome* | *brave* | *vivaldi* | *opera* | *edge*) echo "󰖟" ;;
  *kitty* | *alacritty* | *foot* | *wezterm* | *ghostty*) echo "" ;;
  *konsole* | *gnome-terminal* | *xterm*) echo "󰆍" ;;
  *code* | *vscodium* | *codium*) echo "󰨞" ;;
  *sublime*) echo "󰺿" ;;
  *neovide* | *nvim*) echo "" ;;
  *vim* | *emacs*) echo "󰏖" ;;
  *jetbrains* | *idea* | *pycharm* | *goland* | *clion* | *rider*) echo "󱃖" ;;
  *nautilus* | *files*) echo "󰉋" ;;
  *thunar* | *nemo*) echo "󰉖" ;;
  *dolphin*) echo "󰉗" ;;
  *ranger* | *yazi* | *lf*) echo "󰙅" ;;
  *spotify*) echo "󰓇" ;;
  *vlc*) echo "󰕼" ;;
  *mpv*) echo "󰎁" ;;
  *rhythmbox* | *lollypop* | *strawberry*) echo "󰝚" ;;
  *celluloid* | *totem*) echo "󰿎" ;;
  *discord* | *equibop* | *vesktop*) echo "󰙯" ;;
  *telegram*) echo "󰔁" ;;
  *slack*) echo "󰒱" ;;
  *thunderbird* | *geary*) echo "󰇮" ;;
  *signal*) echo "󰍕" ;;
  *element* | *nheko*) echo "󰭻" ;;
  *obsidian*) echo "󱓧" ;;
  *notion*) echo "󰟣" ;;
  *libreoffice* | *soffice*) echo "󱎺" ;;
  *evince* | *okular* | *zathura* | *mupdf*) echo "󰈦" ;;
  *gimp*) echo "󰃉" ;;
  *inkscape*) echo "󰺾" ;;
  *krita* | *blender*) echo "󰂫" ;;
  *figma*) echo "󰖟" ;;
  *steam*) echo "󰓓" ;;
  *lutris* | *heroic*) echo "󰺵" ;;
  *htop* | *btop* | *nvtop*) echo "󰓠" ;;
  *pavucontrol* | *easyeffects*) echo "󰕾" ;;
  *nm-connection* | *networkmanager*) echo "󰤨" ;;
  *blueman* | *bluetooth*) echo "󰂯" ;;
  *virt-manager* | *qemu* | *virtualbox*) echo "󰟀" ;;
  *docker*) echo "󰡨" ;;
  *bitwarden* | *keepassxc*) echo "󰌋" ;;
  *feh* | *imv* | *eog* | *shotwell* | *satty*) echo "󰋩" ;;
  *zoom* | *teams*) echo "󰤄" ;;
  *) echo "󱂬" ;;
  esac
}

get_ws_icon() {
  local ws_id=$1
  local focused_class all_classes

  focused_class=$(hyprctl activewindow -j 2>/dev/null | jq -r '.class // empty')
  all_classes=$(hyprctl clients -j 2>/dev/null | jq -r ".[] | select(.workspace.id == $ws_id) | .class")

  if [[ -z "$all_classes" ]]; then
    echo "󱂬"
    return
  fi

  if [[ -n "$focused_class" ]] && echo "$all_classes" | grep -qF "$focused_class"; then
    classify_class "$focused_class"
    return
  fi

  local priority=(
    zen firefox librewolf helium chromium brave vivaldi
    code vscodium neovide sublime jetbrains idea pycharm
    spotify vlc mpv
    discord equibop vesktop telegram slack
    obsidian notion
    steam lutris heroic
    gimp inkscape krita blender
    kitty alacritty foot wezterm ghostty
  )
  for p in "${priority[@]}"; do
    if echo "$all_classes" | grep -iq "$p"; then
      classify_class "$p"
      return
    fi
  done

  classify_class "$(echo "$all_classes" | head -1)"
}

get_ws_classes() {
  local ws_id=$1
  hyprctl clients -j 2>/dev/null | jq -r ".[] | select(.workspace.id == $ws_id) | .class" | sort -u | tr '\n' ', ' | sed 's/,$//'
}

# ── Output ────────────────────────────────────────────────
print_workspace() {
  local active_ws
  active_ws=$(hyprctl activeworkspace -j 2>/dev/null | jq -r '.id // empty')

  local occupied_ws
  occupied_ws=$(hyprctl clients -j 2>/dev/null | jq -r '.[].workspace.id' | sort -nu)

  # Detect special workspace
  local special_open=false
  local special_id
  special_id=$(hyprctl activeworkspace -j 2>/dev/null | jq -r '.id // empty')
  if [[ "$special_id" =~ ^- ]]; then
    special_open=true
    active_ws=$(hyprctl monitors -j 2>/dev/null | jq -r '.[0].activeWorkspace.id // empty')
  fi

  local ws_count
  ws_count=$(echo "$occupied_ws" | wc -w)

  local total_windows
  total_windows=$(hyprctl clients -j 2>/dev/null | jq 'length')

  # ── Module text: compact summary ────────────────────────
  local active_icon=""
  if [[ "$active_ws" =~ ^[0-9]+$ ]]; then
    active_icon=$(get_ws_icon "$active_ws")
  fi
  local TOTAL_WS=12
  local win_word="window"
  [ "$total_windows" -ne 1 ] && win_word="windows"
  local active_window_title=""
  if [[ "$active_ws" =~ ^[0-9]+$ ]]; then
    active_window_title=$(hyprctl activewindow -j 2>/dev/null | jq -r '.title // empty')
  fi
  local text="${active_icon} ${active_ws}/${TOTAL_WS} · ${active_window_title} · ${total_windows} ${win_word}"
  [ "$special_open" = true ] && text="${text} 󰆧"

  # ── Tooltip: occupied workspaces + active ──────────────
  local all_ws
  all_ws=$(echo "$occupied_ws" | tr ' ' '\n' | grep -v '^$' | sort -n)
  echo "$occupied_ws" | grep -q "^${active_ws}$" || all_ws="$all_ws\n$active_ws"

  local tooltip=""
  while IFS= read -r ws_idx; do
    [[ -z "$ws_idx" ]] && continue
    local icon="" classes="" marker=" "

    icon=$(get_ws_icon "$ws_idx")
    classes=$(get_ws_classes "$ws_idx")

    if [[ "$ws_idx" == "$active_ws" ]] && [ "$special_open" = false ]; then
      marker="●"
    fi

    tooltip="${tooltip}${marker}  ${ws_idx}  ${icon}"
    [ -n "$classes" ] && tooltip="${tooltip}  ${classes}"
    tooltip="${tooltip}\n"
  done <<<"$all_ws"

  [ "$special_open" = true ] && tooltip="${tooltip}●  S 󰆧  special"

  printf '{"text": "%s", "tooltip": "%s", "class": "workspaces"}\n' "$text" "$tooltip"
}

print_workspace

socat -U - "UNIX-CONNECT:$XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock" |
  while IFS= read -r line; do
    case "$line" in
    workspace\>\>* | \
      focusedmon\>\>* | \
      activewindow\>\>* | \
      openwindow\>\>* | \
      closewindow\>\>* | \
      movewindow\>\>* | \
      urgent\>\>* | \
      fullscreen\>\>* | \
      changefloatingmode\>\>* | \
      specialworkspace\>\>*)
      print_workspace
      ;;
    esac
  done
