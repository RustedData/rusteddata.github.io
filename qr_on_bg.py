from PIL import Image
import qrcode
import io
import math
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime
import os



# Spotify API credentials are now read from environment variables for security
# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET as environment variables.")


BG_IMAGE_PATH = "QR side.png"  # PNG in main folder
OUTPUT_PDF = "qrcards_with_bg.pdf"

# --- Import manual tracks from external file ---
from manual_tracks import manual_tracks


# --- Copied from Generate QR code.py ---
def get_playlist_tracks(playlist_url):
    sp = Spotify(auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    ))

    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    results = sp.playlist_items(playlist_id, additional_types=['track'])

    tracks = []
    while results:
        for item in results["items"]:
            track = item.get("track")
            if not track:
                continue
            title = track.get("name", "")
            # Always get all artist names from the correct field
            artists = track.get("artists", [])
            artist_names = ', '.join([a.get("name", "") for a in artists])
            release_year = track.get("album", {}).get("release_date", "").split("-")[0]
            url = track.get("external_urls", {}).get("spotify", "")
            tracks.append({
                "title": title,
                "artist": artist_names,
                "year": release_year,
                "url": url
            })
        if results["next"]:
            results = sp.next(results)
        else:
            results = None
    return tracks

def generate_qr_code(url):
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def create_qr_on_bg(track_url, out_path):
    bg = Image.open(BG_IMAGE_PATH).convert("RGBA")
    bg_w, bg_h = bg.size
    qr_size = int(0.4 * min(bg_w, bg_h))
    qr_img = generate_qr_code(track_url).resize((qr_size, qr_size), Image.LANCZOS).convert("RGBA")
    # Center QR on background
    x = (bg_w - qr_size) // 2
    y = (bg_h - qr_size) // 2
    bg.paste(qr_img, (x, y), qr_img)
    # Draw a white outline for cutting
    outline_width = max(2, bg_w//100)  # At least 2px, scale with image size
    from PIL import ImageDraw
    outline_draw = ImageDraw.Draw(bg)
    outline_draw.rectangle([(outline_width//2, outline_width//2), (bg_w-outline_width//2-1, bg_h-outline_width//2-1)], outline="white", width=outline_width)
    bg.save(out_path)
    return out_path

def create_pdf_with_qr_images(tracks, filename=OUTPUT_PDF):
    # Each image should be 6.5cm x 6.5cm on paper
    img_cm = 6.5
    img_px = 500  # arbitrary, just for temp images
    images = []
    temp_files = []
    for i, track in enumerate(tracks):
        temp_path = f"temp_qr_{i}.png"
        create_qr_on_bg(track["url"], temp_path)
        images.append(temp_path)
        temp_files.append(temp_path)
    c = canvas.Canvas(filename, pagesize=A4)
    page_w, page_h = A4
    img_w = img_cm * cm
    img_h = img_cm * cm
    # Calculate how many fit per row/col
    cols = int(page_w // img_w)
    rows = int(page_h // img_h)
    per_page = cols * rows
    for idx, img_path in enumerate(images):
        if idx % per_page == 0 and idx > 0:
            c.showPage()
        col = (idx % per_page) % cols
        row = (idx % per_page) // cols
        x = col * img_w
        y = page_h - ((row + 1) * img_h)
        c.drawImage(img_path, x, y, img_w, img_h)
    c.save()
    # Clean up temp files
    for f in temp_files:
        try:
            os.remove(f)
        except Exception:
            pass


if __name__ == "__main__":
    playlist_url = "https://open.spotify.com/playlist/0YmI56lLbxm0Fq9cMX6TZR?si=95f02622779a4d6e"
    tracks = get_playlist_tracks(playlist_url)
    # Append manual tracks at the end
    tracks += manual_tracks
    print(f"Gevonden {len(tracks)} nummers (inclusief handmatige tracks).")
    create_pdf_with_qr_images(tracks, OUTPUT_PDF)
    print(f"✅ PDF gegenereerd: {OUTPUT_PDF}")
