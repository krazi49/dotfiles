#!/usr/bin/env python3
import json
import subprocess
import sys
import os
import time
import html

BAR_WIDTH_COMPACT  = 15
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
FERAL_WARN_FILE    = "/tmp/waybar_feral_battery_warn"
FERAL_CRIT_THRESH  = 10
MOOD_FILE          = os.path.expanduser("~/.config/waybar/current_mood")

def get_current_mood():
    try:
        with open(MOOD_FILE, "r") as f:
            mood = f.read().strip()
            # Only take first word
            mood = mood.split()[0] if mood.split() else ""
            return mood if mood else None
    except:
        return None

# ── Argument dispatch ──────────────────────────────────────
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


# ── Helpers ────────────────────────────────────────────────
def read_sysfs(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except:
        return None

def make_bar(filled, total):
    """Split bar — returns (left, right) tuple. Icon goes between them.
    Both sides fill inward from the edges. Empty segments use • at low alpha."""
    filled = max(0, min(filled, total))
    half   = total // 2
    f      = filled // 2
    e      = half - f
    left   = ("•" * f) + (f"<span alpha='20%'>{'•' * e}</span>" if e else "")
    right  = (f"<span alpha='20%'>{'•' * e}</span>" if e else "") + ("•" * f)
    return left, right

def make_bar_str(filled, total):
    """Plain left-to-right bar for tooltips (no pango markup)."""
    filled = max(0, min(filled, total))
    return "\u2b2c" * filled + "\u2b2d" * (total - filled)

def fmt_time(seconds):
    s = int(round(seconds))
    return f"{s // 60}:{s % 60:02d}"

def live_activity_tooltip(activity_lines, cap, stat):
    bat_line = f"<b>Battery:</b> {cap}%  {stat}"
    return f"{activity_lines}\n<span alpha='40%'>·  ·  ·  ·  ·</span>\n{bat_line}"


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
    mood                                = get_current_mood()
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
        return (
            f"<span font_family='Paper Mono'{a}>{left}</span> "
            f"{icon} "
            f"<span font_family='Paper Mono'{a}>{right}</span>"
        )

    _bl, _br    = make_bar((cap * BAR_WIDTH_COMPACT) // 100, BAR_WIDTH_COMPACT)
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

    elif low_battery and not flash_active:
        # Feral mode: psychological warfare on low battery
        feral_low = mood == "feral" and cap <= 20
        if feral_low:
            messages = ["☠️⚡", "🔴NO", "🦞🔥", "💀🔋", "PLUG", "😡🔌"]
            idx = int(time.time() / 0.5) % len(messages)
            bars_on = (time.time() % 0.4) < 0.2
            _fl, _fr = make_bar(BAR_WIDTH_COMPACT if bars_on else 0, BAR_WIDTH_COMPACT)
            display_text = split_text(messages[idx], _fl, _fr)
            state = "feral-critical"
            insults = [
                "you had one job",
                "plug it in you absolute animal",
                "is this how you treat your devices",
                "your battery is SORRY it tried its best",
                "you're a menace to technology",
                "this laptop deserves better",
            ]
            insult = insults[int(time.time() / 3) % len(insults)]
            tooltip = live_activity_tooltip(f"🦞 <b>{insult}</b>", cap, stat)
            # Notify after 30s of feral battery
            if cap <= 8:
                now = int(time.time())
                fwarn_ts = None
                try:
                    with open(FERAL_WARN_FILE) as f:
                        fwarn_ts = int(f.read().strip())
                except:
                    pass
                if fwarn_ts is None:
                    with open(FERAL_WARN_FILE, 'w') as f:
                        f.write(str(now))
                elif now - fwarn_ts >= 30:
                    os.system("swaync-client -s 'I'M NOT MAD, I'M JUST DISAPPOINTED' 2>/dev/null")
                    os.remove(FERAL_WARN_FILE)
        else:
            state = "critical" if (time.time() % 0.75) < 0.5 else "critical-pulse"
            display_text = bat_text
            tooltip = bat_tooltip

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
        _pl, _pr     = make_bar(int((25*60 - (pomo_mins*60 + pomo_secs)) * BAR_WIDTH_COMPACT / (25*60)), BAR_WIDTH_COMPACT)
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
        lf = rf         = half_filled if bars_on else 0
        _nl, _nr        = make_bar(lf + rf, BAR_WIDTH_COMPACT)
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
        _ml, _mr     = make_bar(int(pct * BAR_WIDTH_COMPACT), BAR_WIDTH_COMPACT)
        display_text = split_text(music_icon, _ml, _mr)
        tooltip_bar  = make_bar_str(int(pct * 30), 30)
        tooltip      = live_activity_tooltip(
            f"<b>{html.escape(m['title'])}</b>\n"
            f"{html.escape(m['artist'])}\n"
            f"{html.escape(m['album'])}\n\n"
            f"<span font_family=\"Paper Mono\" font_features=\"tnum\">"
            f"{fmt_time(m['position'])} {tooltip_bar} {fmt_time(m['length'])}</span>",
            cap, stat
        )

    elif dnd_active:
        _dl, _dr     = make_bar((cap * BAR_WIDTH_COMPACT) // 100, BAR_WIDTH_COMPACT)
        display_text = split_text("󰂛", _dl, _dr, alpha="55%")
        state        = "dnd"
        tooltip      = live_activity_tooltip("<b>Do not disturb</b>", cap, stat)

    else:
        display_text = bat_text
        state        = bat_state
        tooltip      = bat_tooltip

    output = {"text": display_text, "class": state, "tooltip": tooltip}
    if mood:
        output["class"] = [state, f"mood-{mood}"]
    print(json.dumps(output))

if __name__ == "__main__":
    main()
