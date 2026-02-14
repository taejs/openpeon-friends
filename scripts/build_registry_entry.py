#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a PeonPing registry entry JSON object from openpeon.json."
    )
    parser.add_argument(
        "--source-repo",
        default="taejs/openpeon-friends",
        help="GitHub repo in owner/name format",
    )
    parser.add_argument(
        "--source-ref",
        default=None,
        help="Git ref used by registry source_ref",
    )
    parser.add_argument(
        "--source-path",
        default=".",
        help="Path within repo where openpeon.json and sounds/ live",
    )
    parser.add_argument(
        "--description",
        default="Friends main cast sound pack for coding events.",
        help="Registry description field",
    )
    parser.add_argument(
        "--trust-tier",
        default="community",
        choices=["community", "official", "verified"],
        help="Registry trust tier",
    )
    parser.add_argument(
        "--added-date",
        default=dt.date.today().isoformat(),
        help="Date string YYYY-MM-DD",
    )
    parser.add_argument(
        "--updated-date",
        default=dt.date.today().isoformat(),
        help="Date string YYYY-MM-DD",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent.parent
    manifest_path = root / "openpeon.json"

    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw.decode("utf-8"))
    manifest_sha256 = hashlib.sha256(manifest_raw).hexdigest()

    categories = manifest.get("categories", {})
    category_names = []
    preview_sounds = []
    sound_count = 0
    total_size_bytes = 0

    for category, payload in categories.items():
        sounds = payload.get("sounds", [])
        if sounds:
            category_names.append(category)
        for sound in sounds:
            file_ref = sound.get("file", "")
            sound_path = (root / file_ref).resolve()
            sound_count += 1
            if sound_path.exists():
                total_size_bytes += sound_path.stat().st_size
            filename = Path(file_ref).name
            if filename and len(preview_sounds) < 2:
                preview_sounds.append(filename)

    source_ref = args.source_ref or f"v{manifest.get('version')}"

    entry = {
        "name": manifest.get("name"),
        "display_name": manifest.get("display_name"),
        "version": manifest.get("version"),
        "description": args.description,
        "author": manifest.get("author", {}),
        "trust_tier": args.trust_tier,
        "categories": sorted(category_names),
        "language": manifest.get("language"),
        "license": manifest.get("license"),
        "sound_count": sound_count,
        "total_size_bytes": total_size_bytes,
        "source_repo": args.source_repo,
        "source_ref": source_ref,
        "source_path": args.source_path,
        "manifest_sha256": manifest_sha256,
        "tags": ["tv", "sitcom", "friends"],
        "preview_sounds": preview_sounds,
        "added": args.added_date,
        "updated": args.updated_date,
    }

    print(json.dumps(entry, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
