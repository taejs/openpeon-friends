#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST_PATH="$ROOT_DIR/openpeon.json"
DURATION_SECONDS="${DURATION_SECONDS:-1.2}"
OVERWRITE="${OVERWRITE:-0}"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg is required but not installed." >&2
  exit 1
fi

if [ ! -f "$MANIFEST_PATH" ]; then
  echo "Missing manifest: $MANIFEST_PATH" >&2
  exit 1
fi

files_raw="$(python3 - "$MANIFEST_PATH" <<'PY'
import json
import sys

manifest_path = sys.argv[1]
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

for category in manifest.get("categories", {}).values():
    for sound in category.get("sounds", []):
        path = sound.get("file")
        if path:
            print(path)
PY
)"

files=()
while IFS= read -r line; do
  [ -n "$line" ] || continue
  files+=("$line")
done <<EOF
$files_raw
EOF

if [ "${#files[@]}" -eq 0 ]; then
  echo "No sound files found in manifest." >&2
  exit 1
fi

created=0
skipped=0
for rel_path in "${files[@]}"; do
  out_path="$ROOT_DIR/$rel_path"
  mkdir -p "$(dirname "$out_path")"
  if [ -f "$out_path" ] && [ "$OVERWRITE" != "1" ]; then
    skipped=$((skipped + 1))
    continue
  fi
  ffmpeg -hide_banner -loglevel error \
    -f lavfi -i "anullsrc=r=44100:cl=mono" \
    -t "$DURATION_SECONDS" \
    -q:a 9 \
    -acodec libmp3lame \
    -y "$out_path"
  created=$((created + 1))
done

echo "Placeholder audio complete."
echo "created=$created skipped=$skipped total=$((created + skipped))"
