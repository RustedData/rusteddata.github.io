
import json
import sys, os
# Ensure the repository root is on sys.path so `from main.*` imports work
_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from main.spotify_utils import get_playlist_tracks, get_playlist_slug
from main.config import get_playlist_url, SPOTIFY_TRACKS_JSON_TEMPLATE

if __name__ == "__main__":
    playlist_url = get_playlist_url()
    playlist_slug = get_playlist_slug(playlist_url)
    spotify_tracks_json = SPOTIFY_TRACKS_JSON_TEMPLATE.format(playlist_slug=playlist_slug)

    print(f"Exporting tracks for playlist URL: {playlist_url}")
    print(f"Resolved playlist slug: {playlist_slug}")
    print(f"Will write tracks JSON to: {spotify_tracks_json}")

    try:
        new_tracks = get_playlist_tracks(playlist_url)
    except Exception as e:
        print("Failed to fetch tracks from Spotify:", e)
        raise

    # Ensure directory exists for per-playlist JSON
    spotify_dir = os.path.dirname(spotify_tracks_json)
    if spotify_dir and not os.path.exists(spotify_dir):
        os.makedirs(spotify_dir, exist_ok=True)

    # Load existing tracks if present
    if os.path.exists(spotify_tracks_json):
        try:
            with open(spotify_tracks_json, "r", encoding="utf-8") as f:
                existing_tracks = json.load(f)
        except Exception:
            existing_tracks = []
    else:
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

    with open(spotify_tracks_json, "w", encoding="utf-8") as f:
        json.dump(existing_tracks, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(existing_tracks)} tracks to {spotify_tracks_json}")

