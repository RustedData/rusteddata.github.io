import os
import json
from qr_on_bg import create_qr_on_bg
from text_on_bg import create_text_on_bg
from manual_tracks import manual_tracks

# Load tracks from spotify_tracks.json and manual_tracks
with open("spotify_tracks.json", "r", encoding="utf-8") as f:
    spotify_tracks = json.load(f)
tracks = spotify_tracks + manual_tracks

# Output folder
output_dir = "card_pngs"
os.makedirs(output_dir, exist_ok=True)

for idx, track in enumerate(tracks):
    fileid = f"{idx+1:03d}"
    qr_path = os.path.join(output_dir, f"{fileid}_qr_back.png")
    text_path = os.path.join(output_dir, f"{fileid}_text_front.png")
    create_qr_on_bg(track["url"], qr_path)
    create_text_on_bg(track, text_path)

print(f"Generated {len(tracks)} pairs of PNGs in {output_dir}/")
