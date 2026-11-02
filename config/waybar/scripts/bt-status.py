#!/usr/bin/env python3
import json
import subprocess
import sys

def get_bluetooth_status():
    try:
        # Get connected devices using blueutil if available, fallback to bluetoothctl
        output = subprocess.check_output(["bluetoothctl", "devices", "Connected"], stderr=subprocess.DEVNULL, text=True)
        lines = [l.strip() for l in output.splitlines() if l.strip()]
        count = len(lines)
        devices = []
        for line in lines:
            # Format: Device 00:11:22:33:44:55 Name
            parts = line.split()
            if len(parts) >= 3:
                addr = parts[1]
                name = " ".join(parts[2:])
                devices.append(f"{name} ({addr})")
        tooltip = "Connected devices:\n" + "\n".join(devices) if devices else "No Bluetooth devices connected"
        text = "󰂲" if count > 0 else "󰂲"
        alt = str(count)
        cls = "connected" if count > 0 else "disconnected"
        return text, alt, tooltip, cls
    except Exception:
        # Fallback: just check if bluetooth service is running
        try:
            subprocess.run(["systemctl", "is-active", "bluetooth"], check=True, capture_output=True)
            text = "󰂲"
            alt = "unknown"
            tooltip = "Bluetooth service is running"
            cls = "idle"
        except Exception:
            text = "󰂲"
            alt = "off"
            tooltip = "Bluetooth is disabled"
            cls = "disabled"
        return text, alt, tooltip, cls

def main():
    text, alt, tooltip, cls = get_bluetooth_status()
    result = {
        "text": text,
        "alt": alt,
        "tooltip": tooltip,
        "class": cls
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
