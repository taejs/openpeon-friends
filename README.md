# openpeon-friends

Friends sound pack draft for PeonPing/OpenPeon, designed for coding event notifications.

## Required quotes included

- How you doin?
- We were on a break!
- My sandwich?!
- Oh. My. God.

## Popular quotes added

- Pivot! Pivot! Pivot!
- Unagi.
- Joey doesn't share food!
- I got off the plane.
- He's her lobster!
- Could I BE wearing any more clothes?
- I know!

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

2. Generate placeholder audio files (for local validation only):

```bash
bash scripts/create_placeholder_audio.sh
```

3. Replace placeholder files in `sounds/` with real clipped audio.

4. Validate pack rules:

```bash
python3 scripts/validate_pack.py
```

5. Create registry entry payload:

```bash
python3 scripts/build_registry_entry.py --source-repo taejs/openpeon-friends > registry-entry.json
```

6. Tag release:

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
