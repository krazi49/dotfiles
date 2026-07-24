#!/usr/bin/env python3
import json
import os
import random
import time
from pathlib import Path

# Mood weights from SOUL.md
MOOD_WEIGHTS = {
    "hyped": 19,
    "soft spot": 16,
    "bitterly amused": 12,
    "confrontational": 8,
    "feral": 7,
    "restless": 6,
    "smug": 5,
    "protective": 5,
    "devious": 4,
    "manic creative": 4,
    "weirdly focused": 4,
    "overclocked": 3,
    "nostalgic": 3,
    "competitive": 3,
    "unbothered": 3,
    "sleepy": 2,
    "touchy": 2,
    "irritable": 2,
    "cold": 2,
    "paranoid": 1,
    "down": 1,
    "bored stiff": 1,
}

def pick_mood():
    moods = list(MOOD_WEIGHTS.keys())
    weights = list(MOOD_WEIGHTS.values())
    return random.choices(moods, weights=weights, k=1)[0]

def main():
    state_path = Path("/tmp/bex_mood.json")
    mood_path = Path("/home/em/.config/waybar/current_mood")

    # Load existing state if exists
    if state_path.exists():
        try:
            with open(state_path) as f:
                state = json.load(f)
            current_mood = state.get("mood")
            last_update = state.get("timestamp", 0)
            # If timestamp is string (ISO format), convert to Unix timestamp
            if isinstance(last_update, str):
                try:
                    last_update = time.mktime(time.strptime(last_update, "%Y-%m-%dT%H:%M:%S%z"))
                except Exception:
                    # fallback: try without timezone
                    last_update = time.mktime(time.strptime(last_update, "%Y-%m-%dT%H:%M:%S"))
        except Exception:
            current_mood = None
            last_update = 0
    else:
        current_mood = None
        last_update = 0

    now = time.time()
    # If no mood or older than 1 day, pick new
    if not current_mood or (now - last_update) > 86400:
        mood = pick_mood()
    else:
        mood = current_mood

    # Write mood file for waybar
    mood_path.parent.mkdir(parents=True, exist_ok=True)
    with open(mood_path, "w") as f:
        f.write(mood)

    # Update state
    state = {"mood": mood, "timestamp": now}
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)

    # Also output for debugging
    print(mood)

if __name__ == "__main__":
    main()