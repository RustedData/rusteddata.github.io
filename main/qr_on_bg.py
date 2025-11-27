from PIL import Image
import qrcode
import io
import math
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from datetime import datetime
import os
from main.spotify_utils import get_playlist_tracks
from main.config import QR_BG_IMAGE, QR_OUTPUT_PDF, CARD_SIZE_CM, CARDS_COLS, CARDS_ROWS

# --- Import manual tracks from external file ---
from main.manual_tracks import manual_tracks
from main.config import get_playlist_url


# `get_playlist_tracks` is now centralized in `main.spotify_utils`.

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
    bg = Image.open(QR_BG_IMAGE).convert("RGBA")
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

def create_pdf_with_qr_images(tracks, filename=QR_OUTPUT_PDF):
    # Each image should be 6.5cm x 6.5cm on paper
    img_cm = CARD_SIZE_CM
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
    cols = CARDS_COLS
    rows = CARDS_ROWS
    per_page = cols * rows
    block_w = cols * img_w
    block_h = rows * img_h
    margin_x = (page_w - block_w) / 2
    margin_y = (page_h - block_h) / 2
    for page_start in range(0, len(images), per_page):
        page_images = images[page_start:page_start+per_page]
        for row in range(rows):
            row_start = row * cols
            row_imgs = page_images[row_start:row_start+cols]
            n_imgs_in_row = len(row_imgs)
            # Always fill from left to right, even for partial rows, and always center block
            for i, img_path in enumerate(row_imgs):
                x = margin_x + i * img_w
                y = page_h - margin_y - ((row + 1) * img_h)
                c.drawImage(img_path, x, y, img_w, img_h)
        if page_start + per_page < len(images):
            c.showPage()
    c.save()
    # Clean up temp files
    for f in temp_files:
        try:
            os.remove(f)
        except Exception:
            pass


if __name__ == "__main__":
    playlist_url = get_playlist_url()
    tracks = get_playlist_tracks(playlist_url)
    # Append manual tracks at the end
    tracks += manual_tracks
    print(f"Gevonden {len(tracks)} nummers (inclusief handmatige tracks).")
    create_pdf_with_qr_images(tracks, QR_OUTPUT_PDF)
    print(f"✅ PDF gegenereerd: {QR_OUTPUT_PDF}")
