#!/bin/bash

DYNAMIC_CSS="$HOME/.config/waybar/dynamic.css"

update_bar() {
  ACTIVE_WS=$(hyprctl activeworkspace -j | jq '.id')
  TILED=$(hyprctl clients -j | jq "[.[] | select(.workspace.id == $ACTIVE_WS and .floating == false)] | length")

  if [ "$TILED" -eq 0 ]; then
    cat >"$DYNAMIC_CSS" <<'EOF'
window#waybar.left {
    min-height: 0;
    min-width: 0;
}
EOF
  else
    echo "" >"$DYNAMIC_CSS"
  fi

  pkill -SIGHUP waybar
}

# initialise on start
update_bar

# watch socket for relevant events
socat - "UNIX-CONNECT:$XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock" |
  while read -r line; do
    case "$line" in
    workspace\>* | openwindow\>* | closewindow\>* | movewindow\>* | floating\>*)
      update_bar
      ;;
    esac
  done
