#!/usr/bin/env python3
import html
import json
import re
import subprocess
import sys
from pathlib import Path

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


def curl_text(url: str) -> str:
    proc = subprocess.run(
        ["curl", "-fsSL", "-A", USER_AGENT, url],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"curl failed for {url}: {proc.stderr.strip()}")
    return proc.stdout


def curl_file(url: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        ["curl", "-fsSL", "-L", "-A", USER_AGENT, url, "-o", str(out_path)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"download failed for {url}: {proc.stderr.strip()}")


def resolve_101soundboards(url: str) -> str:
    page = curl_text(url)
    # Prefer OpenGraph audio URL; JSON-LD also includes image contentUrl entries.
    match = re.search(r'property="og:audio"\s+content="([^"]+)"', page)
    if not match:
        match = re.search(r'"contentUrl"\s*:\s*"([^"]+)"', page)
    if not match:
        raise RuntimeError(f"unable to find media URL in 101soundboards page: {url}")
    media = html.unescape(match.group(1)).replace("\\/", "/")
    if not media.startswith("http"):
        raise RuntimeError(f"invalid media URL extracted from {url}: {media}")
    return media


def resolve_myinstants(url: str) -> str:
    if "/media/sounds/" in url:
        return url
    page = curl_text(url)
    match = re.search(r"play\('([^']+)'", page)
    if not match:
        raise RuntimeError(f"unable to find media path in myinstants page: {url}")
    media_path = html.unescape(match.group(1))
    if media_path.startswith("http"):
        return media_path
    if media_path.startswith("/"):
        return f"https://www.myinstants.com{media_path}"
    return f"https://www.myinstants.com/{media_path}"


def resolve_media(source_url: str) -> str:
    if "101soundboards.com/sounds/" in source_url:
        return resolve_101soundboards(source_url)
    if "myinstants.com" in source_url:
        return resolve_myinstants(source_url)
    raise RuntimeError(f"unsupported source domain: {source_url}")


def verify_mp3(file_path: Path) -> None:
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name", "-of", "csv=p=0", str(file_path)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {file_path}: {proc.stderr.strip()}")
    codecs = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    if "mp3" not in codecs:
        raise RuntimeError(f"downloaded file is not mp3: {file_path} codecs={codecs}")


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    map_path = root / "source-map.json"
    if not map_path.exists():
        print(f"Missing source map: {map_path}", file=sys.stderr)
        return 1

    entries = json.loads(map_path.read_text(encoding="utf-8"))
    if not isinstance(entries, list) or not entries:
        print("source-map.json must be a non-empty array", file=sys.stderr)
        return 1

    errors = []
    for idx, entry in enumerate(entries, start=1):
        rel_file = entry.get("file")
        source_url = entry.get("source_url")
        if not rel_file or not source_url:
            errors.append(f"[{idx}] missing file/source_url")
            continue

        out_path = (root / rel_file).resolve()
        try:
            out_path.relative_to(root.resolve())
        except ValueError:
            errors.append(f"[{idx}] path escapes repo: {rel_file}")
            continue

        try:
            media_url = resolve_media(source_url)
            curl_file(media_url, out_path)
            verify_mp3(out_path)
            size = out_path.stat().st_size
            print(f"OK  {rel_file}  {size} bytes")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"[{idx}] {rel_file}: {exc}")
            print(f"ERR {rel_file}: {exc}", file=sys.stderr)

    if errors:
        print("\nDownload finished with errors:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    print(f"\nDownloaded {len(entries)} files successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
