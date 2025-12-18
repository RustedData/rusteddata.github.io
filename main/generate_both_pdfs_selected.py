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
from main.config import QR_OUTPUT_PDF_TEMPLATE, TEXT_OUTPUT_PDF_TEMPLATE
import json

"""
Create PDFs from `playlist_list/spotify_tracks_wrapped_selected.json`.

Differences from `generate_both_pdfs.py`:
- Only reads `spotify_tracks_wrapped_selected.json` as input.
- Replaces the `year` field with the `name` field (so the middle of the card shows the person name(s)).
"""

SELECTED_PATH = os.path.join(os.path.dirname(__file__), "playlist_list", "spotify_tracks_wrapped_selected.json")

if __name__ == "__main__":
    # Use the selected JSON filename to derive an output slug (no URL required)
    playlist_slug = os.path.splitext(os.path.basename(SELECTED_PATH))[0]

    # Read selected tracks
    if not os.path.exists(SELECTED_PATH):
        print("Selected tracks not found:", SELECTED_PATH)
        sys.exit(1)
    with open(SELECTED_PATH, "r", encoding="utf-8") as f:
        tracks = json.load(f)

    # Replace `year` with `name` so the middle of the card shows the person(s)
    for t in tracks:
        # `name` may already be a comma-separated string of persons
        t["year"] = t.get("name", "")

    # Build output filenames using the same templates as original script
    qr_pdf = QR_OUTPUT_PDF_TEMPLATE.format(playlist_slug=playlist_slug)
    text_pdf = TEXT_OUTPUT_PDF_TEMPLATE.format(playlist_slug=playlist_slug)
    # Ensure output directory exists
    for p in (qr_pdf, text_pdf):
        out_dir = os.path.dirname(p)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

    create_pdf_with_qr_images(tracks, qr_pdf)
    print(f"✅ QR PDF generated: {qr_pdf}")
    create_pdf_with_text_images_rightmost_first(tracks, text_pdf)
    print(f"✅ Text PDF generated: {text_pdf}")
