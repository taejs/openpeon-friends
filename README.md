# openpeon-friends

Friends sound pack draft for PeonPing/OpenPeon, designed for coding event notifications.

## MyInstants-verified quotes (current)

- How you doin?
- We were on a break!
- Oh. My. God.
- My eyes! My eyes!
- Pivot! Pivot! Pivot!
- Unagi.
- Smelly cat, smelly cat.

## Author

- Name: `taejs`
- GitHub: `taejs`
- Contact: `taeshindev@gmail.com`

`taerim.shin@navercorp` is intentionally not used.

## Repository layout

```text
openpeon-friends/
  openpeon.json
  quotes.csv
  sounds/
  scripts/
    create_placeholder_audio.sh
    validate_pack.py
    build_registry_entry.py
  README.md
  LICENSE
```

## Quick start

1. Configure git author for this project:

```bash
git config user.name "taejs"
git config user.email "taeshindev@gmail.com"
```

2. Download all sounds from MyInstants:

```bash
bash scripts/download_myinstants_audio.sh
```

This script deletes existing `sounds/*.mp3` first, then downloads only the verified set.

3. Validate pack rules:

```bash
python3 scripts/validate_pack.py
```

4. Create registry entry payload:

```bash
python3 scripts/build_registry_entry.py --source-repo taejs/openpeon-friends > registry-entry.json
```

5. Tag release:

```bash
git tag v1.0.0
git push origin v1.0.0
```

## Registry submission checklist

- Add generated entry to `PeonPing/registry` `index.json` (alphabetical order by `name`)
- Use `"trust_tier": "community"`
- Ensure `manifest_sha256`, `sound_count`, `total_size_bytes`, and dates are current

## Notes

- License follows the standard PeonPing pack convention: `CC-BY-NC-4.0`
- Original media rights remain with the original rights holders
- Target size limit: max 1 MB per file, 50 MB total
- Allowed formats: WAV, MP3, OGG
- Keep rights/compliance checks for all final audio clips before publishing
