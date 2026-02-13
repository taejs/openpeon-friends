#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".ogg"}
MAX_FILE_BYTES = 1 * 1024 * 1024
MAX_TOTAL_BYTES = 50 * 1024 * 1024
EXPECTED_AUTHOR_NAME = "taejs"
EXPECTED_AUTHOR_GITHUB = "taejs"
EXPECTED_PACK_NAME = "friends"
EXPECTED_LICENSE = "CC-BY-NC-4.0"
REQUIRED_LABELS = {
    "How you doin?",
    "We were on a break!",
    "You ate my sandwich?",
    "Oh. My. God.",
}


def error(message: str) -> None:
    print(f"ERROR: {message}")


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    manifest_path = root / "openpeon.json"

    if not manifest_path.exists():
        error(f"Manifest not found: {manifest_path}")
        return 1

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        error(f"Failed to parse openpeon.json: {exc}")
        return 1

    failures = 0
    warnings = 0

    required_top = [
        "cesp_version",
        "name",
        "display_name",
        "version",
        "author",
        "license",
        "language",
        "categories",
    ]
    for key in required_top:
        if key not in manifest:
            error(f"Missing top-level field: {key}")
            failures += 1

    author = manifest.get("author", {})
    if manifest.get("name") != EXPECTED_PACK_NAME:
        error(
            f'name must be "{EXPECTED_PACK_NAME}" '
            f'(current: {manifest.get("name")!r})'
        )
        failures += 1
    if manifest.get("license") != EXPECTED_LICENSE:
        error(
            f'license must be "{EXPECTED_LICENSE}" '
            f'(current: {manifest.get("license")!r})'
        )
        failures += 1
    if author.get("name") != EXPECTED_AUTHOR_NAME:
        error(
            f'author.name must be "{EXPECTED_AUTHOR_NAME}" '
            f'(current: {author.get("name")!r})'
        )
        failures += 1
    if author.get("github") != EXPECTED_AUTHOR_GITHUB:
        error(
            f'author.github must be "{EXPECTED_AUTHOR_GITHUB}" '
            f'(current: {author.get("github")!r})'
        )
        failures += 1

    categories = manifest.get("categories", {})
    if not isinstance(categories, dict) or not categories:
        error("categories must be a non-empty object")
        failures += 1
        categories = {}

    all_labels = []
    total_bytes = 0
    total_sounds = 0

    for category_name, category_obj in categories.items():
        sounds = category_obj.get("sounds", [])
        if not isinstance(sounds, list) or not sounds:
            error(f'Category "{category_name}" must contain non-empty sounds list')
            failures += 1
            continue

        for idx, sound in enumerate(sounds, start=1):
            file_ref = sound.get("file")
            label = sound.get("label")
            total_sounds += 1

            if not file_ref or not isinstance(file_ref, str):
                error(f'{category_name}[{idx}] missing "file"')
                failures += 1
                continue
            if not label or not isinstance(label, str):
                error(f'{category_name}[{idx}] missing "label"')
                failures += 1
            else:
                all_labels.append(label)

            resolved = (root / file_ref).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                error(f"{category_name}[{idx}] file escapes repo root: {file_ref}")
                failures += 1
                continue

            ext = resolved.suffix.lower()
            if ext not in ALLOWED_EXTENSIONS:
                error(
                    f"{category_name}[{idx}] unsupported file extension {ext} for {file_ref}"
                )
                failures += 1
                continue

            if not resolved.exists():
                error(f"{category_name}[{idx}] missing file: {file_ref}")
                failures += 1
                continue

            file_size = resolved.stat().st_size
            total_bytes += file_size
            if file_size > MAX_FILE_BYTES:
                error(
                    f"{category_name}[{idx}] exceeds 1MB ({file_size} bytes): {file_ref}"
                )
                failures += 1

    if total_bytes > MAX_TOTAL_BYTES:
        error(f"Total pack size exceeds 50MB: {total_bytes} bytes")
        failures += 1

    labels_set = set(all_labels)
    for label in sorted(REQUIRED_LABELS):
        if label not in labels_set:
            error(f"Required quote missing from labels: {label}")
            failures += 1

    if total_sounds < 20 or total_sounds > 30:
        error(f"Sound count must stay in 20-30 range (current: {total_sounds})")
        failures += 1

    if failures == 0:
        print("OK: pack validation passed")
        print(f"sound_count={total_sounds}")
        print(f"total_size_bytes={total_bytes}")
    else:
        print(f"FAILED: {failures} errors, {warnings} warnings")

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
