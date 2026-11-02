#!/usr/bin/env python3
import json
import subprocess
import sys

def get_updates():
    pacman_count = 0
    aur_count = 0
    
    try:
        # checkupdates uses pacman sync database without touching root db
        res = subprocess.run(["checkupdates"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            pacman_count = len(res.stdout.strip().splitlines())
    except Exception:
        pass

    try:
        # yay -Qu for AUR/foreign package updates
        res = subprocess.run(["yay", "-Qu", "--aur"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            aur_count = len(res.stdout.strip().splitlines())
    except Exception:
        pass

    total = pacman_count + aur_count
    tooltip = f"Pacman: {pacman_count}\nAUR: {aur_count}"
    
    if total > 0:
        text = f"󰚰 {total}"
    else:
        text = "󰚰 0"  # always show the badge, even when clean
        
    out = {
        "text": text,
        "alt": str(total),
        "tooltip": tooltip,
        "class": "updates"
    }
    print(json.dumps(out))

if __name__ == "__main__":
    get_updates()