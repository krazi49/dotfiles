#!/usr/bin/env python3
"""Ghost uptime — tells you how long you've been at this with attitude."""

import json
import os
import sys
import time

def get_uptime():
    try:
        with open("/proc/uptime") as f:
            secs = float(f.read().split()[0])
        days  = int(secs // 86400)
        hours = int((secs % 86400) // 3600)
        mins  = int((secs % 3600) // 60)
        return days, hours, mins, secs
    except:
        return 0, 0, 0, 0

MESSAGES = [
    "you're still here?",
    "touch grass challenge: impossible",
    "same chair, same screen, same you",
    "this is fine. probably.",
    "go to bed",
    "it's not a phase, it's a lifestyle",
    "lock in or log off",
    "is this even fun anymore",
    "your chair misses the outdoors",
    "persistence: max. life: 0",
    "told you this was a bad idea",
    "monitor go brr",
    "sun'll be up soon",
    "fresh air is overrated anyway",
    "the terminal doesn't judge you",
    "third coffee? fourth? who's counting",
    "you could leave. you won't.",
    "this is your life now",
    "boss mode: sitting",
    "enjoying your stay in device jail",
]

def main():
    days, hours, mins, secs = get_uptime()

    if days > 0:
        time_str = f"{days}d {hours}h"
    elif hours > 0:
        time_str = f"{hours}h {mins}m"
    else:
        time_str = f"{mins}m"

    # Pick message based on uptime so it rotates naturally
    idx = int(secs / 600) % len(MESSAGES)
    msg = MESSAGES[idx]

    text = f"{time_str}  {msg}"
    tooltip = (
        f"<b>Uptime:</b> "
        f"{f'{days}d' if days else ''}"
        f"{f' {hours}h' if hours or days else ''}"
        f" {mins}m\n"
        f"<span alpha='40%'>since whatever point you gave up</span>"
    )

    print(json.dumps({"text": text, "tooltip": tooltip, "class": "ghost-uptime"}))

if __name__ == "__main__":
    main()
