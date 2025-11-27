import os
import json
from main.qr_on_bg import create_qr_on_bg
from main.text_on_bg import create_text_on_bg
from main.manual_tracks import manual_tracks
from main.config import SPOTIFY_TRACKS_JSON_TEMPLATE, PNG_OUTPUT_DIR, PNG_OUTPUT_DIR_TEMPLATE, get_playlist_url
from main.spotify_utils import get_playlist_slug

# Load tracks from spotify_tracks.json and manual_tracks
playlist_url = get_playlist_url()
playlist_slug = get_playlist_slug(playlist_url)
spotify_tracks_json = SPOTIFY_TRACKS_JSON_TEMPLATE.format(playlist_slug=playlist_slug)
# Determine PNG output directory for this playlist
try:
    output_dir = PNG_OUTPUT_DIR_TEMPLATE.format(playlist_slug=playlist_slug)
except Exception:
    output_dir = PNG_OUTPUT_DIR
with open(spotify_tracks_json, "r", encoding="utf-8") as f:
    spotify_tracks = json.load(f)
tracks = spotify_tracks + manual_tracks

# Output folder
os.makedirs(output_dir, exist_ok=True)

for idx, track in enumerate(tracks):
    fileid = f"{idx+1:03d}"
    qr_path = os.path.join(output_dir, f"{fileid}_qr_back.png")
    text_path = os.path.join(output_dir, f"{fileid}_text_front.png")
    create_qr_on_bg(track["url"], qr_path)
    create_text_on_bg(track, text_path)

print(f"Generated {len(tracks)} pairs of PNGs in {output_dir}/")
