#!/usr/bin/env python3
"""
sound daemon: watches hyprland IPC for special workspace toggle,
and udev for usb plug/unplug. fires paplay for each.

sounds expected in ~/.sounds/:
  login.wav
  logout.wav
  pluginusb.wav
  unplugusb.wav
  spworkspaceopen.wav
  spworkspacehide.wav
  batteryplug.wav
  batteryunplug.wav
  batterylow.wav
  workspaceswitch.wav
  openterminal.wav
  closeterminal.wav
  openwindow.wav
  closewindow.wav
  volume.wav
"""
import os
import socket
import subprocess
import threading

SOUNDS = os.path.expanduser("~/.sounds")

# window class names (lowercase) treated as "terminal" for open/close sounds
TERMINAL_CLASSES = {"kitty", "floating_kitty"}


def play(name):
    path = os.path.join(SOUNDS, name)
    if os.path.exists(path):
        subprocess.Popen(
            ["paplay", path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        print(f"[sound_daemon] missing sound file: {path}")


def hyprland_socket_path():
    sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    runtime = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    return f"{runtime}/hypr/{sig}/.socket2.sock"


def watch_special_workspace():
    sock_path = hyprland_socket_path()
    window_classes = {}  # address -> class, persists across socket reconnects
    while True:
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.connect(sock_path)
                buf = b""
                while True:
                    data = s.recv(4096)
                    if not data:
                        break
                    buf += data
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        line = line.decode(errors="ignore")
                        # activespecialv2>>WORKSPACEID,WORKSPACENAME,MONITORNAME
                        # WORKSPACEID/WORKSPACENAME both empty = special workspace closed
                        if line.startswith("activespecialv2>>"):
                            payload = line.split(">>", 1)[1]
                            parts = payload.split(",")
                            wsid = parts[0].strip() if len(parts) > 0 else ""
                            wsname = parts[1].strip() if len(parts) > 1 else ""
                            if wsid and wsname:
                                play("spworkspaceopen.wav")
                            else:
                                play("spworkspacehide.wav")

                        # workspacev2>>WORKSPACEID,WORKSPACENAME
                        # fires on normal workspace switches (not special toggles)
                        elif line.startswith("workspacev2>>"):
                            play("workspaceswitch.wav")

                        # openwindow>>ADDRESS,WORKSPACE,CLASS,TITLE
                        elif line.startswith("openwindow>>"):
                            payload = line.split(">>", 1)[1]
                            parts = payload.split(",", 3)
                            addr = parts[0].strip() if len(parts) > 0 else ""
                            wclass = parts[2].strip() if len(parts) > 2 else ""
                            is_term = wclass.lower() in TERMINAL_CLASSES
                            if addr:
                                window_classes[addr] = wclass
                            if is_term:
                                play("openterminal.wav")
                            else:
                                play("openwindow.wav")

                        # closewindow>>ADDRESS
                        elif line.startswith("closewindow>>"):
                            addr = line.split(">>", 1)[1].strip()
                            wclass = window_classes.pop(addr, "")
                            is_term = wclass.lower() in TERMINAL_CLASSES
                            if is_term:
                                play("closeterminal.wav")
                            else:
                                play("closewindow.wav")
        except (FileNotFoundError, ConnectionRefusedError, OSError) as e:
            print(f"[sound_daemon] hyprland socket error: {e}, retrying...")
            import time
            time.sleep(2)


def watch_usb():
    import time

    # uses udevadm monitor instead of pyudev to avoid extra deps
    proc = subprocess.Popen(
        ["udevadm", "monitor", "--udev", "--subsystem-match=usb"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )

    DEBOUNCE_SECONDS = 1.5
    last_fired = {"add": 0.0, "remove": 0.0}

    for line in proc.stdout:
        # example line: "UDEV  [12345.6789] add      /devices/.../usb1/1-1 (usb)"
        if not line.startswith("UDEV"):
            continue
        if "(usb)" not in line:
            continue

        action = None
        if " add " in line:
            action = "add"
        elif " remove " in line:
            action = "remove"
        if action is None:
            continue

        now = time.monotonic()
        if now - last_fired[action] < DEBOUNCE_SECONDS:
            continue  # part of the same physical plug/unplug event
        last_fired[action] = now

        if action == "add":
            play("pluginusb.wav")
        else:
            play("unplugusb.wav")


def watch_battery_plug():
    # watches AC adapter online/offline via udev power_supply events,
    # reading state directly from event properties to avoid sysfs read races
    proc = subprocess.Popen(
        ["udevadm", "monitor", "--udev", "--subsystem-match=power_supply", "--property"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )

    def read_initial_state():
        base = "/sys/class/power_supply"
        try:
            for entry in os.listdir(base):
                if entry.upper().startswith(("AC", "ADP")):
                    online_path = os.path.join(base, entry, "online")
                    if os.path.exists(online_path):
                        with open(online_path) as f:
                            return f.read().strip() == "1"
        except OSError:
            pass
        return None

    last_state = read_initial_state()
    current_is_ac = False

    for line in proc.stdout:
        line = line.rstrip("\n")

        if line.startswith("UDEV"):
            current_is_ac = False
            continue

        if line.startswith("POWER_SUPPLY_NAME="):
            name = line.split("=", 1)[1].upper()
            current_is_ac = name.startswith(("AC", "ADP"))
            continue

        if current_is_ac and line.startswith("POWER_SUPPLY_ONLINE="):
            value = line.split("=", 1)[1].strip()
            state = value == "1"
            if state != last_state:
                if state:
                    play("batteryplug.wav")
                else:
                    play("batteryunplug.wav")
                last_state = state


def watch_battery_low(threshold=20, poll_seconds=30):
    import time

    def get_capacity_and_status():
        base = "/sys/class/power_supply"
        try:
            for entry in os.listdir(base):
                if entry.upper().startswith("BAT"):
                    cap_path = os.path.join(base, entry, "capacity")
                    status_path = os.path.join(base, entry, "status")
                    if os.path.exists(cap_path):
                        with open(cap_path) as f:
                            cap = int(f.read().strip())
                        status = ""
                        if os.path.exists(status_path):
                            with open(status_path) as f:
                                status = f.read().strip()
                        return cap, status
        except (OSError, ValueError):
            pass
        return None, None

    already_warned = False

    while True:
        cap, status = get_capacity_and_status()
        if cap is not None:
            discharging = status.lower() == "discharging"
            if discharging and cap <= threshold:
                if not already_warned:
                    play("batterylow.wav")
                    already_warned = True
            else:
                already_warned = False
        time.sleep(poll_seconds)



def watch_volume():
    import re

    def get_volume():
        try:
            out = subprocess.run(
                ["pactl", "get-sink-volume", "@DEFAULT_SINK@"],
                capture_output=True, text=True, timeout=2,
            ).stdout
            match = re.search(r"(\d+)%", out)
            return int(match.group(1)) if match else None
        except Exception:
            return None

    proc = subprocess.Popen(
        ["pactl", "subscribe"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )

    QUIET_PERIOD = 0.25  # wait for this much silence after the last change before checking
    pending_lock = threading.Lock()
    state = {"timer": None}
    last_volume = get_volume()

    def check_and_fire():
        nonlocal last_volume
        with pending_lock:
            state["timer"] = None
        current = get_volume()
        if current is not None and current != last_volume:
            last_volume = current
            play("volume.wav")
        elif current is not None:
            last_volume = current

    for line in proc.stdout:
        # example: "Event 'change' on sink #0"
        if "on sink" not in line:
            continue
        if "'change'" not in line:
            continue

        with pending_lock:
            if state["timer"] is not None:
                state["timer"].cancel()
            t = threading.Timer(QUIET_PERIOD, check_and_fire)
            t.daemon = True
            state["timer"] = t
            t.start()


if __name__ == "__main__":
    t1 = threading.Thread(target=watch_special_workspace, daemon=True)
    t2 = threading.Thread(target=watch_usb, daemon=True)
    t3 = threading.Thread(target=watch_battery_plug, daemon=True)
    t4 = threading.Thread(target=watch_battery_low, daemon=True)
    t5 = threading.Thread(target=watch_volume, daemon=True)
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
