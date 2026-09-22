#!/usr/bin/env python3
import json
import subprocess
import sys
import os
import time
import html

BAR_WIDTH_COMPACT  = 10
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
BADGE_CELLS        = 2

BADGE_ICON = {
    "temp-warning":     "󱃃",
    "auth-waiting":     "󰌾",
    "screen-recording": "󰹑",
    "bt-flash":         "󰂱",
    "usb-flash":        "󰕓",
    "pomodoro":         "󰅐",
    "clipboard-flash":  "󰅇",
    "hardware-alert":   "󰍬",
    "notification":     "󰂚",
    "music":            "󰝚",
    "music-paused":     "󰏤",
    "dnd":              "󰂛",
    "charging":         "󱐋",
    "full":             "󰄬",
    "plugged":          "󰐧",
    "critical":         "󰁃",
    "discharging":      "󰁅",
}

# Braille sub-cell bar: 8 sub-positions per cell.
BRAILLE_STEPS = ["⠀", "⠁", "⠃", "⠇", "⡇", "⡗", "⡟", "⡿", "⣿"]
BRAILLE_SUB   = 8

BASE_URGENCY = {
    "temp-warning":     100,
    "critical":          90,
    "auth-waiting":      85,
    "screen-recording":  60,
    "hardware-alert":    55,
    "bt-flash":          45,
    "usb-flash":         45,
    "clipboard-flash":   35,
    "notification":      40,
    "pomodoro":          30,
    "music":             20,
    "dnd":               15,
    "charging":          15,
    "full":              10,
    "plugged":           10,
    "discharging":        5,
}


def contextual_score(state, ctx):
    score = BASE_URGENCY.get(state, 0)

    if state == ctx["island"]:
        return -1

    loud_active = ctx["auth_active"] or ctx["temp_warn"] or ctx["rec_active"]

    if state in ("music", "dnd", "charging", "full", "plugged", "discharging"):
        if loud_active:
            score -= 20
        if ctx["island"] in ("temp-warning", "auth-waiting", "screen-recording"):
            score -= 15

    if state == "notification":
        if ctx["dnd_active"]:
            score -= 25
        if ctx["m"] is not None and ctx["m"]["status"] == "Playing":
            score -= 10
        if ctx["rec_active"] or ctx["auth_active"]:
            score += 10
        if ctx["notif_count"] >= 5:
            score += 15

    if state == "dnd":
        if ctx["notif_count"] == 0 and not loud_active:
            score -= 30

    if state == "music":
        if ctx["m"] and ctx["m"]["status"] == "Paused":
            score -= 15
        if ctx["pomo_active"]:
            score -= 10

    if state in ("bt-flash", "usb-flash", "clipboard-flash"):
        age = ctx.get("flash_age")
        if age is not None:
            if age < 1.0:
                score += 40
            elif age < 1.5:
                score += 15

    if state == "hardware-alert":
        if ctx["island"] in ("temp-warning", "screen-recording", "auth-waiting"):
            score -= 20

    if state == "charging":
        if ctx["cap"] >= 80:
            score -= 10

    if state == "auth-waiting":
        if ctx["temp_warn"]:
            score -= 15

    return max(0, score)


# ── Helpers ────────────────────────────────────────────────
def read_sysfs(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except:
        return None

def make_bar(filled, total):
    filled = max(0.0, min(float(filled), float(total)))
    sub_filled = int(round(filled * BRAILLE_SUB))
    full_cells, rem = divmod(sub_filled, BRAILLE_SUB)
    full_cells = max(0, min(full_cells, int(total)))
    empty_cells = max(0, int(total) - full_cells - (1 if rem else 0))

    on  = "⣿" * full_cells
    mid = BRAILLE_STEPS[rem] if rem else ""
    off = f"<span alpha='15%'>{'⣿' * empty_cells}</span>" if empty_cells else ""
    return on + mid + off, ""

def make_bar_str(filled, total):
    filled = max(0.0, min(float(filled), float(total)))
    sub_filled = int(round(filled * BRAILLE_SUB))
    full_cells, rem = divmod(sub_filled, BRAILLE_SUB)
    full_cells = max(0, min(full_cells, int(total)))
    empty_cells = max(0, int(total) - full_cells - (1 if rem else 0))

    on  = "⣿" * full_cells
    mid = BRAILLE_STEPS[rem] if rem else ""
    off = f"<span alpha='25%'>{'⣿' * empty_cells}</span>" if empty_cells else ""
    return on + mid + off

def fmt_time(seconds):
    s = int(round(seconds))
    return f"{s // 60}:{s % 60:02d}"

def tooltip(bar_str, headline, sub1="", sub2="", cap=0, stat="Unknown",
            uptime_str="", metered=False):
    parts = []
    if bar_str:
        parts.append(bar_str)
    parts.append(f"<span size='large' weight='bold'>{headline}</span>")
    if sub1:
        parts.append(f"<span alpha='70%'>{sub1}</span>")
    if sub2:
        parts.append(f"<span alpha='70%'>{sub2}</span>")

    strip_bits = []
    bat_color = None
    if stat == "Charging":
        bat_color = "#a6e3a1"
    elif stat == "Discharging" and cap < LOW_BAT_THRESHOLD:
        bat_color = "#f38ba8"

    if bat_color:
        strip_bits.append(f"<span foreground='{bat_color}'>{cap}%</span>")
    else:
        strip_bits.append(f"{cap}%")

    if uptime_str:
        strip_bits.append(uptime_str)
    if metered:
        strip_bits.append("metered")

    parts.append("<span alpha='40%'>" + "  ·  ".join(strip_bits) + "</span>")
    return "\n".join(parts)


# ── Tooltip builders (shared by island and badge) ─────────

def tt_temp(temp_msg, cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    return tooltip(make_bar_str(1.0, bar_cells), "High temperature", temp_msg, "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_auth(cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    return tooltip(make_bar_str(0.0, bar_cells), "Waiting for password",
                   "Polkit or sudo prompt is open.", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_charger_plug(cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    return tooltip(make_bar_str(cap / 100.0, bar_cells), "Charger plugged",
                   f"Battery at {cap}%", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_charger_unplug(cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    return tooltip(make_bar_str(cap / 100.0, bar_cells), "Charger unplugged",
                   f"Battery at {cap}%", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_recording(rec_duration, cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    return tooltip(make_bar_str(1.0, bar_cells), "Screen recording",
                   f"Duration: {rec_duration}" if rec_duration else "", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_bt(bt_icon, cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    label = "Bluetooth connected" if bt_icon == "󰂱" else "Bluetooth disconnected"
    return tooltip(make_bar_str(1.0, bar_cells), label, "", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_usb(usb_icon, cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    label = "USB device plugged" if usb_icon == "󰕓" else "USB device unplugged"
    return tooltip(make_bar_str(1.0, bar_cells), label, "", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_pomodoro(pomo_mins, pomo_secs, cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    fill = (25*60 - (pomo_mins*60 + pomo_secs)) / (25*60)
    return tooltip(make_bar_str(fill, bar_cells), "Pomodoro",
                   f"{pomo_mins}:{pomo_secs:02d} remaining", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_clipboard(cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    return tooltip(make_bar_str(1.0, bar_cells), "Clipboard updated", "", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_hardware(rec_duration, cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    return tooltip(make_bar_str(1.0, bar_cells), "Mic or camera active",
                   f"Duration: {rec_duration}" if rec_duration else "", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_notification(notif_count, cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    plural = "s" if notif_count != 1 else ""
    return tooltip(make_bar_str(min(notif_count, 8) / 8.0, bar_cells),
                   f"{notif_count} notification{plural}", "Waiting for attention", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_music(m, cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    pct = min(1.0, max(0.0, m["position"] / m["length"])) if m["length"] > 0 else 0.0
    return tooltip(make_bar_str(pct, bar_cells), html.escape(m['title']),
                   html.escape(m['artist']),
                   html.escape(m['album']) if m['album'] else "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_dnd(notif_count, cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    suppressed = (f"{notif_count} notification{'s' if notif_count != 1 else ''} suppressed"
                  if notif_count > 0 else "")
    return tooltip(make_bar_str(cap / 100.0, bar_cells), "Do not disturb",
                   suppressed, "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_battery(stat, cap, time_label, time_str, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    return tooltip(make_bar_str(cap / 100.0, bar_cells), stat,
                   f"Charge: {cap}%", f"{time_label}: {time_str}",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_critical(cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    return tooltip(make_bar_str(cap / LOW_BAT_THRESHOLD, bar_cells), "Battery low",
                   f"Battery at {cap}%", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)


# ── Battery ────────────────────────────────────────────────
def get_battery_info():
    bat_dir = "/sys/class/power_supply"
    try:
        bat_name = next(d for d in os.listdir(bat_dir) if d.startswith("BAT"))
        base = f"{bat_dir}/{bat_name}"
        cap  = int(read_sysfs(f"{base}/capacity") or 0)
        stat = read_sysfs(f"{base}/status") or "Unknown"

        volt_raw = read_sysfs(f"{base}/voltage_now")
        watt_raw = read_sysfs(f"{base}/power_now")
        volt = f"{int(volt_raw)/1_000_000:.2f}V" if volt_raw else "N/A"
        watt = f"{int(watt_raw)/1_000_000:.2f}W" if watt_raw else "N/A"

        charge_now  = read_sysfs(f"{base}/charge_now")
        charge_full = read_sysfs(f"{base}/charge_full")
        current_now = read_sysfs(f"{base}/current_now")
        time_str = "N/A"
        if current_now and int(current_now) > 0:
            c = int(current_now)
            if stat == "Discharging" and charge_now:
                h = int(charge_now) / c
                time_str = f"{int(h)}h {int((h%1)*60):02d}m"
            elif stat == "Charging" and charge_now and charge_full:
                h = (int(charge_full) - int(charge_now)) / c
                time_str = f"{int(h)}h {int((h%1)*60):02d}m"

        return cap, stat, volt, watt, time_str
    except:
        return 0, "Unknown", "N/A", "N/A", "N/A"

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


# ── Auth prompt detection ──────────────────────────────────
def is_auth_active():
    try:
        clients = json.loads(subprocess.check_output(
            ["hyprctl", "clients", "-j"],
            text=True, stderr=subprocess.DEVNULL
        ))
        for client in clients:
            cls   = client.get("class", "").lower()
            title = client.get("title", "").lower()
            if any(kw in cls or kw in title for kw in
                   ("polkit", "pkexec", "authentication agent",)):
                return True
    except:
        pass

    try:
        pids = subprocess.check_output(
            ["pgrep", "-x", "sudo"],
            text=True, stderr=subprocess.DEVNULL
        ).strip().splitlines()
        for pid in pids:
            pid = pid.strip()
            try:
                wchan = read_sysfs(f"/proc/{pid}/wchan") or ""
                if not any(s in wchan for s in ("tty", "read", "n_tty")):
                    continue
                for fd in os.listdir(f"/proc/{pid}/fd"):
                    try:
                        if os.readlink(f"/proc/{pid}/fd/{fd}") == "/dev/tty":
                            return True
                    except:
                        pass
            except:
                pass
    except:
        pass

    return False


# ── Notifications / DND ────────────────────────────────────
def get_notification_count():
    try:
        c = subprocess.check_output(
            ["swaync-client", "-c"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        return int(c) if c else 0
    except:
        return 0

def get_dnd_state():
    try:
        out = subprocess.check_output(
            ["swaync-client", "-D"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        return out.lower() == "true"
    except:
        return False


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
    album  = get_metadata_safe("album")  or "Unknown Album"

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
        "title": title, "artist": artist, "album": album,
        "position": pos, "length": length,
    }


# ── Temperature ───────────────────────────────────────────
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

    prev_str = read_sysfs(BT_PREV_FILE)
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
    usb_base = "/sys/bus/usb/devices"
    current_count = 0
    if os.path.exists(usb_base):
        for dev in os.listdir(usb_base):
            vendor = read_sysfs(f"{usb_base}/{dev}/idVendor")
            product_class = read_sysfs(f"{usb_base}/{dev}/bDeviceClass")
            if vendor and product_class != "09":
                current_count += 1

    prev_str = read_sysfs(USB_PREV_FILE)
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


def handle_clipboard_flash():
    CLIPBOARD_FLASH_FILE = "/tmp/clipboard_flash"
    CLIPBOARD_LAST_FILE = "/tmp/clipboard_last"
    CLIPBOARD_FLASH_SECS = 2

    try:
        clip_content = subprocess.check_output(
            ["wl-paste", "--no-newline"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except:
        return False, ""

    last_content = ""
    if os.path.exists(CLIPBOARD_LAST_FILE):
        try:
            with open(CLIPBOARD_LAST_FILE, "r") as f:
                last_content = f.read().strip()
        except:
            pass

    if clip_content != last_content:
        try:
            with open(CLIPBOARD_LAST_FILE, "w") as f:
                f.write(clip_content)
            with open(CLIPBOARD_FLASH_FILE, "w") as f:
                f.write(str(int(time.time())))
        except:
            pass

    if os.path.exists(CLIPBOARD_FLASH_FILE):
        try:
            ts = read_sysfs(CLIPBOARD_FLASH_FILE)
            if ts:
                age = int(time.time()) - int(ts)
                if age < CLIPBOARD_FLASH_SECS:
                    return True, "📋"
                else:
                    os.remove(CLIPBOARD_FLASH_FILE)
        except:
            pass

    return False, ""


def get_pomodoro_state():
    POMODORO_FILE = "/tmp/pomodoro_active"
    POMODORO_START_FILE = "/tmp/pomodoro_start"
    POMODORO_DURATION = 25 * 60

    if not os.path.exists(POMODORO_FILE):
        return False, 0, 0, None

    try:
        with open(POMODORO_FILE, "r") as f:
            state_name = f.read().strip() or "focus"
    except:
        return False, 0, 0, None

    try:
        with open(POMODORO_START_FILE, "r") as f:
            start_ts = int(f.read().strip())
    except:
        return False, 0, 0, None

    elapsed = int(time.time()) - start_ts
    remaining = max(0, POMODORO_DURATION - elapsed)
    mins = remaining // 60
    secs = remaining % 60

    if elapsed >= POMODORO_DURATION:
        try:
            os.remove(POMODORO_FILE)
            os.remove(POMODORO_START_FILE)
        except:
            pass
        return False, 0, 0, None

    return True, mins, secs, state_name


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


# ── Uptime / network ──────────────────────────────────────
def get_uptime():
    try:
        with open("/proc/uptime") as f:
            secs = float(f.read().split()[0])
        days  = int(secs // 86400)
        hours = int((secs % 86400) // 3600)
        mins  = int((secs % 3600) // 60)
        if days > 0:
            return f"{days}d {hours}h"
        elif hours > 0:
            return f"{hours}h {mins}m"
        else:
            return f"{mins}m"
    except:
        return "N/A"

def is_metered():
    try:
        out = subprocess.check_output(
            ["nmcli", "-t", "-f", "TYPE,STATE", "connection", "show", "--active"],
            text=True, stderr=subprocess.DEVNULL
        )
        for line in out.splitlines():
            parts = line.strip().split(":")
            if len(parts) >= 2 and parts[1] == "activated":
                if parts[0] in ("gsm", "cdma", "bluetooth", "wifi-p2p"):
                    return True
        out2 = subprocess.check_output(
            ["nmcli", "-t", "-f", "GENERAL.METERED", "device", "show"],
            text=True, stderr=subprocess.DEVNULL
        )
        for line in out2.splitlines():
            if "GENERAL.METERED" in line and "yes" in line.lower():
                return True
    except:
        pass
    return False


# ── State picker ───────────────────────────────────────────
def pick_state(cap, stat, temp_warn, auth_active, flash_active, c_window,
               rec_active, bt_flash, usb_flash, pomo_active, clip_flash,
               hw_alert, notif_count, m, dnd_active):
    if temp_warn:                                   return "temp-warning"
    if auth_active:                                 return "auth-waiting"
    if flash_active:                                return "charging" if stat == "Charging" else "discharging"
    if c_window:                                    return "charging" if stat == "Charging" else "discharging"
    if rec_active:                                  return "screen-recording"
    if bt_flash:                                    return "bt-flash"
    if usb_flash:                                   return "usb-flash"
    if pomo_active:                                 return "pomodoro"
    if clip_flash:                                  return "clipboard-flash"
    if hw_alert:                                    return "hardware-alert"
    if notif_count > 0:                             return "notification"
    if m is not None and m["status"] in ("Playing", "Paused"):
        return "music-paused" if m["status"] == "Paused" else "music"
    if dnd_active:                                  return "dnd"
    return "critical" if (cap < LOW_BAT_THRESHOLD and stat == "Discharging") else (
           "charging" if stat == "Charging" else
           "plugged"  if stat == "Not charging" else
           "full"     if (stat == "Full" or cap >= 100) else
           "discharging")


# ── Click action handlers (shared by island and badge) ────
# `state` is the state currently displayed by the module that was clicked.
# Falls back to the island-style default when the state doesn't map to
# a specific action.

def action_left(state, cap, stat, notif_count, dnd_active, m, auth_active, rec_active):
    """Left-click dispatch for a given state."""
    if state in ("notification", "dnd"):
        subprocess.run(["swaync-client", "-t", "-sw"], stderr=subprocess.DEVNULL)
    elif state in ("music", "music-paused"):
        if m is not None:
            subprocess.run(["playerctl", "play-pause"], stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "-RTMIN+8", "waybar"], stderr=subprocess.DEVNULL)
        else:
            subprocess.run(["swaync-client", "-t", "-sw"], stderr=subprocess.DEVNULL)
    elif state == "screen-recording":
        # toggle recording via the user's keybind-style stop script
        subprocess.run(["pkill", "-x", "gpu-screen-recor"], stderr=subprocess.DEVNULL)
    elif state == "pomodoro":
        # no default action — leave the pomodoro running
        pass
    elif state == "auth-waiting":
        subprocess.run(["swaync-client", "-t", "-sw"], stderr=subprocess.DEVNULL)
    elif state == "critical":
        # open a power/status dialog? fall back to the notification panel
        subprocess.run(["swaync-client", "-t", "-sw"], stderr=subprocess.DEVNULL)
    else:
        # battery / flashes / idle: open notification panel (matches island default)
        subprocess.run(["swaync-client", "-t", "-sw"], stderr=subprocess.DEVNULL)

def action_right(state, cap, stat, notif_count, dnd_active, m):
    """Right-click dispatch for a given state."""
    if state in ("notification", "dnd"):
        subprocess.run(["swaync-client", "-d", "-sw"], stderr=subprocess.DEVNULL)
    elif state in ("music", "music-paused"):
        if m is not None:
            subprocess.run(["playerctl", "next"], stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "-RTMIN+8", "waybar"], stderr=subprocess.DEVNULL)
        else:
            subprocess.run(["swaync-client", "-d", "-sw"], stderr=subprocess.DEVNULL)
    elif state == "screen-recording":
        subprocess.run(["pkill", "-x", "gpu-screen-recor"], stderr=subprocess.DEVNULL)
    elif state == "pomodoro":
        pass
    else:
        subprocess.run(["swaync-client", "-d", "-sw"], stderr=subprocess.DEVNULL)

def action_scroll(state, direction, m):
    """direction: +1 for up, -1 for down. Only meaningful for music."""
    if state in ("music", "music-paused") and m is not None:
        step = "+5" if direction > 0 else "-5"
        subprocess.run(["playerctl", "position", f"5{step[0]}"], stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-RTMIN+8", "waybar"], stderr=subprocess.DEVNULL)


# ── Main ───────────────────────────────────────────────────
def main():
    cap, stat, volt, watt, time_str     = get_battery_info()
    flash_active, flash_icon, c_window  = handle_flash(stat, cap)
    hw_alert                            = is_hardware_active()
    notif_count                         = get_notification_count()
    dnd_active                          = get_dnd_state()
    m                                   = get_music_data()
    auth_active                         = is_auth_active()
    cpu_temp, gpu_temp                  = get_temps()
    temp_warn, temp_msg                 = check_temp_warning(cpu_temp, gpu_temp)
    bt_flash, bt_icon                   = handle_bt_flash()
    usb_flash, usb_icon                 = handle_usb_flash()
    clip_flash, clip_icon               = handle_clipboard_flash()
    pomo_active, pomo_mins, pomo_secs, pomo_state = get_pomodoro_state()
    rec_active, rec_duration            = get_screen_recording()
    uptime_str                          = get_uptime()
    metered                             = is_metered()

    bat_icon  = "󰁅"
    bat_state = "discharging"
    if stat == "Full" or cap >= 100:
        bat_icon, bat_state = "󰄬", "full"
    elif stat == "Charging":
        bat_icon, bat_state = "󱐋", "charging"
    elif stat == "Not charging":
        bat_icon, bat_state = "󰐧", "plugged"
    elif cap < LOW_BAT_THRESHOLD:
        bat_icon, bat_state = "󰁃", "critical"

    time_label = "Time to full" if stat == "Charging" else "Time remaining"

    def split_text(icon, left, right, alpha=None):
        a = f" alpha='{alpha}'" if alpha else ""
        right_part = (
            f" <span font_family='Monaspace Krypton'{a}>{right}</span>"
            if right else ""
        )
        return (
            f"{icon} "
            f"<span font_family='Monaspace Krypton'{a}>{left}</span>"
            f"{right_part}"
        )

    _bl, _br    = make_bar(cap * BAR_WIDTH_COMPACT / 100.0, BAR_WIDTH_COMPACT)
    _full_l, _full_r = make_bar(BAR_WIDTH_COMPACT, BAR_WIDTH_COMPACT)
    _empty_l, _empty_r = make_bar(0, BAR_WIDTH_COMPACT)
    bat_text    = split_text(bat_icon, _bl, _br)

    if temp_warn:
        blink        = (time.time() % 0.75) < 0.5
        _tl, _tr     = make_bar(BAR_WIDTH_COMPACT if blink else 0, BAR_WIDTH_COMPACT)
        display_text = split_text("󱃃", _tl, _tr)
        state        = "temp-warning"
        tooltip_text = tt_temp(temp_msg, cap, stat, uptime_str, metered)

    elif auth_active:
        display_text = split_text("󰌾", _empty_l, _empty_r)
        state        = "auth-waiting"
        tooltip_text = tt_auth(cap, stat, uptime_str, metered)

    elif flash_active:
        display_text = split_text(flash_icon, _full_l, _full_r)
        state        = bat_state
        tooltip_text = (tt_charger_plug(cap, stat, uptime_str, metered)
                        if "󱐋" in flash_icon
                        else tt_charger_unplug(cap, stat, uptime_str, metered))

    elif c_window:
        display_text = bat_text
        state        = bat_state
        tooltip_text = tt_battery(stat, cap, time_label, time_str, uptime_str, metered)

    elif rec_active:
        dur_str      = f" {rec_duration}" if rec_duration else ""
        display_text = split_text(f"󰹑{dur_str}", _full_l, _full_r)
        state        = "screen-recording"
        tooltip_text = tt_recording(rec_duration, cap, stat, uptime_str, metered)

    elif bt_flash:
        display_text = split_text(bt_icon, _full_l, _full_r)
        state        = "bt-flash"
        tooltip_text = tt_bt(bt_icon, cap, stat, uptime_str, metered)

    elif usb_flash:
        display_text = split_text(usb_icon, _full_l, _full_r)
        state        = "usb-flash"
        tooltip_text = tt_usb(usb_icon, cap, stat, uptime_str, metered)

    elif pomo_active:
        pomo_str     = f"{pomo_mins}:{pomo_secs:02d}"
        _pl, _pr     = make_bar(
            (25*60 - (pomo_mins*60 + pomo_secs)) * BAR_WIDTH_COMPACT / (25*60),
            BAR_WIDTH_COMPACT
        )
        display_text = split_text(f"󰅐 {pomo_str}", _pl, _pr)
        state        = "pomodoro"
        tooltip_text = tt_pomodoro(pomo_mins, pomo_secs, cap, stat, uptime_str, metered)

    elif clip_flash:
        display_text = split_text(clip_icon, _full_l, _full_r)
        state        = "clipboard-flash"
        tooltip_text = tt_clipboard(cap, stat, uptime_str, metered)

    elif hw_alert:
        duration     = get_recording_duration()
        dur_str      = f" {duration}" if duration else ""
        display_text = split_text(f"󰍬{dur_str}", _full_l, _full_r)
        state        = "hardware-alert"
        tooltip_text = tt_hardware(duration, cap, stat, uptime_str, metered)

    elif notif_count > 0:
        NOTIF_MAX_HALF  = 5
        half_filled     = min(notif_count, NOTIF_MAX_HALF)
        phase           = time.time() % 0.45
        bars_on         = phase < 0.3
        lf              = half_filled if bars_on else 0
        _nl, _nr        = make_bar(lf, BAR_WIDTH_COMPACT)
        display_text    = split_text("󰂚", _nl, _nr)
        state           = "notification"
        tooltip_text    = tt_notification(notif_count, cap, stat, uptime_str, metered)

    elif m is not None and m["status"] in ("Playing", "Paused"):
        is_paused    = m["status"] == "Paused"
        state        = "music-paused" if is_paused else "music"
        music_icon   = "󰏤" if is_paused else "󰝚"
        pct          = min(1.0, max(0.0, m["position"] / m["length"])) if m["length"] > 0 else 0.0
        _ml, _mr     = make_bar(pct * BAR_WIDTH_COMPACT, BAR_WIDTH_COMPACT)
        display_text = split_text(music_icon, _ml, _mr)
        tooltip_text = tt_music(m, cap, stat, uptime_str, metered)

    elif dnd_active:
        _dl, _dr     = make_bar(cap * BAR_WIDTH_COMPACT / 100.0, BAR_WIDTH_COMPACT)
        display_text = split_text("󰂛", _dl, _dr, alpha="55%")
        state        = "dnd"
        tooltip_text = tt_dnd(notif_count, cap, stat, uptime_str, metered)

    else:
        display_text = bat_text
        state        = bat_state
        tooltip_text = tt_battery(stat, cap, time_label, time_str, uptime_str, metered)

    output = {"text": display_text, "class": state, "tooltip": tooltip_text}
    print(json.dumps(output))


# ── Argument dispatch ──────────────────────────────────────
if len(sys.argv) > 1:
    arg = sys.argv[1]

    # ── Resolve current state once, so click actions know what to do ──
    def current_state():
        cap, stat, _, _, _  = get_battery_info()
        flash_active, _, c_window = handle_flash(stat, cap)
        hw_alert            = is_hardware_active()
        notif_count         = get_notification_count()
        dnd_active          = get_dnd_state()
        m                   = get_music_data()
        auth_active         = is_auth_active()
        cpu_temp, gpu_temp  = get_temps()
        temp_warn, _        = check_temp_warning(cpu_temp, gpu_temp)
        bt_flash, _         = handle_bt_flash()
        usb_flash, _        = handle_usb_flash()
        clip_flash, _       = handle_clipboard_flash()
        pomo_active, _, _, _ = get_pomodoro_state()
        rec_active, _       = get_screen_recording()
        return (cap, stat, notif_count, dnd_active, m, auth_active,
                rec_active, temp_warn, flash_active, c_window,
                bt_flash, usb_flash, clip_flash, pomo_active, hw_alert)

    def resolve_state():
        (cap, stat, notif_count, dnd_active, m, auth_active,
         rec_active, temp_warn, flash_active, c_window,
         bt_flash, usb_flash, clip_flash, pomo_active, hw_alert) = current_state()
        return pick_state(cap, stat, temp_warn, auth_active, flash_active,
                          c_window, rec_active, bt_flash, usb_flash,
                          pomo_active, clip_flash, hw_alert, notif_count,
                          m, dnd_active), cap, stat, notif_count, dnd_active, m, auth_active, rec_active

    # ── Unified click actions ──
    # These dispatch based on whatever state the *clicked* module is showing.
    # The island and the badge share the same handlers, so clicking either
    # produces the same result for a given state.

    def click_left():
        state, cap, stat, notif_count, dnd_active, m, auth_active, rec_active = resolve_state()
        action_left(state, cap, stat, notif_count, dnd_active, m, auth_active, rec_active)

    def click_right():
        state, cap, stat, notif_count, dnd_active, m, auth_active, rec_active = resolve_state()
        action_right(state, cap, stat, notif_count, dnd_active, m)

    def click_scroll(direction):
        state, cap, stat, notif_count, dnd_active, m, auth_active, rec_active = resolve_state()
        action_scroll(state, direction, m)

    # ── Arg branches ──
    if arg == "--play-pause":
        click_left()
        sys.exit(0)

    if arg == "--next":
        click_right()
        sys.exit(0)

    if arg == "--seek-forward":
        click_scroll(+1)
        sys.exit(0)

    if arg == "--seek-back":
        click_scroll(-1)
        sys.exit(0)

    if arg == "--extra":
        cap, stat, _, _, _          = get_battery_info()
        uptime_str                  = get_uptime()
        metered                     = is_metered()
        flash_active, _, c_window   = handle_flash(stat, cap)
        hw_alert                    = is_hardware_active()
        notif_count                 = get_notification_count()
        dnd_active                  = get_dnd_state()
        m                           = get_music_data()
        auth_active                 = is_auth_active()
        cpu_temp, gpu_temp          = get_temps()
        temp_warn, temp_msg         = check_temp_warning(cpu_temp, gpu_temp)
        bt_flash, bt_icon           = handle_bt_flash()
        usb_flash, usb_icon         = handle_usb_flash()
        clip_flash, clip_icon       = handle_clipboard_flash()
        pomo_active, _, _, _        = get_pomodoro_state()
        rec_active, _               = get_screen_recording()

        flash_age = None
        for fpath in (BT_FLASH_FILE, USB_FLASH_FILE):
            if os.path.exists(fpath):
                try:
                    ts = int(read_sysfs(fpath).split()[0])
                    age = time.time() - ts
                    if flash_age is None or age < flash_age:
                        flash_age = age
                except:
                    pass
        if os.path.exists("/tmp/clipboard_flash"):
            try:
                ts = int(read_sysfs("/tmp/clipboard_flash"))
                age = time.time() - ts
                if flash_age is None or age < flash_age:
                    flash_age = age
            except:
                pass

        island = pick_state(
            cap, stat, temp_warn, auth_active, flash_active, c_window,
            rec_active, bt_flash, usb_flash, pomo_active, clip_flash,
            hw_alert, notif_count, m, dnd_active,
        )

        ctx = {
            "island":      island,
            "stat":        stat,
            "cap":         cap,
            "notif_count": notif_count,
            "dnd_active":  dnd_active,
            "m":           m,
            "rec_active":  rec_active,
            "pomo_active": pomo_active,
            "hw_alert":    hw_alert,
            "auth_active": auth_active,
            "temp_warn":   temp_warn,
            "flash_age":   flash_age,
        }

        candidates = [
            ("temp-warning",     temp_warn,                                             "󱃃", lambda: 1.0,
                tt_temp(temp_msg, cap, stat, uptime_str, metered, BADGE_CELLS)),
            ("auth-waiting",     auth_active,                                           "󰌾", lambda: 1.0,
                tt_auth(cap, stat, uptime_str, metered, BADGE_CELLS)),
            ("critical",         cap < LOW_BAT_THRESHOLD and stat == "Discharging",     "󰁃",
                lambda: max(0.0, cap / LOW_BAT_THRESHOLD),
                tt_critical(cap, stat, uptime_str, metered, BADGE_CELLS)),
            ("screen-recording", rec_active,                                            "󰹑", lambda: 1.0,
                tt_recording("", cap, stat, uptime_str, metered, BADGE_CELLS)),
            ("hardware-alert",   hw_alert,                                              "󰍬", lambda: 1.0,
                tt_hardware("", cap, stat, uptime_str, metered, BADGE_CELLS)),
            ("bt-flash",         bt_flash,                                              bt_icon, None,
                tt_bt(bt_icon, cap, stat, uptime_str, metered, BADGE_CELLS)),
            ("usb-flash",        usb_flash,                                             usb_icon, None,
                tt_usb(usb_icon, cap, stat, uptime_str, metered, BADGE_CELLS)),
            ("clipboard-flash",  clip_flash,                                            "󰅇", None,
                tt_clipboard(cap, stat, uptime_str, metered, BADGE_CELLS)),
            ("notification",     notif_count > 0,                                       "󰂚",
                lambda: min(notif_count, 8) / 8.0,
                tt_notification(notif_count, cap, stat, uptime_str, metered, BADGE_CELLS)),
            ("pomodoro",         pomo_active,                                           "󰅐", None,
                tt_pomodoro(*get_pomodoro_state()[1:3], cap, stat, uptime_str, metered, BADGE_CELLS)),
            ("music",            m is not None and m["status"] in ("Playing", "Paused"), "󰝚",
                lambda: (min(1.0, m["position"] / m["length"])
                         if m and m["length"] > 0 else 0.0),
                tt_music(m, cap, stat, uptime_str, metered, BADGE_CELLS) if m else ""),
            ("dnd",              dnd_active,                                            "󰂛", None,
                tt_dnd(notif_count, cap, stat, uptime_str, metered, BADGE_CELLS)),
            ("charging",         stat == "Charging",                                    "󱐋",
                lambda: cap / 100.0,
                tt_battery(stat, cap, "Time to full", "", uptime_str, metered, BADGE_CELLS)),
        ]

        best = None
        best_score = 0
        for name, active, icon, fill_fn, tip in candidates:
            if not active:
                continue
            s = contextual_score(name, ctx)
            if s > best_score:
                best_score = s
                best = (name, icon, fill_fn, tip)

        if best is None:
            empty, _ = make_bar(0, BADGE_CELLS)
            text = f"\u00a0 {empty}"
            cls  = "idle"
            tip  = ""
        else:
            name, icon, fill_fn, tip = best
            fill = fill_fn() if fill_fn else 1.0
            bar, _ = make_bar(fill * BADGE_CELLS, BADGE_CELLS)
            text = f"{icon} {bar}"
            cls  = name

        print(json.dumps({
            "text":    text,
            "class":   cls,
            "tooltip": tip,
        }))
        sys.exit(0)


if __name__ == "__main__":
    main()
