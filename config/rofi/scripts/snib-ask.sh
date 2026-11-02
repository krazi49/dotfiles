#!/bin/bash
mkdir -p /tmp/snib-eyes
exec 2>>/tmp/snib-eyes/debug.log

# environment the keybind doesn't give you
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
[[ -s "$HOME/.nvm/nvm.sh" ]] && source "$HOME/.nvm/nvm.sh"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
if [[ -z "$WAYLAND_DISPLAY" ]]; then
  export WAYLAND_DISPLAY=$(ls "$XDG_RUNTIME_DIR" | grep -m1 '^wayland-[0-9]*$')
fi
if [[ -z "$HYPRLAND_INSTANCE_SIGNATURE" ]]; then
  export HYPRLAND_INSTANCE_SIGNATURE=$(ls -t "$XDG_RUNTIME_DIR/hypr" 2>/dev/null | head -n1)
fi

THEME="$HOME/.config/rofi/config.rasi"

if [[ -n "$1" ]]; then
  question="$1"
else
  question=$(rofi -dmenu -theme "$THEME" -p "ask snib about your screen:" | head -n 1)
fi
[[ -z "$question" ]] && exit 0

shot=/tmp/snib-eyes/shot.png
grim "$shot"
[[ ! -s "$shot" ]] && exit 0
echo "$question" >/tmp/snib-eyes/question

ans=$(openclaw infer model run --model snibble/eyes \
  --file "$shot" --prompt "$question" </dev/null 2>>/tmp/snib-eyes/debug.log)
status=$?

if [[ $status -ne 0 || -z "$ans" ]]; then
  ans="openclaw failed (exit $status)
$(tail -n 15 /tmp/snib-eyes/debug.log)
which openclaw: $(command -v openclaw || echo 'not found')"
fi

setsid -f kitty --class floating_snib --title "snib·eyes" bash -c '
  printf "\n%s\n\n" "$1"
  read -n1 -rsp "done. press any key"
' bash "$ans" >/dev/null 2>&1
