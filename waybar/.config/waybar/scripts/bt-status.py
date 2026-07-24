#!/usr/bin/env python3
import json
import subprocess

def get_bt_data():
    try:
        # Get paired devices
        devices_out = subprocess.check_output(["bluetoothctl", "devices", "Paired"], stderr=subprocess.DEVNULL).decode("utf-8").splitlines()
        connected_list = []

        for line in devices_out:
            parts = line.split()
            if len(parts) < 3: continue
            addr = parts[1]
            # Grab just the name, skipping the 'Device' and 'MAC' parts
            name = line.split(" ", 2)[2]

            info = subprocess.check_output(["bluetoothctl", "info", addr], stderr=subprocess.DEVNULL).decode("utf-8")

            if "Connected: yes" in info:
                battery = "N/A"
                for row in info.splitlines():
                    if "Battery Percentage" in row:
                        # bluetoothctl gives e.g. "0x64 (100)" — grab the value in parentheses
                        if "(" in row and ")" in row:
                            battery = row.split("(")[1].split(")")[0]
                        else:
                            battery = "".join(filter(str.isdigit, row))

                # Format: "Device Name: 80%" (No MAC address)
                connected_list.append(f"{name}: {battery}%")

        if not connected_list:
            return {"text": "", "tooltip": "No devices connected", "class": "disconnected"}

        # Join with single newlines for a tight, clean list
        tooltip_text = "\n".join(connected_list)

        return {
            "text": f" {len(connected_list)}",
            "tooltip": tooltip_text,
            "class": "connected"
        }
    except Exception as e:
        return {"text": "!", "tooltip": str(e), "class": "error"}

print(json.dumps(get_bt_data(), ensure_ascii=False))
