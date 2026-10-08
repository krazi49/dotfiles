#!/usr/bin/env python3
import json
import subprocess
import sys
import os
import time
import html
from dataclasses import dataclass, field
from typing import Optional

# ── Display ────────────────────────────────────────────────
BAR_WIDTH_COMPACT   = 7          # island bar, in braille cells
BADGE_CELLS         = 2          # badge tooltip bar
BAR_FONT            = "Monaspace Krypton"
BAR_DIM_ALPHA       = "25%"      # empty part of the bar
DND_ALPHA           = "55%"      # bar/number alpha while do-not-disturb is shown
NUM_GAP             = "   "      # space between bar and numbers
IDLE_BADGE_TEXT     = "\u00a0"   # badge text when nothing is active

# ── Layout templates ───────────────────────────────────────
# island keys: {icon} {bar} {gap} {value}   ({gap} is NUM_GAP, empty if bar or value is empty)
# badge  keys: {icon} {value} {more}        ({more} is the overflow marker)
# a bad template (unknown key etc.) silently falls back to the default
ISLAND_LAYOUT       = "{icon} {bar}{gap}{value}"
BADGE_LAYOUT        = "{icon} {value}{more}"

# ── Island priority (first active entry wins) ─────────────
# Single source of truth for what the island shows. An entry left out of the
# list is never shown on the island (the plain battery readout is the fallback).
#   charger-flash / charger-window: the brief plug/unplug events
#   critical: battery under LOW_BAT_THRESHOLD while discharging
ISLAND_PRIORITY = [
    "temp-warning",
    "auth-waiting",
    "critical",
    "charger-flash",
    "charger-window",
    "screen-recording",
    "bt-flash",
    "usb-flash",
    "pomodoro",
    "hardware-alert",
    "notification",
    "music",
    "dnd",
]

# ── Idle state (battery fallback, nothing else going on) ───
# the island also gets an "idle" css class in this state, e.g. #custom-island.idle
IDLE_SHOW_PERCENT   = False      # False = icon + bar only
IDLE_SHOW_BAR       = True
IDLE_PERCENT_BELOW  = 30         # show the percentage anyway under this charge
IDLE_ALPHA          = None       # e.g. "70%" to dim the whole island when idle

# ── Badge overflow ─────────────────────────────────────────
BADGE_SHOW_OVERFLOW  = True      # dim "+N" when other states are also active
BADGE_OVERFLOW_FMT   = "+{n}"
BADGE_OVERFLOW_GAP   = " "
BADGE_OVERFLOW_ALPHA = "45%"
BADGE_TT_LIST_OTHERS = True      # "also: ..." line in the badge tooltip

# ── Tooltip ────────────────────────────────────────────────
TT_CHARGING_COLOR   = "#a6e3a1"
TT_LOW_COLOR        = "#f38ba8"
TT_SEPARATOR        = "─" * 13
TT_SHOW_UPTIME      = True
TT_SHOW_METERED     = True
TT_SHOW_POWER       = False      # battery watts / volts in the footer strip
TT_SHOW_TEMPS       = False      # cpu / gpu temps in the footer strip

# ── Feature toggles (False skips the poll entirely) ───────
ENABLED = {
    "temp":          True,
    "auth":          True,
    "recording":     True,
    "hardware":      True,       # pw-dump is the heaviest poll here
    "bluetooth":     True,
    "usb":           True,
    "pomodoro":      True,
    "notifications": True,
    "music":         True,
    "dnd":           True,
    "metered":       True,
}

# ── Thresholds ─────────────────────────────────────────────
LOW_BAT_THRESHOLD   = 15
CPU_TEMP_WARN       = 90
GPU_TEMP_WARN       = 100
POMODORO_DURATION   = 25 * 60

# ── Timing (seconds) ───────────────────────────────────────
CHARGER_FLASH_SECS  = 2
CHARGER_SHOW_SECS   = 5
BT_FLASH_SECS       = 2
USB_FLASH_SECS      = 2
TEMP_BLINK_PERIOD   = 0.75
TEMP_BLINK_ON       = 0.5
NOTIF_BLINK_PERIOD  = 0.45
NOTIF_BLINK_ON      = 0.3
NOTIF_BAR_MAX       = 5          # island bar saturates at this many
NOTIF_TT_MAX        = 8          # tooltip bar saturates at this many

# ── Poll caching (shared by island and badge processes) ───
CACHE_DIR           = "/tmp/waybar_adaptive_cache"
TEMP_CACHE_SECS     = 3
HW_CACHE_SECS       = 2
METERED_CACHE_SECS  = 30
MUSIC_CACHE_SECS    = 0          # 0 = always poll

# ── Actions ────────────────────────────────────────────────
SWAYNC_PANEL_CMD    = ["swaync-client", "-t", "-sw"]
SWAYNC_DND_CMD      = ["swaync-client", "-d", "-sw"]
WAYBAR_SIGNAL       = 8          # RTMIN+N used to refresh the module
SEEK_STEP_SECS      = 5
SCREENREC_PROCESS   = "gpu-screen-recor"

# ── Files ──────────────────────────────────────────────────
FLASH_FILE          = "/tmp/waybar_adaptive_flash"
PREV_STAT_FILE      = "/tmp/waybar_adaptive_prev_stat"
CHARGER_EVENT_FILE  = "/tmp/waybar_adaptive_charger_event"
MIC_START_FILE      = "/tmp/waybar_adaptive_mic_start"
BT_FLASH_FILE       = "/tmp/waybar_adaptive_bt_flash"
BT_PREV_FILE        = "/tmp/waybar_adaptive_bt_prev"
SCREENREC_START     = "/tmp/waybar_adaptive_screenrec"
USB_FLASH_FILE      = "/tmp/waybar_adaptive_usb_flash"
USB_PREV_FILE       = "/tmp/waybar_adaptive_usb_prev"
POMODORO_FILE       = "/tmp/pomodoro_active"
POMODORO_START_FILE = "/tmp/pomodoro_start"

BADGE_ICON = {
    "temp-warning":     "󱃃",
    "auth-waiting":     "󰌾",
    "screen-recording": "󰹑",
    "bt-flash":         "󰂱",
    "usb-flash":        "󰕓",
    "pomodoro":         "󰅐",
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

# Names shown in the badge tooltip's "also:" line.
STATE_LABELS = {
    "temp-warning":     "High temperature",
    "auth-waiting":     "Password prompt",
    "screen-recording": "Screen recording",
    "hardware-alert":   "Mic or camera",
    "bt-flash":         "Bluetooth",
    "usb-flash":        "USB",
    "notification":     "Notifications",
    "pomodoro":         "Pomodoro",
    "music":            "Music",
    "music-paused":     "Music (paused)",
    "dnd":              "Do not disturb",
    "charging":         "Charging",
    "critical":         "Low battery",
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
    "notification":      40,
    "pomodoro":          30,
    "music":             20,
    "music-paused":       5,
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

    if state in ("music", "music-paused", "dnd", "charging", "full", "plugged", "discharging"):
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

    if state in ("music", "music-paused"):
        if ctx["pomo_active"]:
            score -= 10

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
    except OSError:
        return None


def cached(key, ttl, fn):
    """Run fn() at most once per ttl seconds across all processes.
    Result must be JSON-serialisable (tuples come back as lists)."""
    if ttl <= 0:
        return fn()
    path = f"{CACHE_DIR}/{key}.json"
    try:
        if time.time() - os.path.getmtime(path) < ttl:
            with open(path) as f:
                return json.load(f)
    except (OSError, ValueError):
        pass
    val = fn()
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        tmp = f"{path}.{os.getpid()}.tmp"
        with open(tmp, "w") as f:
            json.dump(val, f)
        os.replace(tmp, path)
    except (OSError, TypeError):
        pass
    return val


def make_bar(filled, total, dim_alpha=BAR_DIM_ALPHA):
    """Braille sub-cell progress bar. `filled` and `total` are in cell units."""
    filled = max(0.0, min(float(filled), float(total)))
    sub_filled = int(round(filled * BRAILLE_SUB))
    full_cells, rem = divmod(sub_filled, BRAILLE_SUB)
    full_cells = max(0, min(full_cells, int(total)))
    empty_cells = max(0, int(total) - full_cells - (1 if rem else 0))

    on  = "⣿" * full_cells
    mid = BRAILLE_STEPS[rem] if rem else ""
    off = f"<span alpha='{dim_alpha}'>{'⣿' * empty_cells}</span>" if empty_cells else ""
    return on + mid + off


def fmt_time(seconds):
    s = int(round(seconds))
    return f"{s // 60}:{s % 60:02d}"


# Extra footer bits (power, temps), filled once per run by gather_state().
_FOOTER_EXTRA = []


def set_footer_extras(watt, volt, cpu_temp, gpu_temp):
    _FOOTER_EXTRA.clear()
    if TT_SHOW_POWER:
        bits = [x for x in (watt, volt) if x and x != "N/A"]
        if bits:
            _FOOTER_EXTRA.append(" / ".join(bits))
    if TT_SHOW_TEMPS:
        bits = []
        if cpu_temp is not None:
            bits.append(f"CPU {cpu_temp:.0f}°C")
        if gpu_temp is not None:
            bits.append(f"GPU {gpu_temp:.0f}°C")
        if bits:
            _FOOTER_EXTRA.append(" ".join(bits))


def tooltip(bar_str, headline, sub1="", sub2="", cap=0, stat="Unknown",
            uptime_str="", metered=False):
    parts = []

    parts.append(f"<span size='large' weight='bold'>{headline}</span>")

    if sub1:
        parts.append(f"<span alpha='75%'>{sub1}</span>")
    if sub2:
        parts.append(f"<span alpha='75%'>{sub2}</span>")

    if bar_str:
        parts.append("")
        parts.append(bar_str)

    strip_bits = []
    bat_color = None
    if stat == "Charging":
        bat_color = TT_CHARGING_COLOR
    elif stat == "Discharging" and cap < LOW_BAT_THRESHOLD:
        bat_color = TT_LOW_COLOR

    if bat_color:
        strip_bits.append(f"<span foreground='{bat_color}'>{cap}%</span>")
    else:
        strip_bits.append(f"{cap}%")

    if TT_SHOW_UPTIME and uptime_str:
        strip_bits.append(uptime_str)
    if TT_SHOW_METERED and metered:
        strip_bits.append("metered")
    strip_bits.extend(_FOOTER_EXTRA)

    parts.append("")
    parts.append(f"<span alpha='25%'>{TT_SEPARATOR}</span>")
    parts.append("<span alpha='45%' size='small'>" + "   ·   ".join(strip_bits) + "</span>")

    return "\n".join(parts)

# ── Tooltip builders (shared by island and badge) ─────────

def tt_temp(temp_msg, cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    return tooltip(make_bar(bar_cells, bar_cells), "High temperature", temp_msg, "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_auth(cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    return tooltip(make_bar(0, bar_cells), "Waiting for password",
                   "Polkit or sudo prompt is open.", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_charger_plug(cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    return tooltip(make_bar(cap / 100.0 * bar_cells, bar_cells), "Charger plugged",
                   f"Battery at {cap}%", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_charger_unplug(cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    return tooltip(make_bar(cap / 100.0 * bar_cells, bar_cells), "Charger unplugged",
                   f"Battery at {cap}%", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_recording(rec_duration, cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    return tooltip(make_bar(bar_cells, bar_cells), "Screen recording",
                   f"Duration: {rec_duration}" if rec_duration else "", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_bt(bt_icon, cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    label = "Bluetooth connected" if bt_icon == "󰂱" else "Bluetooth disconnected"
    return tooltip(make_bar(bar_cells, bar_cells), label, "", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_usb(usb_icon, cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    label = "USB device plugged" if usb_icon == "󰕓" else "USB device unplugged"
    return tooltip(make_bar(bar_cells, bar_cells), label, "", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_pomodoro(pomo_mins, pomo_secs, cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    fill = (POMODORO_DURATION - (pomo_mins * 60 + pomo_secs)) / POMODORO_DURATION
    return tooltip(make_bar(fill * bar_cells, bar_cells), "Pomodoro",
                   f"{pomo_mins}:{pomo_secs:02d} remaining", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_hardware(rec_duration, cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    return tooltip(make_bar(bar_cells, bar_cells), "Mic or camera active",
                   f"Duration: {rec_duration}" if rec_duration else "", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_notification(notif_count, cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    plural = "s" if notif_count != 1 else ""
    return tooltip(make_bar(min(notif_count, NOTIF_TT_MAX) / float(NOTIF_TT_MAX) * bar_cells, bar_cells),
                   f"{notif_count} notification{plural}", "Waiting for attention", "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_music(m, cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    pct = min(1.0, max(0.0, m["position"] / m["length"])) if m["length"] > 0 else 0.0
    return tooltip(make_bar(pct * bar_cells, bar_cells), html.escape(m["title"]),
                   html.escape(m["artist"]),
                   html.escape(m["album"]) if m["album"] else "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_dnd(notif_count, cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    suppressed = (f"{notif_count} notification{'s' if notif_count != 1 else ''} suppressed"
                  if notif_count > 0 else "")
    return tooltip(make_bar(cap / 100.0 * bar_cells, bar_cells), "Do not disturb",
                   suppressed, "",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_battery(stat, cap, time_label, time_str, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    return tooltip(make_bar(cap / 100.0 * bar_cells, bar_cells), stat,
                   f"Charge: {cap}%", f"{time_label}: {time_str}",
                   cap=cap, stat=stat, uptime_str=uptime_str, metered=metered)

def tt_critical(cap, stat, uptime_str, metered, bar_cells=BAR_WIDTH_COMPACT):
    return tooltip(make_bar(cap / LOW_BAT_THRESHOLD * bar_cells, bar_cells), "Battery low",
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
                time_str = f"{int(h)}h {int((h % 1) * 60):02d}m"
            elif stat == "Charging" and charge_now and charge_full:
                h = (int(charge_full) - int(charge_now)) / c
                time_str = f"{int(h)}h {int((h % 1) * 60):02d}m"

        return cap, stat, volt, watt, time_str
    except (StopIteration, OSError, ValueError):
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
        except OSError:
            pass

    if prev and norm != prev and not os.path.exists(FLASH_FILE):
        is_plug   = norm == "Charging"    and prev == "Discharging"
        is_unplug = norm == "Discharging" and prev == "Charging"
        if is_plug or is_unplug:
            ftype = "plug" if is_plug else "unplug"
            try:
                with open(FLASH_FILE, "w") as f:
                    f.write(f"{int(time.time())} {ftype}")
            except OSError:
                pass

    flash_active, flash_icon = False, ""
    if os.path.exists(FLASH_FILE):
        try:
            content = read_sysfs(FLASH_FILE)
            if content and len(content.split()) == 2:
                ts, ftype = content.split()
                age = int(time.time()) - int(ts)
                if age < CHARGER_FLASH_SECS:
                    flash_active = True
                    flash_icon   = "󱐋" if ftype == "plug" else "󰚦"
                else:
                    os.remove(FLASH_FILE)
                    if not os.path.exists(CHARGER_EVENT_FILE):
                        with open(CHARGER_EVENT_FILE, "w") as f:
                            f.write(str(int(time.time())))
            else:
                os.remove(FLASH_FILE)
        except (OSError, ValueError):
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
        except (OSError, ValueError):
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
    except (subprocess.SubprocessError, OSError, json.JSONDecodeError):
        pass

    active = cam_active or mic_active
    if active and not os.path.exists(MIC_START_FILE):
        try:
            with open(MIC_START_FILE, "w") as f:
                f.write(str(int(time.time())))
        except OSError:
            pass
    elif not active and os.path.exists(MIC_START_FILE):
        try:
            os.remove(MIC_START_FILE)
        except OSError:
            pass
    return active


def get_recording_duration():
    if not os.path.exists(MIC_START_FILE):
        return ""
    try:
        ts = int(read_sysfs(MIC_START_FILE))
        return fmt_time(int(time.time()) - ts)
    except (TypeError, ValueError):
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
                   ("polkit", "pkexec", "authentication agent")):
                return True
    except (subprocess.SubprocessError, OSError, json.JSONDecodeError):
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
                    except OSError:
                        pass
            except OSError:
                pass
    except (subprocess.SubprocessError, OSError):
        pass

    return False


# ── Notifications / DND ────────────────────────────────────
def get_notification_count():
    try:
        c = subprocess.check_output(
            ["swaync-client", "-c"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        return int(c) if c else 0
    except (subprocess.SubprocessError, OSError, ValueError):
        return 0


def get_dnd_state():
    try:
        out = subprocess.check_output(
            ["swaync-client", "-D"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        return out.lower() == "true"
    except (subprocess.SubprocessError, OSError):
        return False


# ── Music ──────────────────────────────────────────────────
def get_metadata_safe(key):
    try:
        return subprocess.check_output(
            ["playerctl", "metadata", key],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.SubprocessError, OSError):
        return ""


def get_music_data():
    try:
        status = subprocess.check_output(
            ["playerctl", "status"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.SubprocessError, OSError):
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
    except (subprocess.SubprocessError, OSError, ValueError):
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
            name = read_sysfs(f"{hwmon_base}/{hw}/name") or ""
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
    except (subprocess.SubprocessError, OSError, ValueError, IndexError):
        for hw in (sorted(os.listdir(hwmon_base)) if os.path.exists(hwmon_base) else []):
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
    return (True, "  ".join(parts)) if parts else (False, "")


# ── Bluetooth flash ────────────────────────────────────────
def handle_bt_flash():
    try:
        out = subprocess.check_output(
            ["bluetoothctl", "devices", "Connected"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        current_count = len([l for l in out.splitlines() if l.strip()])
    except (subprocess.SubprocessError, OSError):
        current_count = 0

    prev_str = read_sysfs(BT_PREV_FILE)
    prev_count = int(prev_str) if prev_str and prev_str.isdigit() else current_count

    try:
        with open(BT_PREV_FILE, "w") as f:
            f.write(str(current_count))
    except OSError:
        pass

    if prev_count != current_count and not os.path.exists(BT_FLASH_FILE):
        connected = current_count > prev_count
        try:
            with open(BT_FLASH_FILE, "w") as f:
                f.write(f"{int(time.time())} {'connect' if connected else 'disconnect'}")
        except OSError:
            pass

    if os.path.exists(BT_FLASH_FILE):
        try:
            content = read_sysfs(BT_FLASH_FILE)
            if content and len(content.split()) == 2:
                ts, etype = content.split()
                age = int(time.time()) - int(ts)
                if age < BT_FLASH_SECS:
                    return True, ("󰂱" if etype == "connect" else "󰂲")
                os.remove(BT_FLASH_FILE)
        except (OSError, ValueError):
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
    except OSError:
        pass

    if prev_count != current_count and not os.path.exists(USB_FLASH_FILE):
        plugged = current_count > prev_count
        try:
            with open(USB_FLASH_FILE, "w") as f:
                f.write(f"{int(time.time())} {'plug' if plugged else 'unplug'}")
        except OSError:
            pass

    if os.path.exists(USB_FLASH_FILE):
        try:
            content = read_sysfs(USB_FLASH_FILE)
            if content and len(content.split()) == 2:
                ts, etype = content.split()
                age = int(time.time()) - int(ts)
                if age < USB_FLASH_SECS:
                    return True, ("󰕓" if etype == "plug" else "󰅖")
                os.remove(USB_FLASH_FILE)
        except (OSError, ValueError):
            pass

    return False, ""


def get_pomodoro_state():
    if not os.path.exists(POMODORO_FILE):
        return False, 0, 0, None

    state_name = read_sysfs(POMODORO_FILE) or "focus"

    try:
        start_ts = int(read_sysfs(POMODORO_START_FILE))
    except (TypeError, ValueError):
        return False, 0, 0, None

    elapsed = int(time.time()) - start_ts
    remaining = max(0, POMODORO_DURATION - elapsed)
    mins, secs = divmod(remaining, 60)

    if elapsed >= POMODORO_DURATION:
        for f in (POMODORO_FILE, POMODORO_START_FILE):
            try:
                os.remove(f)
            except OSError:
                pass
        return False, 0, 0, None

    return True, mins, secs, state_name


# ── Screen recording ───────────────────────────────────────
def get_screen_recording():
    try:
        subprocess.check_output(["pgrep", "-x", SCREENREC_PROCESS], stderr=subprocess.DEVNULL)
        active = True
    except (subprocess.CalledProcessError, OSError):
        active = False

    if active and not os.path.exists(SCREENREC_START):
        try:
            with open(SCREENREC_START, "w") as f:
                f.write(str(int(time.time())))
        except OSError:
            pass
    elif not active and os.path.exists(SCREENREC_START):
        try:
            os.remove(SCREENREC_START)
        except OSError:
            pass

    if active and os.path.exists(SCREENREC_START):
        try:
            ts = int(read_sysfs(SCREENREC_START))
            return True, fmt_time(int(time.time()) - ts)
        except (TypeError, ValueError):
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
        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"
    except (OSError, ValueError, IndexError):
        return "N/A"


def is_metered():
    try:
        out = subprocess.check_output(
            ["nmcli", "-t", "-f", "TYPE,STATE", "connection", "show", "--active"],
            text=True, stderr=subprocess.DEVNULL
        )
        for line in out.splitlines():
            parts = line.strip().split(":")
            if len(parts) >= 2 and parts[1] == "activated" and parts[0] in (
                "gsm", "cdma", "bluetooth", "wifi-p2p"
            ):
                return True
        out2 = subprocess.check_output(
            ["nmcli", "-t", "-f", "GENERAL.METERED", "device", "show"],
            text=True, stderr=subprocess.DEVNULL
        )
        for line in out2.splitlines():
            if "GENERAL.METERED" in line and "yes" in line.lower():
                return True
    except (subprocess.SubprocessError, OSError):
        pass
    return False


# ── Shared state gathering ─────────────────────────────────
@dataclass
class State:
    cap: int
    stat: str
    volt: str
    watt: str
    time_str: str
    uptime_str: str
    metered: bool
    flash_active: bool
    flash_icon: str
    c_window: bool
    hw_alert: bool
    notif_count: int
    dnd_active: bool
    m: Optional[dict]
    auth_active: bool
    cpu_temp: Optional[float]
    gpu_temp: Optional[float]
    temp_warn: bool
    temp_msg: str
    bt_flash: bool
    bt_icon: str
    usb_flash: bool
    usb_icon: str
    pomo_active: bool
    pomo_mins: int
    pomo_secs: int
    pomo_state: Optional[str]
    rec_active: bool
    rec_duration: str
    layer: str = field(init=False, default="")
    island: str = field(init=False, default="")

    def __post_init__(self):
        self.layer  = pick_layer(self)
        self.island = island_name(self, self.layer)


def gather_state() -> State:
    """Single source of truth: polls every enabled input exactly once."""
    cap, stat, volt, watt, time_str = get_battery_info()
    flash_active, flash_icon, c_window = handle_flash(stat, cap)

    hw_alert    = bool(ENABLED["hardware"] and cached("hw", HW_CACHE_SECS, is_hardware_active))
    notif_count = get_notification_count() if ENABLED["notifications"] else 0
    dnd_active  = get_dnd_state() if ENABLED["dnd"] else False
    m           = cached("music", MUSIC_CACHE_SECS, get_music_data) if ENABLED["music"] else None
    auth_active = is_auth_active() if ENABLED["auth"] else False

    if ENABLED["temp"]:
        cpu_temp, gpu_temp = cached("temps", TEMP_CACHE_SECS, get_temps)
    else:
        cpu_temp, gpu_temp = None, None
    temp_warn, temp_msg = check_temp_warning(cpu_temp, gpu_temp)

    bt_flash, bt_icon   = handle_bt_flash() if ENABLED["bluetooth"] else (False, "")
    usb_flash, usb_icon = handle_usb_flash() if ENABLED["usb"] else (False, "")
    pomo_active, pomo_mins, pomo_secs, pomo_state = (
        get_pomodoro_state() if ENABLED["pomodoro"] else (False, 0, 0, None)
    )
    rec_active, rec_duration = get_screen_recording() if ENABLED["recording"] else (False, "")
    uptime_str = get_uptime()
    metered    = bool(ENABLED["metered"] and cached("metered", METERED_CACHE_SECS, is_metered))

    set_footer_extras(watt, volt, cpu_temp, gpu_temp)

    return State(
        cap=cap, stat=stat, volt=volt, watt=watt, time_str=time_str,
        uptime_str=uptime_str, metered=metered,
        flash_active=flash_active, flash_icon=flash_icon, c_window=c_window,
        hw_alert=hw_alert, notif_count=notif_count, dnd_active=dnd_active, m=m,
        auth_active=auth_active, cpu_temp=cpu_temp, gpu_temp=gpu_temp,
        temp_warn=temp_warn, temp_msg=temp_msg,
        bt_flash=bt_flash, bt_icon=bt_icon, usb_flash=usb_flash, usb_icon=usb_icon,
        pomo_active=pomo_active, pomo_mins=pomo_mins, pomo_secs=pomo_secs, pomo_state=pomo_state,
        rec_active=rec_active, rec_duration=rec_duration,
    )


def flash_age_seconds():
    best = None
    for fpath, first_field in ((BT_FLASH_FILE, True), (USB_FLASH_FILE, True)):
        content = read_sysfs(fpath)
        if not content:
            continue
        try:
            ts = int(content.split()[0]) if first_field else int(content)
        except (ValueError, IndexError):
            continue
        age = time.time() - ts
        if best is None or age < best:
            best = age
    return best


# ── State picker ───────────────────────────────────────────
def layer_flags(s):
    """Which island layers are currently active (order comes from ISLAND_PRIORITY)."""
    return {
        "temp-warning":     s.temp_warn,
        "auth-waiting":     s.auth_active,
        "critical":         s.cap < LOW_BAT_THRESHOLD and s.stat == "Discharging",
        "charger-flash":    s.flash_active,
        "charger-window":   s.c_window,
        "screen-recording": s.rec_active,
        "bt-flash":         s.bt_flash,
        "usb-flash":        s.usb_flash,
        "pomodoro":         s.pomo_active,
        "hardware-alert":   s.hw_alert,
        "notification":     s.notif_count > 0,
        "music":            s.m is not None and s.m["status"] in ("Playing", "Paused"),
        "dnd":              s.dnd_active,
    }


def pick_layer(s):
    flags = layer_flags(s)
    for name in ISLAND_PRIORITY:
        if flags.get(name):
            return name
    return "battery"


def battery_state(s):
    if s.stat == "Charging":
        return "charging"
    if s.stat == "Not charging":
        return "plugged"
    if s.stat == "Full" or s.cap >= 100:
        return "full"
    return "discharging"


def island_name(s, layer):
    """Public state name: used for css classes, click actions and badge suppression."""
    if layer in ("charger-flash", "charger-window"):
        return "charging" if s.stat == "Charging" else "discharging"
    if layer == "music":
        return "music-paused" if s.m["status"] == "Paused" else "music"
    if layer == "battery":
        return battery_state(s)
    return layer


def run_cmd(args):
    """Fire-and-forget external command; never raises (missing binary, etc)."""
    try:
        subprocess.run(args, stderr=subprocess.DEVNULL)
    except (subprocess.SubprocessError, OSError):
        pass


def refresh_waybar():
    run_cmd(["pkill", f"-RTMIN+{WAYBAR_SIGNAL}", "waybar"])


# ── Click action handlers (shared by island and badge) ────
def action_left(state, m):
    if state in ("notification", "dnd", "auth-waiting", "critical"):
        run_cmd(SWAYNC_PANEL_CMD)
    elif state in ("music", "music-paused"):
        if m is not None:
            run_cmd(["playerctl", "play-pause"])
            refresh_waybar()
        else:
            run_cmd(SWAYNC_PANEL_CMD)
    elif state == "screen-recording":
        run_cmd(["pkill", "-x", SCREENREC_PROCESS])
    elif state == "pomodoro":
        pass  # no default action — leave the pomodoro running
    else:
        # battery / flashes / idle: open notification panel (matches island default)
        run_cmd(SWAYNC_PANEL_CMD)


def action_right(state, m):
    if state in ("notification", "dnd"):
        run_cmd(SWAYNC_DND_CMD)
    elif state in ("music", "music-paused"):
        if m is not None:
            run_cmd(["playerctl", "next"])
            refresh_waybar()
        else:
            run_cmd(SWAYNC_DND_CMD)
    elif state == "screen-recording":
        run_cmd(["pkill", "-x", SCREENREC_PROCESS])
    elif state == "pomodoro":
        pass
    else:
        run_cmd(SWAYNC_DND_CMD)


def action_scroll(state, direction, m):
    """direction: +1 for up, -1 for down. Only meaningful for music."""
    if state in ("music", "music-paused") and m is not None:
        sign = "+" if direction > 0 else "-"
        run_cmd(["playerctl", "position", f"{SEEK_STEP_SECS}{sign}"])
        refresh_waybar()


# ── Rendering ──────────────────────────────────────────────
def apply_layout(layout, default, **parts):
    """str.format with a safe fallback if the user's template is malformed."""
    try:
        return layout.format(**parts)
    except (KeyError, IndexError, ValueError):
        return default.format(**parts)


def _span(text, alpha=None):
    if text == "":
        return ""
    a = f" alpha='{alpha}'" if alpha else ""
    return f"<span font_family='{BAR_FONT}'{a}>{text}</span>"


def split_text(icon, bar, numbers=(), alpha=None):
    numbers = tuple(numbers)[:2]
    if len(numbers) == 2:
        joined = ":".join(numbers)
    elif numbers:
        joined = numbers[0]
    else:
        joined = ""
    return apply_layout(
        ISLAND_LAYOUT, "{icon} {bar}{gap}{value}",
        icon=icon,
        bar=_span(bar, alpha),
        gap=NUM_GAP if (bar and joined) else "",
        value=_span(joined, alpha),
    )


def badge_text(icon, number, more=""):
    return apply_layout(
        BADGE_LAYOUT, "{icon} {value}{more}",
        icon=icon, value=_span(number), more=more,
    )


def pct_str(value):
    """Percentage string, dropping the % sign once it hits 100 (keeps width sane)."""
    v = int(round(value))
    return "100" if v >= 100 else f"{v}%"


def _bat(s):
    """Shared battery pieces: (icon, state, time_label, bar, full_text)."""
    icon = BADGE_ICON.get(s.island if s.island in
           ("full", "charging", "plugged", "critical", "discharging") else "discharging", "󰁅")
    state = s.island if s.island in ("full", "charging", "plugged", "critical") else "discharging"
    time_label = "Time to full" if s.stat == "Charging" else "Time remaining"
    bar  = make_bar(s.cap * BAR_WIDTH_COMPACT / 100.0, BAR_WIDTH_COMPACT)
    text = split_text(icon, bar, (f"{s.cap}%",))
    return icon, state, time_label, bar, text


def _r_temp(s):
    blink = (time.time() % TEMP_BLINK_PERIOD) < TEMP_BLINK_ON
    text = split_text("󱃃", make_bar(BAR_WIDTH_COMPACT if blink else 0, BAR_WIDTH_COMPACT))
    return text, "temp-warning", tt_temp(s.temp_msg, s.cap, s.stat, s.uptime_str, s.metered)


def _r_auth(s):
    text = split_text("󰌾", make_bar(0, BAR_WIDTH_COMPACT))
    return text, "auth-waiting", tt_auth(s.cap, s.stat, s.uptime_str, s.metered)


def _r_battery_full(s):
    """Full battery readout. Used for critical and for the charger window."""
    _, state, time_label, _, text = _bat(s)
    return text, state, tt_battery(s.stat, s.cap, time_label, s.time_str, s.uptime_str, s.metered)


def _r_flash(s):
    _, state, _, _, _ = _bat(s)
    text = split_text(s.flash_icon, make_bar(BAR_WIDTH_COMPACT, BAR_WIDTH_COMPACT), (f"{s.cap}%",))
    tip = (tt_charger_plug(s.cap, s.stat, s.uptime_str, s.metered)
           if "󱐋" in s.flash_icon
           else tt_charger_unplug(s.cap, s.stat, s.uptime_str, s.metered))
    return text, state, tip


def _r_rec(s):
    nums = tuple(s.rec_duration.split(":")) if s.rec_duration else ()
    text = split_text("󰹑", make_bar(BAR_WIDTH_COMPACT, BAR_WIDTH_COMPACT), nums)
    return text, "screen-recording", tt_recording(s.rec_duration, s.cap, s.stat, s.uptime_str, s.metered)


def _r_bt(s):
    text = split_text(s.bt_icon, make_bar(BAR_WIDTH_COMPACT, BAR_WIDTH_COMPACT))
    return text, "bt-flash", tt_bt(s.bt_icon, s.cap, s.stat, s.uptime_str, s.metered)


def _r_usb(s):
    text = split_text(s.usb_icon, make_bar(BAR_WIDTH_COMPACT, BAR_WIDTH_COMPACT))
    return text, "usb-flash", tt_usb(s.usb_icon, s.cap, s.stat, s.uptime_str, s.metered)


def _r_pomo(s):
    fill = (POMODORO_DURATION - (s.pomo_mins * 60 + s.pomo_secs)) * BAR_WIDTH_COMPACT / POMODORO_DURATION
    text = split_text("󰅐", make_bar(fill, BAR_WIDTH_COMPACT), (str(s.pomo_mins), f"{s.pomo_secs:02d}"))
    return text, "pomodoro", tt_pomodoro(s.pomo_mins, s.pomo_secs, s.cap, s.stat, s.uptime_str, s.metered)


def _r_hw(s):
    duration = get_recording_duration()
    nums = tuple(duration.split(":")) if duration else ()
    text = split_text("󰍬", make_bar(BAR_WIDTH_COMPACT, BAR_WIDTH_COMPACT), nums)
    return text, "hardware-alert", tt_hardware(duration, s.cap, s.stat, s.uptime_str, s.metered)


def _r_notif(s):
    half_filled = min(s.notif_count, NOTIF_BAR_MAX)
    bars_on = (time.time() % NOTIF_BLINK_PERIOD) < NOTIF_BLINK_ON
    fill = half_filled if bars_on else 0
    text = split_text("󰂚", make_bar(fill, BAR_WIDTH_COMPACT), (str(s.notif_count),))
    return text, "notification", tt_notification(s.notif_count, s.cap, s.stat, s.uptime_str, s.metered)


def _r_music(s):
    is_paused = s.m["status"] == "Paused"
    state = "music-paused" if is_paused else "music"
    icon = "󰏤" if is_paused else "󰝚"
    pct = min(1.0, max(0.0, s.m["position"] / s.m["length"])) if s.m["length"] > 0 else 0.0
    text = split_text(icon, make_bar(pct * BAR_WIDTH_COMPACT, BAR_WIDTH_COMPACT))
    return text, state, tt_music(s.m, s.cap, s.stat, s.uptime_str, s.metered)


def _r_dnd(s):
    text = split_text("󰂛", make_bar(s.cap * BAR_WIDTH_COMPACT / 100.0, BAR_WIDTH_COMPACT),
                      (f"{s.cap}%",), alpha=DND_ALPHA)
    return text, "dnd", tt_dnd(s.notif_count, s.cap, s.stat, s.uptime_str, s.metered)


def _r_idle(s):
    """Nothing else is happening: the quiet battery readout."""
    icon, state, time_label, bar, _ = _bat(s)
    tip = tt_battery(s.stat, s.cap, time_label, s.time_str, s.uptime_str, s.metered)
    show_pct = IDLE_SHOW_PERCENT or s.cap < IDLE_PERCENT_BELOW
    text = split_text(
        icon,
        bar if IDLE_SHOW_BAR else "",
        (f"{s.cap}%",) if show_pct else (),
        alpha=IDLE_ALPHA,
    )
    return text, [state, "idle"], tip


ISLAND_RENDERERS = {
    "temp-warning":     _r_temp,
    "auth-waiting":     _r_auth,
    "critical":         _r_battery_full,
    "charger-flash":    _r_flash,
    "charger-window":   _r_battery_full,
    "screen-recording": _r_rec,
    "bt-flash":         _r_bt,
    "usb-flash":        _r_usb,
    "pomodoro":         _r_pomo,
    "hardware-alert":   _r_hw,
    "notification":     _r_notif,
    "music":            _r_music,
    "dnd":              _r_dnd,
    "battery":          _r_idle,
}


def render_island(s: State):
    """Build the main (wide) module's display text, state name and tooltip.
    Dispatches on s.layer, which pick_layer() chose from ISLAND_PRIORITY.
    The class is a string, or a list when the idle state adds an extra class."""
    return ISLAND_RENDERERS.get(s.layer, _r_idle)(s)


def render_badge(s: State):
    """Build the compact badge's display text, state name and tooltip."""
    ctx = {
        "island": s.island, "stat": s.stat, "cap": s.cap,
        "notif_count": s.notif_count, "dnd_active": s.dnd_active, "m": s.m,
        "rec_active": s.rec_active, "pomo_active": s.pomo_active,
        "hw_alert": s.hw_alert, "auth_active": s.auth_active,
        "temp_warn": s.temp_warn, "flash_age": flash_age_seconds(),
    }

    pomo_remaining = s.pomo_mins * 60 + s.pomo_secs

    candidates = [
        ("temp-warning",     s.temp_warn,   "󱃃",
            lambda: f"{max(s.cpu_temp or 0, s.gpu_temp or 0):.0f}°",
            tt_temp(s.temp_msg, s.cap, s.stat, s.uptime_str, s.metered, BADGE_CELLS)),
        ("auth-waiting",     s.auth_active, "󰌾", lambda: "",
            tt_auth(s.cap, s.stat, s.uptime_str, s.metered, BADGE_CELLS)),
        ("critical",         s.cap < LOW_BAT_THRESHOLD and s.stat == "Discharging", "󰁃",
            lambda: pct_str(s.cap),
            tt_critical(s.cap, s.stat, s.uptime_str, s.metered, BADGE_CELLS)),
        ("screen-recording", s.rec_active,  "󰹑",
            lambda: s.rec_duration or "0:00",
            tt_recording("", s.cap, s.stat, s.uptime_str, s.metered, BADGE_CELLS)),
        ("hardware-alert",   s.hw_alert,    "󰍬", lambda: "",
            tt_hardware("", s.cap, s.stat, s.uptime_str, s.metered, BADGE_CELLS)),
        ("bt-flash",         s.bt_flash,    s.bt_icon, lambda: "",
            tt_bt(s.bt_icon, s.cap, s.stat, s.uptime_str, s.metered, BADGE_CELLS)),
        ("usb-flash",        s.usb_flash,   s.usb_icon, lambda: "",
            tt_usb(s.usb_icon, s.cap, s.stat, s.uptime_str, s.metered, BADGE_CELLS)),
        ("notification",     s.notif_count > 0, "󰂚",
            lambda: str(s.notif_count),
            tt_notification(s.notif_count, s.cap, s.stat, s.uptime_str, s.metered, BADGE_CELLS)),
        ("pomodoro",         s.pomo_active, "󰅐",
            lambda: f"{s.pomo_mins}:{s.pomo_secs:02d}",
            tt_pomodoro(s.pomo_mins, s.pomo_secs, s.cap, s.stat, s.uptime_str, s.metered, BADGE_CELLS)),
        # Name + icon track pause state, matching render_island's
        # "music-paused" vs "music" naming, so contextual_score's
        # `state == ctx["island"]` suppression check actually fires when paused.
        ("music-paused" if (s.m and s.m["status"] == "Paused") else "music",
            s.m is not None and s.m["status"] in ("Playing", "Paused"),
            "󰏤" if (s.m and s.m["status"] == "Paused") else "󰝚",
            lambda: (pct_str(min(1.0, s.m['position'] / s.m['length']) * 100)
                     if s.m and s.m["length"] > 0 else "0%"),
            tt_music(s.m, s.cap, s.stat, s.uptime_str, s.metered, BADGE_CELLS) if s.m else ""),
        ("dnd",              s.dnd_active,  "󰂛", lambda: pct_str(s.cap),
            tt_dnd(s.notif_count, s.cap, s.stat, s.uptime_str, s.metered, BADGE_CELLS)),
        ("charging",         s.stat == "Charging", "󱐋",
            lambda: pct_str(s.cap),
            tt_battery(s.stat, s.cap, "Time to full", s.time_str, s.uptime_str, s.metered, BADGE_CELLS)),
    ]

    # Score every active candidate; anything scoring 0 or less is hidden.
    # sort is stable, so ties keep list order (same as the old strict `>`).
    scored = []
    for name, active, icon, num_fn, tip in candidates:
        if not active:
            continue
        score = contextual_score(name, ctx)
        if score > 0:
            scored.append((score, name, icon, num_fn, tip))
    scored.sort(key=lambda item: -item[0])

    if not scored:
        return badge_text(IDLE_BADGE_TEXT, ""), "idle", ""

    _, name, icon, num_fn, tip = scored[0]
    others = scored[1:]

    more = ""
    if BADGE_SHOW_OVERFLOW and others:
        marker = BADGE_OVERFLOW_FMT.format(n=len(others))
        more = BADGE_OVERFLOW_GAP + _span(marker, BADGE_OVERFLOW_ALPHA)

    if BADGE_TT_LIST_OTHERS and others:
        labels = ", ".join(STATE_LABELS.get(o[1], o[1]) for o in others)
        also = f"<span alpha='45%' size='small'>also: {html.escape(labels)}</span>"
        tip = f"{tip}\n{also}" if tip else also

    return badge_text(icon, num_fn(), more), name, tip


# ── Main ───────────────────────────────────────────────────
def main():
    s = gather_state()
    text, cls, tip = render_island(s)
    print(json.dumps({"text": text, "class": cls, "tooltip": tip}))


if __name__ == "__main__" and len(sys.argv) == 1:
    main()
    sys.exit(0)

# ── Argument dispatch ──────────────────────────────────────
if len(sys.argv) > 1:
    arg = sys.argv[1]

    if arg == "--play-pause":
        s = gather_state()
        action_left(s.island, s.m)
        sys.exit(0)

    if arg == "--next":
        s = gather_state()
        action_right(s.island, s.m)
        sys.exit(0)

    if arg == "--seek-forward":
        s = gather_state()
        action_scroll(s.island, +1, s.m)
        sys.exit(0)

    if arg == "--seek-back":
        s = gather_state()
        action_scroll(s.island, -1, s.m)
        sys.exit(0)

    if arg == "--extra":
        s = gather_state()
        text, cls, tip = render_badge(s)
        print(json.dumps({"text": text, "class": cls, "tooltip": tip}))
        sys.exit(0)
