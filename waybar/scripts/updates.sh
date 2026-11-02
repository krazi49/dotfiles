#!/bin/bash
# Pacman & AUR update checker script for waybar

get_updates() {
    # Check official pacman updates using checkupdates
    # checkupdates exits with 2 if no updates are found on some versions, or 0 with output
    pacman_updates=$(checkupdates 2>/dev/null | wc -l)
    
    # Check AUR updates using yay (non-interactive, query only)
    # yay -Qua lists upgradable AUR packages
    aur_updates=$(yay -Qua 2>/dev/null | wc -l)
    
    total=$((pacman_updates + aur_updates))
    
    if [ "$total" -gt 0 ]; then
        text="󰚰  $total"
        tooltip="Official: $pacman_updates\nAUR: $aur_updates"
        class="update"
    else
        text="󰚰  0"
        tooltip="System is up to date"
        class="updated"
    fi
    
    printf '{"text": "%s", "tooltip": "%s", "class": "%s"}\n' "$text" "$tooltip" "$class"
}

get_updates
