import sys, os
# Ensure the repository root is on sys.path so `from main.*` imports work
_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from PyPDF2 import PdfReader, PdfWriter
from main.config import TEXT_OUTPUT_PDF_TEMPLATE, QR_OUTPUT_PDF_TEMPLATE, COMBINED_OUTPUT_PDF_TEMPLATE

# Let the user pick which `spotify_tracks_*.json` to use from `main/playlist_list/`
playlist_list_dir = os.path.join(os.path.dirname(__file__), "playlist_list")
candidates = []
if os.path.isdir(playlist_list_dir):
    for fname in sorted(os.listdir(playlist_list_dir)):
        if fname.startswith("spotify_tracks_") and fname.endswith(".json"):
            name = fname[len("spotify_tracks_"):-len(".json")]
            candidates.append((name, fname))

if not candidates:
    print(f"No spotify_tracks_*.json files found in {playlist_list_dir}")
    sys.exit(1)

if len(candidates) == 1:
    playlist_slug = candidates[0][0]
else:
    print("Select playlist list to combine PDFs:")
    for i, (name, fname) in enumerate(candidates, start=1):
        print(f"{i}: {fname}")
    while True:
        sel = input(f"Choose 1-{len(candidates)} [1]: ").strip()
        if not sel:
            sel = "1"
        try:
            idx = int(sel)
            if 1 <= idx <= len(candidates):
                playlist_slug = candidates[idx-1][0]
                break
        except Exception:
            pass
        print("Invalid selection, try again.")

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
