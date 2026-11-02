#!/usr/bin/env bash

# Use the results from your manual test above
D_RES="2304x1296@60"
G_RES="1280x720@60"

# Listen to the Hyprland event socket
socat -U - UNIX-CONNECT:$XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock | while read -r line; do
    if [[ $line == "fullscreen>>1" ]]; then
        # Switch to Game Res
        hyprctl keyword monitor "eDP-1,$G_RES,auto,1"
    elif [[ $line == "fullscreen>>0" ]]; then
        # Switch back to Desktop Res
        hyprctl keyword monitor "eDP-1,$D_RES,auto,1"
    fi
done

