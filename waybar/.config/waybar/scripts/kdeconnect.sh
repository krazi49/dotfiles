#!/bin/bash
DEVICE=$(kdeconnect-cli -l --id-only | head -1)

if [ -z "$DEVICE" ]; then
  echo '{"text": "", "tooltip": "No device connected", "class": "disconnected"}'
  exit
fi

BATTERY=$(kdeconnect-cli -d $DEVICE --battery)
NAME=$(kdeconnect-cli -d $DEVICE --name)

echo "{\"text\": \"\", \"tooltip\": \"$NAME\n$BATTERY\"}"
