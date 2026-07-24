#!/usr/bin/env python3
"""Mood daemon — picks & drifts mood matching SOUL.md weighting.
   Runs every ~30min via cron. On first run of the day picks fresh.
   On subsequent runs, may drift to a neighbouring mood.
"""

import json
import os
import random
import sys
import time

MOOD_FILE     = os.path.expanduser("~/.config/waybar/current_mood")
STATE_FILE    = os.path.expanduser("/tmp/waybar_mood_state.json")

MOOD_WEIGHTS = {
    "hyped":             22,
    "feral":             20,
    "soft-spot":         16,
    "confrontational":   12,
    "bitterly-amused":   10,
    "protective":         8,
    "weirdly-focused":    6,
    "unbothered":         4,
    "nostalgic":          4,
    "competitive":        3,
    "paranoid":           2,
    "irritable":          2,
    "bored-stiff":        1,
}

# Drift map: which moods can drift into which
DRIFT_MAP = {
    "hyped":            ["feral", "weirdly-focused"],
    "feral":            ["hyped", "confrontational", "competitive"],
    "soft-spot":        ["protective", "irritable"],
    "confrontational":  ["irritable", "feral", "competitive"],
    "bitterly-amused":  ["irritable", "nostalgic"],
    "protective":       ["confrontational", "soft-spot"],
    "weirdly-focused":  ["protective", "bitterly-amused"],
    "unbothered":       ["bitterly-amused", "irritable"],
    "nostalgic":        ["bitterly-amused", "soft-spot"],
    "competitive":      ["confrontational", "hyped"],
    "paranoid":         ["irritable", "confrontational"],
    "irritable":        ["confrontational", "paranoid", "soft-spot"],
    "bored-stiff":      ["unbothered", "bitterly-amused"],
}

def pick_mood():
    """Weighted random pick matching SOUL.md distribution."""
    total = sum(MOOD_WEIGHTS.values())
    r = random.randint(1, total)
    cumulative = 0
    for mood, weight in MOOD_WEIGHTS.items():
        cumulative += weight
        if r <= cumulative:
            return mood
    return "unbothered"  # fallback

def maybe_drift(current_mood):
    """~15% chance to drift to neighbouring mood."""
    if random.random() < 0.15 and current_mood in DRIFT_MAP:
        neighbours = DRIFT_MAP[current_mood]
        if neighbours:
            return random.choice(neighbours)
    return current_mood

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return None

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def get_today():
    return time.strftime("%Y-%m-%d")

def main():
    state = load_state()
    today = get_today()

    if state and state.get("date") == today:
        # Already have a mood for today — maybe drift
        current = state.get("mood", "unbothered")
        new_mood = maybe_drift(current)
    else:
        # New day — fresh pick
        new_mood = pick_mood()

    save_state({"date": today, "mood": new_mood})

    with open(MOOD_FILE, 'w') as f:
        f.write(new_mood)

    # Print the mood so cron can see it if needed
    print(new_mood)

if __name__ == "__main__":
    main()