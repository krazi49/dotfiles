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
"""
import os
import socket
import subprocess
import threading

SOUNDS = os.path.expanduser("~/.sounds")


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
                        # activespecial>>MONITORNAME,WORKSPACENAME
                        # empty workspace name = special workspace closed
                        if line.startswith("activespecial>>"):
                            payload = line.split(">>", 1)[1]
                            parts = payload.split(",", 1)
                            wsname = parts[1] if len(parts) > 1 else ""
                            if wsname.strip():
                                play("spworkspaceopen.wav")
                            else:
                                play("spworkspacehide.wav")
        except (FileNotFoundError, ConnectionRefusedError, OSError) as e:
            print(f"[sound_daemon] hyprland socket error: {e}, retrying...")
            import time
            time.sleep(2)


def watch_usb():
    import pyudev

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem="usb")
    for device in iter(monitor.poll, None):
        if device.device_type != "usb_device":
            continue
        if device.action == "add":
            play("pluginusb.wav")
        elif device.action == "remove":
            play("unplugusb.wav")


if __name__ == "__main__":
    t1 = threading.Thread(target=watch_special_workspace, daemon=True)
    t2 = threading.Thread(target=watch_usb, daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
