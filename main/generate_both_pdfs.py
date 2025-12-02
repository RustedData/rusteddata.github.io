
import sys, os
# Ensure the repository root is on sys.path so `from main.*` imports work
_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from main.qr_on_bg import create_pdf_with_qr_images
from main.text_on_bg import create_pdf_with_text_images_rightmost_first
from main.spotify_utils import get_playlist_slug
from main.config import SPOTIFY_TRACKS_JSON_TEMPLATE, QR_OUTPUT_PDF_TEMPLATE, TEXT_OUTPUT_PDF_TEMPLATE, get_playlist_url
from main.manual_tracks import manual_tracks
import json

if __name__ == "__main__":
    # Determine playlist-specific filenames
    playlist_url = get_playlist_url()
    playlist_slug = get_playlist_slug(playlist_url)
    print(playlist_slug)
    # Look for existing per-playlist JSON files in the `main/playlist_list/` folder.
    # Prefer a slug-named file (human title) if present; do not fall back to id-named files.
    playlist_list_dir = os.path.join(os.path.dirname(__file__), "playlist_list")
    print(f"Exporting tracks for playlist URL: {playlist_url}")
    print(f"Resolved playlist slug: {playlist_slug}")
    spotify_tracks = None

    # Candidate path based on the configured template (slug-only)
    spotify_tracks_json = SPOTIFY_TRACKS_JSON_TEMPLATE.format(playlist_slug=playlist_slug)

    # Read tracks from the chosen per-playlist spotify_tracks JSON
    with open(spotify_tracks_json, "r", encoding="utf-8") as f:
        spotify_tracks = json.load(f)
    # Combine with manual_tracks
    tracks = spotify_tracks
    print(f"Gevonden {len(tracks)} nummers (spotify + handmatig).")

    # Use the slug resolved from the playlist URL (API-first) for output filenames
    qr_pdf = QR_OUTPUT_PDF_TEMPLATE.format(playlist_slug=playlist_slug)
    text_pdf = TEXT_OUTPUT_PDF_TEMPLATE.format(playlist_slug=playlist_slug)
    # Ensure output directory exists
    for p in (qr_pdf, text_pdf):
        out_dir = os.path.dirname(p)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

    print(qr_pdf)
    create_pdf_with_qr_images(tracks, qr_pdf)
    print(f"✅ QR PDF gegenereerd: {qr_pdf}")
    create_pdf_with_text_images_rightmost_first(tracks, text_pdf)
    print(f"✅ Tekst PDF gegenereerd: {text_pdf}")
