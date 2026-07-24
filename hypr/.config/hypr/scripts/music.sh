#!/bin/bash

# Matugen-friendly fzf theme
export FZF_DEFAULT_OPTS="--color=16 --info=inline --layout=reverse --prompt='󰎆 Music Search: ' --border=rounded"

# 1. Faster search prompt
read -p "󰎆 Song/Artist: " query
[ -z "$query" ] && exit 0

# 2. Optimized yt-dlp call:
# --flat-playlist: Doesn't resolve every video URL (saves seconds on a Celeron)
# ytmsearch: Searches YouTube Music specifically (Official Audio > Videos)
selection=$(yt-dlp --flat-playlist --get-title --get-id "ytmsearch10:$query" |
  sed 'N;s/\n/ - /' |
  fzf --height=15 --header="Official Tracks & Albums")

if [ -n "$selection" ]; then
  video_id=$(echo "$selection" | awk -F ' - ' '{print $NF}')

  clear
  echo "󰎆 Playing: ${selection% - *}"

  # 3. High-Efficiency mpv playback
  # --no-resume-playback: Saves a tiny bit of disk I/O on your 4GB RAM
  mpv --no-video --ytdl-format=bestaudio --no-resume-playback "https://music.youtube.com/watch?v=$video_id"
fi
