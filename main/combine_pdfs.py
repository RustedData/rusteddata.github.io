from PyPDF2 import PdfReader, PdfWriter
from main.config import TEXT_OUTPUT_PDF_TEMPLATE, QR_OUTPUT_PDF_TEMPLATE, COMBINED_OUTPUT_PDF_TEMPLATE, get_playlist_url
from main.spotify_utils import get_playlist_slug
import os

# Resolve per-playlist filenames
playlist_url = get_playlist_url()
playlist_slug = get_playlist_slug(playlist_url)

# If there is a slug-named spotify_tracks file in main/playlist_list/, prefer that slug
try:
    playlist_list_dir = os.path.join(os.path.dirname(__file__), "playlist_list")
    if os.path.isdir(playlist_list_dir):
        for fname in os.listdir(playlist_list_dir):
            if not fname.startswith("spotify_tracks_") or not fname.endswith(".json"):
                continue
            name = fname[len("spotify_tracks_"):-len(".json")]
            if name:
                playlist_slug = name
                break
except Exception:
    pass

pdf1_path = TEXT_OUTPUT_PDF_TEMPLATE.format(playlist_slug=playlist_slug)
pdf2_path = QR_OUTPUT_PDF_TEMPLATE.format(playlist_slug=playlist_slug)
output_path = COMBINED_OUTPUT_PDF_TEMPLATE.format(playlist_slug=playlist_slug)

reader1 = PdfReader(pdf1_path)
reader2 = PdfReader(pdf2_path)
writer = PdfWriter()

num_pages = max(len(reader1.pages), len(reader2.pages))

for i in range(num_pages):
    if i < len(reader1.pages):
        writer.add_page(reader1.pages[i])
    if i < len(reader2.pages):
        writer.add_page(reader2.pages[i])

with open(output_path, "wb") as f:
    writer.write(f)

# Ensure output directory exists for combined PDF (already written above, but ensure path is correct)
output_dir = os.path.dirname(output_path)
if output_dir and not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)

# If file was written to a directory that didn't exist previously, re-write to be safe
with open(output_path, "wb") as f:
    writer.write(f)

print(f"Combined PDF written to {output_path}")
