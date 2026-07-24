#!/bin/bash
# Returns • when there are any windows visible in wlr/taskbar, empty otherwise
count=$(hyprctl clients -j 2>/dev/null | python3 -c "import json,sys; print(len([c for c in json.load(sys.stdin) if c.get('mapped') and c.get('workspace')]))" 2>/dev/null)
if [ "$count" -gt 0 ]; then
  echo '{"text": "•", "class": "bullet", "tooltip": false}'
else
  echo '{"text": "", "class": "bullet-empty", "tooltip": false}'
fi
