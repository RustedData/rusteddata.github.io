#!/usr/bin/env python3
"""Export Spotify tracks for playlists listed in wrapped_hitster.json.

Creates: main/playlist_list/spotify_tracks_wrapped_full.json

Each element contains: title, artist, year, url, checked, name, order
"""
import json
import os
import sys

# make repo root importable like other scripts
_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from main.spotify_utils import get_playlist_tracks


WRAPPED_PATH = os.path.join(os.path.dirname(__file__), "input files", "wrapped_hitster.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "playlist_list", "spotify_tracks_wrapped_full.json")


def load_wrapped(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_output(path, items):
    out_dir = os.path.dirname(path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def build_wrapped_full(wrapped_list):
    all_items = []
    for playlist_entry in wrapped_list:
        name = playlist_entry.get("name")
        url = playlist_entry.get("url")
        if not url:
            print(f"Skipping entry with no url: {playlist_entry}")
            continue
        try:
            tracks = get_playlist_tracks(url) or []
        except Exception as exc:
            print(f"Failed to fetch tracks for {name} ({url}): {exc}")
            continue

        for idx, t in enumerate(tracks, start=1):
            item = {
                "title": t.get("title", ""),
                "artist": t.get("artist", ""),
                "album": t.get("album", ""),
                "year": t.get("year", ""),
                "url": t.get("url", ""),
                "checked": False,
                "name": name,
                "order": idx,
            }
            all_items.append(item)

    return all_items


def main():
    if not os.path.exists(WRAPPED_PATH):
        print(f"Wrapped input not found: {WRAPPED_PATH}")
        sys.exit(1)

    wrapped = load_wrapped(WRAPPED_PATH)
    items = build_wrapped_full(wrapped)
    write_output(OUT_PATH, items)
    print(f"Wrote {len(items)} tracks to {OUT_PATH}")


if __name__ == "__main__":
    main()
