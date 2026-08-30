#!/usr/bin/env python3
import json
import subprocess
import sys
import os
import time

BAR_WIDTH = 10
TOGGLE_FILE = "/tmp/waybar_battery_toggle"

# ── Native Toggle Handler ──────────────────────────────────
if len(sys.argv) > 1 and sys.argv[1] == "--toggle":
    if os.path.exists(TOGGLE_FILE):
        os.remove(TOGGLE_FILE)
    else:
        with open(TOGGLE_FILE, "w") as f:
            f.write("")
    # Force Waybar to refresh the module immediately (Signal 8 -> RTMIN+8)
    subprocess.run(["pkill", "-RTMIN+8", "waybar"], stderr=subprocess.DEVNULL)
    sys.exit(0)

def get_battery_info():
    try:
        bat_dir = "/sys/class/power_supply"
        # Find the active battery device (e.g., BAT0 or BAT1)
        bat_name = [d for d in os.listdir(bat_dir) if d.startswith("BAT")][0]
        with open(f"{bat_dir}/{bat_name}/capacity", "r") as f:
            cap = int(f.read().strip())
        with open(f"{bat_dir}/{bat_name}/status", "r") as f:
            stat = f.read().strip()
        return cap, stat
    except Exception:
        return 0, "Unknown"

def get_notification_count():
    try:
        count = subprocess.check_output(["swaync-client", "-c"], text=True).strip()
        return int(count) if count else 0
    except Exception:
        return 0

def is_hardware_active():
    cam_active = False
    if os.path.exists("/sys/class/video4linux"):
        for dev in os.listdir("/sys/class/video4linux"):
            try:
                with open(f"/sys/class/video4linux/{dev}/index", "r") as f: pass
                cam_active = True
            except: pass
            
    mic_active = False
    try:
        wp_out = subprocess.check_output(["wpctl", "status"], text=True)
        if "[running]" in wp_out.lower() and "capture" in wp_out.lower():
            mic_active = True
    except: pass
    return cam_active or mic_active

def get_music_progress():
    try:
        status = subprocess.check_output(["playerctl", "status"], text=True).strip()
        if status != "Playing": return None
        pos = float(subprocess.check_output(["playerctl", "position"], text=True).strip())
        length_str = subprocess.check_output(["playerctl", "metadata", "mpris:length"], text=True).strip()
        if not length_str: return None
        length = float(length_str) / 1000000.0
        percent = min(100, max(0, int((pos / length) * 100)))
        filled = (percent * BAR_WIDTH) // 100
        return "━" * filled + "╌" * (BAR_WIDTH - filled)
    except:
        return None

def main():
    cap, stat = get_battery_info()
    hw_alert = is_hardware_active()
    unread_notifs = get_notification_count()
    music_bar = get_music_progress()
    
    # Base Battery Configuration
    state = "discharging"
    icon = "󰁅"
    
    if stat == "Full":
        icon, state = "󰄬", "full"
    elif stat == "Charging":
        icon, state = "󱐋", "charging"
    elif stat == "Not charging" or cap == 100:
        icon, state = "󰐧", "plugged"
    elif cap < 20:
        icon, state = "󰁃", "critical"

    # ── Priority Processing Chain ──────────────────────────
    if hw_alert:
        state = "hardware-alert"
        shift = int(time.time() * 2) % 2
        display_text = "󰍬 In use 󰄀" if shift == 0 else " 󰍬 In use 󰄀 "
        
    elif unread_notifs > 0:
        state = "notification"
        display_text = f"  {unread_notifs} NOTIF" if int(time.time()) % 2 == 0 else f"   {unread_notifs} NOTIF"
        
    elif music_bar is not None:
        state = "music"
        display_text = f"󰎈 <span font_family='Monaspace Krypton'>{music_bar}</span>"
        
    else:
        # Standalone Battery Presentation Logic
        if os.path.exists(TOGGLE_FILE):
            symbol = "<span font_weight='black' size='small' rise='-600' alpha='65%'>%</span>"
            display_text = f"{icon} {cap}{symbol}"
        else:
            filled = (cap * BAR_WIDTH) // 100
            bat_bar = "━" * filled + "╌" * (BAR_WIDTH - filled)
            display_text = f"{icon} <span font_family='Monaspace Krypton'>{bat_bar}</span>"

    tooltip = f"<b>Status:</b> {stat}\n<b>Battery:</b> {cap}%"
    print(json.dumps({"text": display_text, "class": state, "tooltip": tooltip}))

if __name__ == "__main__":
    main()
