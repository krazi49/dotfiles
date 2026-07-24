#!/usr/bin/env python3
# power-vert-lock.py — hyprlock label version of power-vert.sh
#
# Differences from the Waybar version:
#   • outputs a raw pango string, not JSON (hyprlock `cmd[update:N]` reads stdout directly)
#   • no click-handler argument dispatch (hyprlock labels are non-interactive)
#   • no is_auth_active() — hyprctl clients is unreliable from the lock screen
#   • bar is wider (BAR_WIDTH = 20 instead of 10)
#   • notification and DND branches are dropped — not meaningful on a lock screen
#   • music branch is kept — playerctl works fine from the lock screen
#
# Hyprlock config usage:
#
#   label {
#       monitor =
#       text     = cmd[update:1000] /path/to/power-vert-lock.py
#       font_family = Paper Mono
#       font_size   = 14
#       color       = rgba(cdd6f4ff)
#       position    = 0, -40
#       halign      = center
#       valign      = center
#   }

import json
import subprocess
import os
import time
import html

BAR_WIDTH          = 20          # wider than the Waybar version (was 10)
TOGGLE_BATTERY     = "/tmp/waybar_battery_toggle"
FLASH_FILE         = "/tmp/waybar_adaptive_flash"
PREV_STAT_FILE     = "/tmp/waybar_adaptive_prev_stat"
CHARGER_EVENT_FILE = "/tmp/waybar_adaptive_charger_event"
MIC_START_FILE     = "/tmp/waybar_adaptive_mic_start"
CPU_CACHE_FILE     = "/tmp/waybar_adaptive_cpu_cache"
CHARGER_SHOW_SECS  = 5
LOW_BAT_THRESHOLD  = 15
CPU_TEMP_WARN      = 90
GPU_TEMP_WARN      = 100
BT_FLASH_FILE      = "/tmp/waybar_adaptive_bt_flash"
BT_PREV_FILE       = "/tmp/waybar_adaptive_bt_prev"
BT_FLASH_SECS      = 2
SCREENREC_START    = "/tmp/waybar_adaptive_screenrec"
USB_FLASH_FILE     = "/tmp/waybar_adaptive_usb_flash"
USB_PREV_FILE      = "/tmp/waybar_adaptive_usb_prev"
USB_FLASH_SECS     = 2


# ── Helpers ────────────────────────────────────────────────
def read_sysfs(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except:
        return None

def make_bar(filled, total):
    """Split bar — fills outward from centre. Returns (left, right) pango strings."""
    filled = max(0, min(filled, total))
    half   = total // 2
    f      = filled // 2
    e      = half - f
    left   = (f"<span alpha='20%'>{'━' * e}</span>" if e else "") + ("━" * f)
    right  = ("━" * f) + (f"<span alpha='20%'>{'━' * e}</span>" if e else "")
    return left, right

def make_bar_str(filled, total):
    filled = max(0, min(filled, total))
    return "━" * filled + "╌" * (total - filled)

def fmt_time(seconds):
    s = int(round(seconds))
    return f"{s // 60}:{s % 60:02d}"

def split_text(icon, left, right, alpha=None):
    a = f" alpha='{alpha}'" if alpha else ""
    return (
        f"<span font_family='Paper Mono'{a}>{left}</span> "
        f"{icon} "
        f"<span font_family='Paper Mono'{a}>{right}</span>"
    )


# ── Battery ────────────────────────────────────────────────
def get_battery_info():
    bat_dir = "/sys/class/power_supply"
    try:
        bat_name = next(d for d in os.listdir(bat_dir) if d.startswith("BAT"))
        base = f"{bat_dir}/{bat_name}"
        cap  = int(read_sysfs(f"{base}/capacity") or 0)
        stat = read_sysfs(f"{base}/status") or "Unknown"

        charge_now  = read_sysfs(f"{base}/charge_now")
        charge_full = read_sysfs(f"{base}/charge_full")
        current_now = read_sysfs(f"{base}/current_now")
        time_str = ""
        if current_now and int(current_now) > 0:
            c = int(current_now)
            if stat == "Discharging" and charge_now:
                h = int(charge_now) / c
                time_str = f"{int(h)}h {int((h % 1) * 60):02d}m"
            elif stat == "Charging" and charge_now and charge_full:
                h = (int(charge_full) - int(charge_now)) / c
                time_str = f"{int(h)}h {int((h % 1) * 60):02d}m"

        return cap, stat, time_str
    except:
        return 0, "Unknown", ""

def normalise_stat(stat):
    if stat in ("Full", "Not charging"):
        return "Charging"
    return stat

def handle_flash(stat, cap):
    norm = normalise_stat(stat)
    prev = read_sysfs(PREV_STAT_FILE) or ""

    if norm in ("Charging", "Discharging"):
        try:
            with open(PREV_STAT_FILE, "w") as f:
                f.write(norm)
        except:
            pass

    if prev and norm != prev and not os.path.exists(FLASH_FILE):
        is_plug   = norm == "Charging"    and prev == "Discharging"
        is_unplug = norm == "Discharging" and prev == "Charging"
        if is_plug or is_unplug:
            ftype = "plug" if is_plug else "unplug"
            try:
                with open(FLASH_FILE, "w") as f:
                    f.write(f"{int(time.time())} {ftype}")
            except:
                pass

    flash_active, flash_icon = False, ""
    if os.path.exists(FLASH_FILE):
        try:
            content = read_sysfs(FLASH_FILE)
            if content and len(content.split()) == 2:
                ts, ftype = content.split()
                age = int(time.time()) - int(ts)
                if age < 2:
                    flash_active = True
                    flash_icon   = "󱐋" if ftype == "plug" else "󰚦"
                else:
                    os.remove(FLASH_FILE)
                    if not os.path.exists(CHARGER_EVENT_FILE):
                        with open(CHARGER_EVENT_FILE, "w") as f:
                            f.write(str(int(time.time())))
            else:
                os.remove(FLASH_FILE)
        except:
            pass

    charger_window = False
    if os.path.exists(CHARGER_EVENT_FILE):
        try:
            ts_str = read_sysfs(CHARGER_EVENT_FILE)
            if ts_str:
                age = int(time.time()) - int(ts_str)
                if age < CHARGER_SHOW_SECS:
                    charger_window = True
                else:
                    os.remove(CHARGER_EVENT_FILE)
            else:
                os.remove(CHARGER_EVENT_FILE)
        except:
            pass

    return flash_active, flash_icon, charger_window


# ── Hardware / mic ─────────────────────────────────────────
def is_hardware_active():
    cam_active = False
    mic_active = False

    if os.path.exists("/sys/class/video4linux"):
        for dev in os.listdir("/sys/class/video4linux"):
            p = f"/sys/class/video4linux/{dev}/power/runtime_status"
            if read_sysfs(p) == "active":
                cam_active = True
                break

    try:
        nodes = json.loads(subprocess.check_output(["pw-dump"], text=True))
        for node in nodes:
            if node.get("type") == "PipeWire:Interface:Node":
                info  = node.get("info", {})
                props = info.get("props", {})
                mc    = props.get("media.class", "")
                nn    = props.get("node.name", "").lower()
                if info.get("state") == "running":
                    if "Audio/Source" in mc or "Stream/Input/Audio" in mc:
                        if "monitor" not in nn and "monitor" not in mc.lower():
                            mic_active = True
                            break
    except:
        pass

    active = cam_active or mic_active
    if active and not os.path.exists(MIC_START_FILE):
        try:
            with open(MIC_START_FILE, "w") as f:
                f.write(str(int(time.time())))
        except:
            pass
    elif not active and os.path.exists(MIC_START_FILE):
        try:
            os.remove(MIC_START_FILE)
        except:
            pass
    return active

def get_recording_duration():
    if not os.path.exists(MIC_START_FILE):
        return ""
    try:
        ts = int(read_sysfs(MIC_START_FILE))
        return fmt_time(int(time.time()) - ts)
    except:
        return ""


# ── Music ──────────────────────────────────────────────────
def get_metadata_safe(key):
    try:
        return subprocess.check_output(
            ["playerctl", "metadata", key],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
    except:
        return ""

def get_music_data():
    try:
        status = subprocess.check_output(
            ["playerctl", "status"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except:
        return None
    if not status or status == "No players found":
        return None

    title  = get_metadata_safe("title")  or "Unknown Track"
    artist = get_metadata_safe("artist") or "Unknown Artist"

    try:
        pos = float(subprocess.check_output(
            ["playerctl", "position"], text=True, stderr=subprocess.DEVNULL
        ).strip())
        length_raw = get_metadata_safe("mpris:length")
        length = float(length_raw) / 1_000_000 if length_raw else 0.0
    except:
        pos, length = 0.0, 0.0

    return {
        "status": status,
        "title": title, "artist": artist,
        "position": pos, "length": length,
    }


# ── System health ──────────────────────────────────────────
def get_system_faults():
    try:
        cpu_pct = 0.0
        cached = read_sysfs(CPU_CACHE_FILE)
        if cached:
            try:
                cpu_pct = float(cached)
            except:
                pass

        mem = {}
        with open("/proc/meminfo") as f:
            for line in f:
                k, v = line.split(":", 1)
                mem[k.strip()] = int(v.strip().split()[0])
        ram_pct = 100.0 * (1 - mem["MemAvailable"] / mem["MemTotal"])

        if cpu_pct > 90 or ram_pct > 90:
            return True, f"CPU {cpu_pct:.0f}%  RAM {ram_pct:.0f}%"
        return False, ""
    except:
        return False, ""


# ── Temperature ────────────────────────────────────────────
def get_temps():
    cpu_temp = None
    gpu_temp = None

    hwmon_base = "/sys/class/hwmon"
    if os.path.exists(hwmon_base):
        for hw in sorted(os.listdir(hwmon_base)):
            name_path = f"{hwmon_base}/{hw}/name"
            name = read_sysfs(name_path) or ""
            if name in ("coretemp", "k10temp", "zenpower", "cpu_thermal"):
                hw_path = f"{hwmon_base}/{hw}"
                for f in sorted(os.listdir(hw_path)):
                    if f.startswith("temp") and f.endswith("_input"):
                        val = read_sysfs(f"{hw_path}/{f}")
                        if val:
                            t = int(val) / 1000
                            if cpu_temp is None or t > cpu_temp:
                                cpu_temp = t
                if cpu_temp is not None:
                    break

    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        gpu_temp = float(out.split()[0])
    except:
        for hw in sorted(os.listdir(hwmon_base)) if os.path.exists(hwmon_base) else []:
            name = read_sysfs(f"{hwmon_base}/{hw}/name") or ""
            if name in ("amdgpu", "radeon"):
                for f in sorted(os.listdir(f"{hwmon_base}/{hw}")):
                    if f.startswith("temp") and f.endswith("_input"):
                        val = read_sysfs(f"{hwmon_base}/{hw}/{f}")
                        if val:
                            t = int(val) / 1000
                            if gpu_temp is None or t > gpu_temp:
                                gpu_temp = t
                break

    return cpu_temp, gpu_temp

def check_temp_warning(cpu_temp, gpu_temp):
    parts = []
    if cpu_temp is not None and cpu_temp >= CPU_TEMP_WARN:
        parts.append(f"CPU {cpu_temp:.0f}°C")
    if gpu_temp is not None and gpu_temp >= GPU_TEMP_WARN:
        parts.append(f"GPU {gpu_temp:.0f}°C")
    if parts:
        return True, "  ".join(parts)
    return False, ""


# ── Bluetooth flash ────────────────────────────────────────
def handle_bt_flash():
    try:
        out = subprocess.check_output(
            ["bluetoothctl", "devices", "Connected"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        current_count = len([l for l in out.splitlines() if l.strip()])
    except:
        current_count = 0

    prev_str   = read_sysfs(BT_PREV_FILE)
    prev_count = int(prev_str) if prev_str and prev_str.isdigit() else current_count

    try:
        with open(BT_PREV_FILE, "w") as f:
            f.write(str(current_count))
    except:
        pass

    if prev_count != current_count and not os.path.exists(BT_FLASH_FILE):
        connected = current_count > prev_count
        try:
            with open(BT_FLASH_FILE, "w") as f:
                f.write(f"{int(time.time())} {'connect' if connected else 'disconnect'}")
        except:
            pass

    if os.path.exists(BT_FLASH_FILE):
        try:
            content = read_sysfs(BT_FLASH_FILE)
            if content and len(content.split()) == 2:
                ts, etype = content.split()
                age = int(time.time()) - int(ts)
                if age < BT_FLASH_SECS:
                    icon = "󰂱" if etype == "connect" else "󰂲"
                    return True, icon
                else:
                    os.remove(BT_FLASH_FILE)
        except:
            pass

    return False, ""


# ── USB flash ──────────────────────────────────────────────
def handle_usb_flash():
    usb_base      = "/sys/bus/usb/devices"
    current_count = 0
    if os.path.exists(usb_base):
        for dev in os.listdir(usb_base):
            vendor        = read_sysfs(f"{usb_base}/{dev}/idVendor")
            product_class = read_sysfs(f"{usb_base}/{dev}/bDeviceClass")
            if vendor and product_class != "09":
                current_count += 1

    prev_str   = read_sysfs(USB_PREV_FILE)
    prev_count = int(prev_str) if prev_str and prev_str.isdigit() else current_count

    try:
        with open(USB_PREV_FILE, "w") as f:
            f.write(str(current_count))
    except:
        pass

    if prev_count != current_count and not os.path.exists(USB_FLASH_FILE):
        plugged = current_count > prev_count
        try:
            with open(USB_FLASH_FILE, "w") as f:
                f.write(f"{int(time.time())} {'plug' if plugged else 'unplug'}")
        except:
            pass

    if os.path.exists(USB_FLASH_FILE):
        try:
            content = read_sysfs(USB_FLASH_FILE)
            if content and len(content.split()) == 2:
                ts, etype = content.split()
                age = int(time.time()) - int(ts)
                if age < USB_FLASH_SECS:
                    icon = "󰕓" if etype == "plug" else "󰅖"
                    return True, icon
                else:
                    os.remove(USB_FLASH_FILE)
        except:
            pass

    return False, ""


# ── Screen recording ───────────────────────────────────────
def get_screen_recording():
    try:
        subprocess.check_output(
            ["pgrep", "-x", "gpu-screen-recor"],
            stderr=subprocess.DEVNULL
        )
        active = True
    except subprocess.CalledProcessError:
        active = False

    if active and not os.path.exists(SCREENREC_START):
        try:
            with open(SCREENREC_START, "w") as f:
                f.write(str(int(time.time())))
        except:
            pass
    elif not active and os.path.exists(SCREENREC_START):
        try:
            os.remove(SCREENREC_START)
        except:
            pass

    if active and os.path.exists(SCREENREC_START):
        try:
            ts = int(read_sysfs(SCREENREC_START))
            return True, fmt_time(int(time.time()) - ts)
        except:
            return True, ""
    return False, ""


# ── Main ───────────────────────────────────────────────────
def main():
    cap, stat, time_str             = get_battery_info()
    flash_active, flash_icon, c_win = handle_flash(stat, cap)
    hw_alert                        = is_hardware_active()
    m                               = get_music_data()
    fault_active, fault_msg         = get_system_faults()
    cpu_temp, gpu_temp              = get_temps()
    temp_warn, temp_msg             = check_temp_warning(cpu_temp, gpu_temp)
    bt_flash, bt_icon               = handle_bt_flash()
    usb_flash, usb_icon             = handle_usb_flash()
    rec_active, rec_duration        = get_screen_recording()

    # battery icon
    bat_icon = "󰁅"
    if stat == "Full" or cap >= 100:
        bat_icon = "󰄬"
    elif stat == "Charging":
        bat_icon = "󱐋"
    elif stat == "Not charging":
        bat_icon = "󰐧"
    elif cap < LOW_BAT_THRESHOLD:
        bat_icon = "󰁃"

    low_battery = cap < LOW_BAT_THRESHOLD and stat == "Discharging"

    _bl,   _br   = make_bar((cap * BAR_WIDTH) // 100, BAR_WIDTH)
    _full_l, _full_r = make_bar(BAR_WIDTH, BAR_WIDTH)
    _empty_l, _empty_r = make_bar(0, BAR_WIDTH)
    bat_text     = split_text(bat_icon, _bl, _br)

    # ── Priority chain ─────────────────────────────────────
    #  0  temperature warning
    #  1  low battery
    #  2  charger flash (2s)
    #  3  charger window (5s)
    #  4  screen recording
    #  5  bt flash (2s)
    #  6  usb flash (2s)
    #  7  cam/mic active
    #  8  system resource fault
    #  9  music
    # 10  default battery

    if temp_warn:
        blink        = (time.time() % 0.75) < 0.5
        _tl, _tr     = make_bar(BAR_WIDTH if blink else 0, BAR_WIDTH)
        display_text = split_text("󱃃", _tl, _tr)

    elif low_battery and not flash_active:
        blink        = (time.time() % 0.75) < 0.5
        display_text = split_text(bat_icon, _bl if blink else _empty_l, _br if blink else _empty_r)

    elif flash_active:
        display_text = split_text(flash_icon, _full_l, _full_r)

    elif c_win:
        display_text = bat_text

    elif rec_active:
        dur_str      = f" {rec_duration}" if rec_duration else ""
        display_text = split_text(f"󰹑{dur_str}", _full_l, _full_r)

    elif bt_flash:
        display_text = split_text(bt_icon, _full_l, _full_r)

    elif usb_flash:
        display_text = split_text(usb_icon, _full_l, _full_r)

    elif hw_alert:
        duration     = get_recording_duration()
        dur_str      = f" {duration}" if duration else ""
        display_text = split_text(f"󰍬{dur_str}", _full_l, _full_r)

    elif fault_active:
        blink        = (time.time() % 0.75) < 0.5
        _fl, _fr     = make_bar(BAR_WIDTH if blink else 0, BAR_WIDTH)
        display_text = split_text("󰘚", _fl, _fr)

    elif m is not None and m["status"] in ("Playing", "Paused"):
        is_paused    = m["status"] == "Paused"
        music_icon   = "󰏤" if is_paused else "󰝚"
        pct          = min(1.0, max(0.0, m["position"] / m["length"])) if m["length"] > 0 else 0.0
        _ml, _mr     = make_bar(int(pct * BAR_WIDTH), BAR_WIDTH)
        # show artist – title below the bar in a dimmed span
        label        = html.escape(f"{m['artist']} – {m['title']}")
        display_text = (
            split_text(music_icon, _ml, _mr)
            + f"\n<span alpha='60%' font_size='small'>{label}</span>"
        )

    else:
        # default: battery % + time remaining/to full
        suffix = f"  <span alpha='55%'>{time_str}</span>" if time_str else ""
        display_text = bat_text + suffix

    # hyprlock reads stdout directly — no JSON wrapper
    print(display_text)

if __name__ == "__main__":
    main()
