#!/bin/bash

# ── Single-instance guard ─────────────────────────────────
LOCKFILE="/tmp/waybar-workspace.lock"

if [ -f "$LOCKFILE" ]; then
  OLD_PID=$(cat "$LOCKFILE")
  if kill -0 "$OLD_PID" 2>/dev/null; then
    # Old instance is alive — kill it and wait for it to die
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
  # Browsers
  *zen*) echo "󰾔" ;;
  *firefox* | *librewolf* | *waterfox*) echo "󰈹" ;;
  *chromium* | *chrome* | *brave* | *vivaldi* | *opera* | *edge*) echo "󰖟" ;;
  # Terminals
  *kitty* | *alacritty* | *foot* | *wezterm* | *ghostty*) echo "󰩊" ;;
  *konsole* | *gnome-terminal* | *xterm*) echo "󰆍" ;;
  # Editors / IDEs
  *code* | *vscodium* | *codium*) echo "󰨞" ;;
  *sublime*) echo "󰺿" ;;
  *neovide* | *nvim*) echo "" ;;
  *vim* | *emacs*) echo "󰏖" ;;
  *jetbrains* | *idea* | *pycharm* | *goland* | *clion* | *rider*) echo "󱃖" ;;
  # File managers
  *nautilus* | *files*) echo "󰉋" ;;
  *thunar* | *nemo*) echo "󰉖" ;;
  *dolphin*) echo "󰉗" ;;
  *ranger* | *yazi* | *lf*) echo "󰙅" ;;
  # Media
  *spotify*) echo "󰓇" ;;
  *vlc*) echo "󰕼" ;;
  *mpv*) echo "󰎁" ;;
  *rhythmbox* | *lollypop* | *strawberry*) echo "󰝚" ;;
  *celluloid* | *totem*) echo "󰿎" ;;
  # Communication
  *discord* | *equibop* | *vesktop*) echo "󰙯" ;;
  *telegram*) echo "󰔁" ;;
  *slack*) echo "󰒱" ;;
  *thunderbird* | *geary*) echo "󰇮" ;;
  *signal*) echo "󰍕" ;;
  *element* | *nheko*) echo "󰭻" ;;
  # Notes / Docs
  *obsidian*) echo "󱓧" ;;
  *notion*) echo "󰟣" ;;
  *libreoffice* | *soffice*) echo "󱎺" ;;
  *evince* | *okular* | *zathura* | *mupdf*) echo "󰈦" ;;
  # Graphics / Design
  *gimp*) echo "󰃉" ;;
  *inkscape*) echo "󰺾" ;;
  *krita* | *blender*) echo "󰂫" ;;
  *figma*) echo "󰖟" ;;
  # Games
  *steam*) echo "󰓓" ;;
  *lutris* | *heroic*) echo "󰺵" ;;
  # System tools
  *htop* | *btop* | *nvtop*) echo "󰓠" ;;
  *pavucontrol* | *easyeffects*) echo "󰕾" ;;
  *nm-connection* | *networkmanager*) echo "󰤨" ;;
  *blueman* | *bluetooth*) echo "󰂯" ;;
  *virt-manager* | *qemu* | *virtualbox*) echo "󰟀" ;;
  *docker*) echo "󰡨" ;;
  # Misc
  *bitwarden* | *keepassxc*) echo "󰌋" ;;
  *feh* | *imv* | *eog* | *shotwell*) echo "󰋩" ;;
  *xournalpp* | *xournal*) echo "󱓧" ;;
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
    echo "󰿚"
    return
  fi

  # If the focused window is on this workspace, prioritise it
  if [[ -n "$focused_class" ]] && echo "$all_classes" | grep -qF "$focused_class"; then
    classify_class "$focused_class"
    return
  fi

  # Otherwise pick by priority
  local priority=(
    zen firefox librewolf chromium brave vivaldi
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

# ── Friendly names ────────────────────────────────────────
friendly_name() {
  local cls="${1,,}"
  case "$cls" in
  *zen* | *firefox* | *librewolf* | *waterfox* | *chromium* | *helium* | *chrome* | *brave* | *vivaldi* | *opera* | *edge*) echo "browser" ;;
  *kitty* | *alacritty* | *foot* | *wezterm* | *ghostty* | *konsole* | *gnome-terminal* | *xterm*) echo "terminal" ;;
  *code* | *vscodium* | *codium* | *sublime* | *neovide* | *nvim* | *vim* | *emacs*) echo "editor" ;;
  *jetbrains* | *idea* | *pycharm* | *goland* | *clion* | *rider*) echo "ide" ;;
  *nautilus* | *files* | *thunar* | *nemo* | *dolphin*) echo "files" ;;
  *ranger* | *yazi* | *lf*) echo "files" ;;
  *spotify*) echo "spotify" ;;
  *vlc* | *mpv* | *celluloid* | *totem* | *rhythmbox* | *lollypop* | *strawberry*) echo "media" ;;
  *discord* | *equibop* | *vesktop*) echo "discord" ;;
  *telegram*) echo "telegram" ;;
  *slack*) echo "slack" ;;
  *signal*) echo "signal" ;;
  *element* | *nheko*) echo "matrix" ;;
  *obsidian*) echo "obsidian" ;;
  *notion*) echo "notion" ;;
  *steam* | *lutris* | *heroic*) echo "games" ;;
  *gimp* | *inkscape* | *krita* | *blender* | *figma*) echo "design" ;;
  *libreoffice* | *soffice* | *evince* | *okular* | *zathura* | *mupdf*) echo "docs" ;;
  *) echo "${1#org.gnome.}" ;;
  esac
}

print_workspace() {
  local all_clients ws_data ws_id ws_name title win_count total_count \
    special_open special_id special_count \
    active_workspaces tooltip text cls

  all_clients=$(hyprctl clients -j 2>/dev/null)
  ws_data=$(hyprctl activeworkspace -j 2>/dev/null)
  ws_id=$(echo "$ws_data" | jq -r '.id')
  ws_name=$(echo "$ws_data" | jq -r '.name')
  active_workspaces=$(echo "$all_clients" | jq '[.[].workspace.id] | unique | length')

  if [[ "$ws_name" == special* ]]; then
    special_open=true
  else
    special_open=false
  fi

  special_id=$(echo "$all_clients" | jq -r '[.[] | select(.workspace.name | startswith("special")) | .workspace.id] | first // empty')
  if [[ -n "$special_id" ]]; then
    special_count=$(echo "$all_clients" | jq "[.[] | select(.workspace.name | startswith(\"special\"))] | length")
  else
    special_count=0
  fi

  title=$(hyprctl activewindow -j 2>/dev/null | jq -r '.title // empty' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
  if [[ ${#title} -gt 30 ]]; then
    title="$(printf '%s' "${title:0:29}" | sed 's/[[:space:]]*$//')…"
  fi
  win_count=$(echo "$all_clients" | jq "[.[] | select(.workspace.id == $ws_id)] | length")
  total_count=$(echo "$all_clients" | jq '[.[] | select(.mapped)] | length')

  if $special_open && [[ -n "$special_id" ]]; then
    text="󰜉 $special_count"
    cls="special"
  elif [[ -n "$title" ]]; then
    text="$ws_id/12 • $title • $total_count windows open"
    [[ "$total_count" -eq 1 ]] && text="$ws_id/12 • $title • 1 window open"
    cls="ws-$ws_id"
  else
    text="$ws_id/12 • empty • $total_count windows open"
    [[ "$total_count" -eq 1 ]] && text="$ws_id/12 • empty • 1 window open"
    cls="ws-$ws_id"
  fi

  tooltip=""
  local ws classes names line c
  for ws in $(seq 1 12); do
    classes=$(echo "$all_clients" | jq -r --arg id "$ws" '.[] | select(.workspace.id == ($id | tonumber)) | .class' | sort -u)
    [[ -z "$classes" ]] && continue
    names=""
    while IFS= read -r c; do
      [[ -z "$c" ]] && continue
      [[ -n "$names" ]] && names="$names, "
      names="$names$(friendly_name "$c")"
    done <<< "$classes"
    line="○ ws $ws [$names]"
    [[ "$ws" == "$ws_id" ]] && line="●${line:1}"
    tooltip="$tooltip$line\n"
  done
  if [[ -n "$special_id" ]]; then
    tooltip="${tooltip}────────────\n󰜉 special [$special_count window(s)]\n"
  fi
  tooltip="<span font_family='Monaspace Krypton NF'>${tooltip%\\n}</span>"

  printf '{"text": "%s", "tooltip": "%s", "class": "%s"}\n' "$text" "$tooltip" "$cls"
}

# ── Main ──────────────────────────────────────────────────
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
      changefloatingmode\>\>*)
      print_workspace
      ;;
    esac
  done
