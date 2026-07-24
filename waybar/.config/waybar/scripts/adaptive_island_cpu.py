#!/usr/bin/env python3
"""Background CPU monitor for adaptive_island.py.
Writes CPU % to /tmp/waybar_adaptive_cpu_cache every 3 seconds.
Start once at login: adaptive_island_cpu.py &
or add to your hyprland startup config."""
import time
import os

CACHE_FILE   = "/tmp/waybar_adaptive_cpu_cache"
INTERVAL     = 3.0   # seconds between updates

def read_cpu_stat():
    with open("/proc/stat") as f:
        parts = f.readline().split()
    vals  = list(map(int, parts[1:]))
    idle  = vals[3] + vals[4]   # idle + iowait
    total = sum(vals)
    return idle, total

prev_idle, prev_total = read_cpu_stat()

while True:
    time.sleep(INTERVAL)
    idle, total = read_cpu_stat()
    d_total = total - prev_total
    d_idle  = idle  - prev_idle
    cpu_pct = 100.0 * (1 - d_idle / d_total) if d_total > 0 else 0.0
    prev_idle, prev_total = idle, total
    try:
        with open(CACHE_FILE, "w") as f:
            f.write(f"{cpu_pct:.1f}")
    except:
        pass
