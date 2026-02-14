#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v curl >/dev/null 2>&1; then
  echo "Missing dependency: curl" >&2
  exit 1
fi

if ! command -v ffprobe >/dev/null 2>&1; then
  echo "Missing dependency: ffprobe" >&2
  exit 1
fi

declare -a SOURCES=(
  "sounds/joey__how_you_doin.mp3|https://www.myinstants.com/media/sounds/joey-how-you-doin.mp3"
  "sounds/ross__we_were_on_a_break.mp3|https://www.myinstants.com/media/sounds/wewereonabreak.mp3"
  "sounds/janice__oh_my_god.mp3|https://www.myinstants.com/media/sounds/friends-oh-my-god.mp3"
  "sounds/phoebe__my_eyes.mp3|https://www.myinstants.com/media/sounds/chandler-aaah-my-eyes.mp3"
  "sounds/ross__pivot.mp3|https://www.myinstants.com/media/sounds/friends-funny-scene-pivot.mp3"
  "sounds/ross__unagi.mp3|https://www.myinstants.com/media/sounds/unagi.mp3"
  "sounds/phoebe__smelly_cat.mp3|https://www.myinstants.com/media/sounds/smelly-cat.mp3"
)

rm -f sounds/*.mp3

for item in "${SOURCES[@]}"; do
  rel_file="${item%%|*}"
  url="${item#*|}"
  out_file="$ROOT_DIR/$rel_file"
  tmp_file="${out_file}.tmp"

  mkdir -p "$(dirname "$out_file")"
  curl -fsSL -L "$url" -o "$tmp_file"

  codec="$(ffprobe -v error -show_entries stream=codec_name -of csv=p=0 "$tmp_file" 2>/dev/null || true)"
  if [[ "$codec" != *"mp3"* ]]; then
    rm -f "$tmp_file"
    echo "Not an MP3 stream: $url" >&2
    exit 1
  fi

  mv "$tmp_file" "$out_file"
  size="$(wc -c < "$out_file" | tr -d ' ')"
  echo "OK  $rel_file  $size bytes"
done

echo
echo "Downloaded ${#SOURCES[@]} verified MyInstants clips."
