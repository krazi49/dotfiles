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
CPU_TEMP_WARN      = 90   # °C
GPU_TEMP_WARN      = 100  # °C
BT_FLASH_FILE      = "/tmp/waybar_adaptive_bt_flash"
BT_PREV_FILE       = "/tmp/waybar_adaptive_bt_prev"
BT_FLASH_SECS      = 2
SCREENREC_START    = "/tmp/waybar_adaptive_screenrec"
USB_FLASH_FILE     = "/tmp/waybar_adaptive_usb_flash"
USB_PREV_FILE      = "/tmp/waybar_adaptive_usb_prev"
USB_FLASH_SECS     = 2

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
# Left column (dots 1,2,3,7) fills top→bottom first, then right column (4,5,6,8).
BRAILLE_STEPS = ["⠀", "⠁", "⠃", "⠇", "⡇", "⡗", "⡟", "⡿", "⣿"]
BRAILLE_SUB   = 8

# Base urgency: how loudly does this state want to be seen?
# 100 = critical, 50 = alerting, 30 = activity, 10 = ambient info
BASE_URGENCY = {
    "temp-warning":     100,
    "critical":          90,   # battery < 15%, discharging
    "auth-waiting":      85,   # you literally cannot proceed
    "screen-recording":  60,
    "hardware-alert":    55,   # mic/cam on
    "bt-flash":          45,   # transient, attention-worthy when it fires
    "usb-flash":         45,
    "clipboard-flash":   35,
    "notification":      40,
    "pomodoro":          30,
    "music":             20,
    "dnd":               15,
    "charging":          15,
    "full":              10,
    "plugged":           10,
    "discharging":        5,   # ambient — it's the default
}


def contextual_score(state, ctx):
    """
    Base urgency adjusted for what's happening right now.

    ctx keys:
      island           — the state the main island is currently showing
      stat             — battery status string
      cap              — battery percent
      notif_count      — unread notifications
      dnd_active       — bool
      m                — music dict or None
      rec_active       — bool
      pomo_active      — bool
      hw_alert         — bool
      auth_active      — bool
      temp_warn        — bool
      flash_age        — seconds since the current transient flash fired, or None
    """
    score = BASE_URGENCY.get(state, 0)

    # ── Never let the badge duplicate the island ───────────
    if state == ctx["island"]:
        return -1

    # ── Ambient states shrink further when something loud is up ──
    loud_active = ctx["auth_active"] or ctx["temp_warn"] or ctx["rec_active"]

    if state in ("music", "dnd", "charging", "full", "plugged", "discharging"):
        if loud_active:
            score -= 20     # don't clutter the badge while you're busy
        if ctx["island"] in ("temp-warning", "auth-waiting", "screen-recording"):
            score -= 15     # the island already owns the stage

    # ── Notification handling ──────────────────────────────
    if state == "notification":
        if ctx["dnd_active"]:
            score -= 25     # DND means "don't bother me" — mute the count
        if ctx["m"] is not None and ctx["m"]["status"] == "Playing":
            score -= 10     # music playing = you're probably fine
        if ctx["rec_active"] or ctx["auth_active"]:
            score += 10     # but if something's live, still worth flagging
        if ctx["notif_count"] >= 5:
            score += 15     # a pile-up is louder than one

    # ── DND itself ─────────────────────────────────────────
    if state == "dnd":
        # DND only matters if something would otherwise be shown
        if ctx["notif_count"] == 0 and not loud_active:
            score -= 30     # nothing to suppress = don't advertise it

    # ── Music ──────────────────────────────────────────────
    if state == "music":
        if ctx["m"] and ctx["m"]["status"] == "Paused":
            score -= 15     # paused music is quiet context, not activity
        if ctx["pomo_active"]:
            score -= 10     # pomodoro takes precedence visually

    # ── Transient flashes: novelty boost ───────────────────
    if state in ("bt-flash", "usb-flash", "clipboard-flash"):
        age = ctx.get("flash_age")
        if age is not None:
            if age < 1.0:
                score += 40     # just happened — shout about it
            elif age < 1.5:
                score += 15     # still fresh
            # else: fades back to base urgency

    # ── Recording / mic ────────────────────────────────────
    if state == "hardware-alert":
        # hardware-alert is only interesting if the island isn't already
        # shouting something louder
        if ctx["island"] in ("temp-warning", "screen-recording", "auth-waiting"):
            score -= 20

    # ── Charging ───────────────────────────────────────────
    if state == "charging":
        # charging is worth showing only when the battery was recently low
        # or something else already surfaced it — otherwise it's ambient
        if ctx["cap"] >= 80:
            score -= 10

    # ── Auth ───────────────────────────────────────────────
    if state == "auth-waiting":
        # auth is critical, but not if the island is *already* showing it
        # (handled above), and not if temp is screaming
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
    """
    Braille sub-cell progress bar.

    `filled` may be a float; it is multiplied by BRAILLE_SUB to get
    sub-cell resolution (8 sub-positions per cell).

    The returned string always occupies exactly `total` glyph cells,
    so the bar's width doesn't shift as the fill level changes.

    Returns (left, right) — `right` is always empty, kept for signature
    compatibility with the old `make_bar`.
    """
    filled = max(0.0, min(float(filled), float(total)))

    sub_filled = int(round(filled * BRAILLE_SUB))
    full_cells, rem = divmod(sub_filled, BRAILLE_SUB)

    # guard against rounding at the ends
    full_cells = max(0, min(full_cells, int(total)))

    empty_cells = int(total) - full_cells - (1 if rem else 0)
    empty_cells = max(0, empty_cells)

    on  = "⣿" * full_cells
    mid = BRAILLE_STEPS[rem] if rem else ""
    off = (
        f"<span alpha='15%'>{'⣿' * empty_cells}</span>"
        if empty_cells > 0 else ""
    )

    return on + mid + off, ""

def make_bar_str(filled, total):
    """Braille bar for tooltips — same visual language as the island bar."""
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

def live_activity_tooltip(activity_lines, cap, stat):
    bat_line = f"<b>Battery:</b> {cap}%"
    return f"{activity_lines}\n<span alpha='40%'>------</span>\n{bat_line}"


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
    # GUI polkit dialog
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

    # Terminal sudo waiting for password
    try:
        pids = subprocess.check_output(
            ["pgrep", "-x", "sudo"],
            text=True, stderr=subprocess.DEVNULL
        ).strip().splitlines()
        for pid in pids:
            pid = pid.strip()
            try:
                # wchan tells us what the kernel is waiting on:
                # tty read = still prompting, wait4 = already running the command
                wchan = read_sysfs(f"/proc/{pid}/wchan") or ""
                if not any(s in wchan for s in ("tty", "read", "n_tty")):
                    continue
                # double-check /dev/tty is actually open
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
    """Detects USB device plug/unplug. Returns (flash_active, flash_icon)."""
    usb_base = "/sys/bus/usb/devices"
    current_count = 0
    if os.path.exists(usb_base):
        for dev in os.listdir(usb_base):
            # count only real devices (have idVendor), skip hubs/root hubs
            vendor = read_sysfs(f"{usb_base}/{dev}/idVendor")
            product_class = read_sysfs(f"{usb_base}/{dev}/bDeviceClass")
            if vendor and product_class != "09":  # 09 = hub
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
    """Detects clipboard changes. Returns (flash_active, flash_icon)."""
    CLIPBOARD_FLASH_FILE = "/tmp/clipboard_flash"
    CLIPBOARD_LAST_FILE = "/tmp/clipboard_last"
    CLIPBOARD_FLASH_SECS = 2

    try:
        # Get clipboard content (without trailing newline)
        clip_content = subprocess.check_output(
            ["wl-paste", "--no-newline"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except:
        # If wl-paste fails, return no flash
        return False, ""

    # Read last known content
    last_content = ""
    if os.path.exists(CLIPBOARD_LAST_FILE):
        try:
            with open(CLIPBOARD_LAST_FILE, "r") as f:
                last_content = f.read().strip()
        except:
            pass

    # If content changed, update last and set flash timestamp
    if clip_content != last_content:
        try:
            with open(CLIPBOARD_LAST_FILE, "w") as f:
                f.write(clip_content)
            with open(CLIPBOARD_FLASH_FILE, "w") as f:
                f.write(str(int(time.time())))
        except:
            pass

    # Check if flash is still active
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
    """Returns (is_active, remaining_minutes, remaining_seconds, state_name)."""
    POMODORO_FILE = "/tmp/pomodoro_active"
    POMODORO_START_FILE = "/tmp/pomodoro_start"
    POMODORO_DURATION = 25 * 60  # 25 minutes in seconds

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
        # Timer expired — clean up
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
    """Return the single highest-priority state name, matching main()'s chain."""
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

    # resolve battery icon + css state
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

    extra_lines = []
    if metered:
        extra_lines.append("<b>Network:</b> metered connection")
    if uptime_str:
        extra_lines.append(f"<b>Uptime:</b> {uptime_str}")

    bat_tooltip = (
        f"<b>Status:</b> {stat}\n"
        f"<b>Charge:</b> {cap}%\n"
        f"<b>Voltage:</b> {volt}\n"
        f"<b>Power:</b> {watt}\n"
        f"<b>{time_label}:</b> {time_str}"
    )
    if extra_lines:
        bat_tooltip += "\n<span alpha='40%'>·  ·  ·  ·  ·</span>\n" + "\n".join(extra_lines)

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
    low_battery = cap < LOW_BAT_THRESHOLD and stat == "Discharging"

    # ── Priority chain ─────────────────────────────────────
    #  0  temperature warning
    #  1  auth prompt
    #  2  low battery / feral critical
    #  3  charger flash (2s)
    #  4  charger window (5s)
    #  5  screen recording
    #  6  bt flash (2s)
    #  7  usb flash (2s)
    #  8  pomodoro timer
    #  9  clipboard flash
    # 10  cam/mic active
    # 11  notifications
    # 12  music
    # 13  DND
    # 14  default battery

    if temp_warn:
        blink        = (time.time() % 0.75) < 0.5
        _tl, _tr     = make_bar(BAR_WIDTH_COMPACT if blink else 0, BAR_WIDTH_COMPACT)
        display_text = split_text("󱃃", _tl, _tr)
        state        = "temp-warning"
        tooltip      = live_activity_tooltip(f"<b>󱃃 High temperature</b>\n{temp_msg}", cap, stat)

    elif auth_active:
        display_text = split_text("󰌾", _empty_l, _empty_r)
        state        = "auth-waiting"
        tooltip      = live_activity_tooltip("<b>Waiting for password</b>", cap, stat)

    elif flash_active:
        display_text = split_text(flash_icon, _full_l, _full_r)
        state        = bat_state
        tooltip      = bat_tooltip

    elif c_window:
        display_text = bat_text
        state        = bat_state
        tooltip      = bat_tooltip

    elif rec_active:
        dur_str      = f" {rec_duration}" if rec_duration else ""
        display_text = split_text(f"󰹑{dur_str}", _full_l, _full_r)
        state        = "screen-recording"
        tooltip      = live_activity_tooltip("<b>󰹑  screen recording</b>", cap, stat)

    elif bt_flash:
        display_text = split_text(bt_icon, _full_l, _full_r)
        state        = "bt-flash"
        tooltip      = bat_tooltip

    elif usb_flash:
        display_text = split_text(usb_icon, _full_l, _full_r)
        state        = "usb-flash"
        tooltip      = live_activity_tooltip("<b>USB device changed</b>", cap, stat)

    elif pomo_active:
        pomo_str     = f"{pomo_mins}:{pomo_secs:02d}"
        _pl, _pr     = make_bar(
            (25*60 - (pomo_mins*60 + pomo_secs)) * BAR_WIDTH_COMPACT / (25*60),
            BAR_WIDTH_COMPACT
        )
        display_text = split_text(f"󰅐 {pomo_str}", _pl, _pr)
        state        = "pomodoro"
        tooltip      = live_activity_tooltip(f"<b>󰅐  Pomodoro</b> — focus for {pomo_mins}:{pomo_secs:02d} left", cap, stat)

    elif clip_flash:
        display_text = split_text(clip_icon, _full_l, _full_r)
        state        = "clipboard-flash"
        tooltip      = live_activity_tooltip("<b>📋  clipboard updated</b>", cap, stat)

    elif hw_alert:
        duration     = get_recording_duration()
        dur_str      = f" {duration}" if duration else ""
        display_text = split_text(f"󰍬{dur_str}", _full_l, _full_r)
        state        = "hardware-alert"
        tooltip      = live_activity_tooltip("<b>󰍬  recording</b>", cap, stat)

    elif notif_count > 0:
        NOTIF_MAX_HALF  = 5
        half_filled     = min(notif_count, NOTIF_MAX_HALF)
        phase           = time.time() % 0.45
        bars_on         = phase < 0.3
        lf              = half_filled if bars_on else 0
        _nl, _nr        = make_bar(lf, BAR_WIDTH_COMPACT)
        display_text    = split_text("󰂚", _nl, _nr)
        state           = "notification"
        plural          = "s" if notif_count != 1 else ""
        tooltip         = live_activity_tooltip(
            f"<b>{notif_count} notification{plural}</b>", cap, stat
        )

    elif m is not None and m["status"] in ("Playing", "Paused"):
        is_paused    = m["status"] == "Paused"
        state        = "music-paused" if is_paused else "music"
        music_icon   = "󰏤" if is_paused else "󰝚"
        pct          = min(1.0, max(0.0, m["position"] / m["length"])) if m["length"] > 0 else 0.0
        _ml, _mr     = make_bar(pct * BAR_WIDTH_COMPACT, BAR_WIDTH_COMPACT)
        display_text = split_text(music_icon, _ml, _mr)
        tooltip_bar  = make_bar_str(int(pct * 30), 30)
        tooltip      = live_activity_tooltip(
            f"<b>{html.escape(m['title'])}</b>\n"
            f"{html.escape(m['artist'])}\n"
            f"{html.escape(m['album'])}\n\n"
            f"<span font_family=\"Monaspace Krypton\" font_features=\"tnum\">"
            f"{fmt_time(m['position'])} {tooltip_bar} {fmt_time(m['length'])}</span>",
            cap, stat
        )

    elif dnd_active:
        _dl, _dr     = make_bar(cap * BAR_WIDTH_COMPACT / 100.0, BAR_WIDTH_COMPACT)
        display_text = split_text("󰂛", _dl, _dr, alpha="55%")
        state        = "dnd"
        tooltip      = live_activity_tooltip("<b>Do not disturb</b>", cap, stat)

    else:
        display_text = bat_text
        state        = bat_state
        tooltip      = bat_tooltip

    output = {"text": display_text, "class": state, "tooltip": tooltip}
    print(json.dumps(output))


# ── Argument dispatch ──────────────────────────────────────
# NOTE: lives at the bottom so every helper is defined before we dispatch.
if len(sys.argv) > 1:
    arg = sys.argv[1]

    if arg == "--play-pause":
        # Check for notifications first - if any exist, open swaync
        try:
            notif_count = subprocess.check_output(
                ["swaync-client", "-c"], text=True, stderr=subprocess.DEVNULL
            ).strip()
            notif_count = int(notif_count) if notif_count else 0
        except:
            notif_count = 0

        if notif_count > 0:
            subprocess.run(["swaync-client", "-t", "-sw"], stderr=subprocess.DEVNULL)
        else:
            try:
                status = subprocess.check_output(
                    ["playerctl", "status"], text=True, stderr=subprocess.DEVNULL
                ).strip()
                is_music = status in ("Playing", "Paused")
            except:
                is_music = False
            if is_music:
                subprocess.run(["playerctl", "play-pause"], stderr=subprocess.DEVNULL)
                subprocess.run(["pkill", "-RTMIN+8", "waybar"], stderr=subprocess.DEVNULL)
            else:
                subprocess.run(["swaync-client", "-t", "-sw"], stderr=subprocess.DEVNULL)
        sys.exit(0)

    if arg == "--next":
        try:
            status = subprocess.check_output(
                ["playerctl", "status"], text=True, stderr=subprocess.DEVNULL
            ).strip()
            if status in ("Playing", "Paused"):
                subprocess.run(["playerctl", "next"], stderr=subprocess.DEVNULL)
        except:
            pass
        subprocess.run(["pkill", "-RTMIN+8", "waybar"], stderr=subprocess.DEVNULL)
        sys.exit(0)

    if arg == "--seek-forward":
        try:
            status = subprocess.check_output(
                ["playerctl", "status"], text=True, stderr=subprocess.DEVNULL
            ).strip()
            if status in ("Playing", "Paused"):
                subprocess.run(["playerctl", "position", "5+"], stderr=subprocess.DEVNULL)
        except:
            pass
        subprocess.run(["pkill", "-RTMIN+8", "waybar"], stderr=subprocess.DEVNULL)
        sys.exit(0)

    if arg == "--seek-back":
        try:
            status = subprocess.check_output(
                ["playerctl", "status"], text=True, stderr=subprocess.DEVNULL
            ).strip()
            if status in ("Playing", "Paused"):
                subprocess.run(["playerctl", "position", "5-"], stderr=subprocess.DEVNULL)
        except:
            pass
        subprocess.run(["pkill", "-RTMIN+8", "waybar"], stderr=subprocess.DEVNULL)
        sys.exit(0)

    if arg == "--extra":
        # ── gather the same signals main() uses ──
        cap, stat, _, _, _          = get_battery_info()
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

        # ── how old is the current transient flash? ──
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

        # ── what is the island showing right now? ──
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

        # ── candidate pool with icons + tooltips ──
        candidates = [
            ("temp-warning",     temp_warn,                                             "󱃃", f"<b>High temperature</b>\n{temp_msg}"),
            ("auth-waiting",     auth_active,                                           "󰌾", "<b>Waiting for password</b>"),
            ("critical",         cap < LOW_BAT_THRESHOLD and stat == "Discharging",     "󰁃", "<b>Battery low</b>"),
            ("screen-recording", rec_active,                                            "󰹑", "<b>Screen recording</b>"),
            ("hardware-alert",   hw_alert,                                              "󰍬", "<b>Mic or camera active</b>"),
            ("bt-flash",         bt_flash,                                              bt_icon, "<b>Bluetooth device changed</b>"),
            ("usb-flash",        usb_flash,                                             usb_icon, "<b>USB device changed</b>"),
            ("clipboard-flash",  clip_flash,                                            "📋", "<b>Clipboard updated</b>"),
            ("notification",     notif_count > 0,                                       "󰂚", f"<b>{notif_count} notification{'s' if notif_count != 1 else ''}</b>"),
            ("pomodoro",         pomo_active,                                           "󰅐", "<b>Pomodoro running</b>"),
            ("music",            m is not None and m["status"] in ("Playing", "Paused"), "󰝚", "<b>Music playing</b>"),
            ("dnd",              dnd_active,                                            "󰂛", "<b>Do not disturb</b>"),
            ("charging",         stat == "Charging",                                    "󱐋", "<b>Charging</b>"),
        ]

        # ── score them, pick the winner ──
        best = None
        best_score = 0
        for name, active, icon, tip in candidates:
            if not active:
                continue
            s = contextual_score(name, ctx)
            if s > best_score:
                best_score = s
                best = (name, icon, tip)

        if best is None:
            # Emit a zero-width NBSP so Waybar keeps the widget mounted.
            # The `.idle` CSS collapses padding/margin/opacity to zero.
            print(json.dumps({
                "text":    "<span alpha='0%'>\u00a0</span>",
                "class":   "idle",
                "tooltip": "",
            }))
        else:
            name, icon, tip = best
            print(json.dumps({"text": icon, "class": name, "tooltip": tip}))
        sys.exit(0)


if __name__ == "__main__":
    main()
