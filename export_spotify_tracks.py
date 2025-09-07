
import json
import os
# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from qr_on_bg import get_playlist_tracks

if __name__ == "__main__":
    playlist_url = "https://open.spotify.com/playlist/0YmI56lLbxm0Fq9cMX6TZR?si=95f02622779a4d6e"
    new_tracks = get_playlist_tracks(playlist_url)

    # Load existing tracks
    try:
        with open("spotify_tracks.json", "r", encoding="utf-8") as f:
            existing_tracks = json.load(f)
    except Exception:
        existing_tracks = []

    # Build set of existing URLs
    existing_urls = set(t.get("url") for t in existing_tracks)

    # Only add new tracks (by url)
    added = 0
    for t in new_tracks:
        if t.get("url") not in existing_urls:
            t["checked"] = False
            existing_tracks.append(t)
            added += 1

    # Ensure all tracks have checked field
    for t in existing_tracks:
        if "checked" not in t:
            t["checked"] = True  # Assume old tracks are checked

    # Order by title
    existing_tracks.sort(key=lambda x: x.get("title", "").lower())

    with open("spotify_tracks.json", "w", encoding="utf-8") as f:
        json.dump(existing_tracks, f, ensure_ascii=False, indent=2)

