from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials


CLIENT_ID = "6df28ad49766486da9edd3cf83d1e119"
CLIENT_SECRET = "741c0c0c9cd545cdb18a3fddd96c851a"
BG_IMAGE_PATH = "Text side.png"
OUTPUT_PDF = "qrcards_text_side.pdf"

# --- Import manual tracks from external file ---
from manual_tracks import manual_tracks

# Helper to get fonts (fallback to default if not found)
def get_font(size, bold=False, italic=False):
    try:
        if bold and italic:
            return ImageFont.truetype("arialbi.ttf", size)
        elif bold:
            return ImageFont.truetype("arialbd.ttf", size)
        elif italic:
            return ImageFont.truetype("ariali.ttf", size)
        else:
            return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

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
            track = item["track"]
            if not track:
                continue
            title = track["name"]
            artist = ', '.join([a["name"] for a in track["artists"]])
            release_year = track["album"]["release_date"].split("-")[0]
            url = track["external_urls"]["spotify"]
            tracks.append({
                "title": title,
                "artist": artist,
                "year": release_year,
                "url": url
            })
        if results["next"]:
            results = sp.next(results)
        else:
            results = None
    return tracks

def draw_glow_text(bg, draw, pos, text, font, glow_radius=4, fill="white", glow_color="black"):
    # Draw glow by drawing text several times with blur
    x, y = pos
    # Create a temp image for the glow
    temp = Image.new("RGBA", bg.size, (0,0,0,0))
    temp_draw = ImageDraw.Draw(temp)
    for dx in range(-glow_radius, glow_radius+1):
        for dy in range(-glow_radius, glow_radius+1):
            temp_draw.text((x+dx, y+dy), text, font=font, fill=glow_color)
    blurred = temp.filter(ImageFilter.GaussianBlur(radius=glow_radius))
    bg.paste(blurred, (0,0), blurred)
    draw.text((x, y), text, font=font, fill=fill)

def create_text_on_bg(track, out_path):
    bg = Image.open(BG_IMAGE_PATH).convert("RGBA")
    W, H = bg.size
    draw = ImageDraw.Draw(bg)
    # Font sizes relative to image height
    year_font = get_font(int(H*0.30), bold=True)  # Bigger year
    artist_font = get_font(int(H*0.07), bold=True)  # Much smaller
    title_font = get_font(int(H*0.06), italic=True)  # Much smaller

    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current = ''
        for word in words:
            test = current + (' ' if current else '') + word
            bbox = draw.textbbox((0,0), test, font=font)
            w = bbox[2] - bbox[0]
            if w > max_width and current:
                lines.append(current)
                current = word
            else:
                current = test
        if current:
            lines.append(current)
        return lines

    # Release year (center, a bit higher)
    year_text = str(track["year"])
    year_bbox = draw.textbbox((0,0), year_text, font=year_font)
    w, h = year_bbox[2] - year_bbox[0], year_bbox[3] - year_bbox[1]
    # Use the bbox to center exactly in the image, accounting for font ascent/descent
    year_x = (W - w) // 2 - year_bbox[0]
    year_y = (H - h) // 2 - year_bbox[1]
    year_pos = (year_x, year_y)
    draw_glow_text(bg, draw, year_pos, year_text, year_font, fill="white", glow_color="black")

    # Draw a white outline for cutting
    outline_width = max(2, W//100)  # At least 2px, scale with image size
    outline_draw = ImageDraw.Draw(bg)
    outline_draw.rectangle([(outline_width//2, outline_width//2), (W-outline_width//2-1, H-outline_width//2-1)], outline="white", width=outline_width)

    # Artist (top, much smaller, wrap if needed)
    artist_text = track["artist"]
    max_artist_width = int(W*0.9)
    artist_lines = wrap_text(artist_text, artist_font, max_artist_width)
    artist_y = int(H*0.13)
    for i, line in enumerate(artist_lines):
        bbox = draw.textbbox((0,0), line, font=artist_font)
        aw = bbox[2] - bbox[0]
        ah = bbox[3] - bbox[1]
        artist_pos = ((W-aw)//2, artist_y + i*ah)
        draw_glow_text(bg, draw, artist_pos, line, artist_font, fill="white", glow_color="black")

    # Title (bottom, much smaller, wrap if needed)
    title_text = track["title"]
    max_title_width = int(W*0.9)
    title_lines = wrap_text(title_text, title_font, max_title_width)
    th_total = sum([draw.textbbox((0,0), line, font=title_font)[3] - draw.textbbox((0,0), line, font=title_font)[1] for line in title_lines])
    title_y = int(H*0.80)
    y_offset = 0
    for line in title_lines:
        bbox = draw.textbbox((0,0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        title_pos = ((W-tw)//2, title_y + y_offset)
        draw_glow_text(bg, draw, title_pos, line, title_font, fill="white", glow_color="black")
        y_offset += th
    bg.save(out_path)
    return out_path

def create_pdf_with_text_images(tracks, filename=OUTPUT_PDF):
    """
    Output a PDF with the text images of the tracks.
    Each image is placed in the center of a cell in a grid, similar to the QR code side.
    """
    img_cm = 6.5
    images = []
    temp_files = []
    for i, track in enumerate(tracks):
        temp_path = f"temp_text_{i}.png"
        create_text_on_bg(track, temp_path)
        images.append(temp_path)
        temp_files.append(temp_path)
    c = canvas.Canvas(filename, pagesize=A4)
    page_w, page_h = A4
    img_w = img_cm * cm
    img_h = img_cm * cm
    cols = int(page_w // img_w)
    rows = int(page_h // img_h)
    per_page = cols * rows
    for idx, img_path in enumerate(images):
        if idx % per_page == 0 and idx > 0:
            c.showPage()
        col = idx % cols
        row = (idx // cols) % rows
        x = col * img_w
        y = page_h - ((row + 1) * img_h)
        c.drawImage(img_path, x, y, img_w, img_h)
    c.save()
    for f in temp_files:
        try:
            os.remove(f)
        except Exception:
            pass

def create_pdf_with_text_images_mirrored(tracks, filename=OUTPUT_PDF):
    """
    Output a PDF where each row is mirrored compared to the QR side.
    If the QR side row is: image 1, image 2, image 3, whitespace
    The text side row will be: whitespace, image 3, image 2, image 1
    """
    img_cm = 6.5
    images = []
    temp_files = []
    for i, track in enumerate(tracks):
        temp_path = f"temp_text_{i}.png"
        create_text_on_bg(track, temp_path)
        images.append(temp_path)
        temp_files.append(temp_path)
    c = canvas.Canvas(filename, pagesize=A4)
    page_w, page_h = A4
    img_w = img_cm * cm
    img_h = img_cm * cm
    cols = int(page_w // img_w)
    rows = int(page_h // img_h)
    per_page = cols * rows
    n_images = len(images)
    for idx in range(n_images):
        if idx % per_page == 0 and idx > 0:
            c.showPage()
        row = (idx // cols) % rows
        col = idx % cols
        # Mirror the column index within the row
        mirrored_col = cols - 1 - col
        img_path = images[idx]
        x = mirrored_col * img_w
        y = page_h - ((row + 1) * img_h)
        c.drawImage(img_path, x, y, img_w, img_h)
    c.save()
    for f in temp_files:
        try:
            os.remove(f)
        except Exception:
            pass

def create_pdf_with_text_images_rightmost_first(tracks, filename=OUTPUT_PDF):
    """
    Output a PDF where each row is filled from right to left:
    image 1 in the top right, image 2 to its left, etc.
    """
    img_cm = 6.5
    images = []
    temp_files = []
    for i, track in enumerate(tracks):
        temp_path = f"temp_text_{i}.png"
        create_text_on_bg(track, temp_path)
        images.append(temp_path)
        temp_files.append(temp_path)
    c = canvas.Canvas(filename, pagesize=A4)
    page_w, page_h = A4
    img_w = img_cm * cm
    img_h = img_cm * cm
    cols = int(page_w // img_w)
    rows = int(page_h // img_h)
    per_page = cols * rows
    n_images = len(images)
    for page_start in range(0, n_images, per_page):
        page_images = images[page_start:page_start+per_page]
        for row in range(rows):
            row_start = row * cols
            row_imgs = page_images[row_start:row_start+cols]
            n_imgs_in_row = len(row_imgs)
            row_width = n_imgs_in_row * img_w
            left_margin = page_w - row_width
            for i, img_path in enumerate(reversed(row_imgs)):
                x = left_margin + i * img_w
                y = page_h - ((row + 1) * img_h)
                c.drawImage(img_path, x, y, img_w, img_h)
        if page_start + per_page < n_images:
            c.showPage()
    c.save()
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
    create_pdf_with_text_images_rightmost_first(tracks, OUTPUT_PDF)
    print(f"✅ PDF gegenereerd: {OUTPUT_PDF}")
