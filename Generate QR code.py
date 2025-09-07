# Voeg hier handmatig YouTube-tracks toe:
manual_tracks = [
    # Voorbeeld:
     {"title": "Jannenlied", "artist": "Jannen uit Zwaag", "year": "2011", "url": "https://www.youtube.com/watch?v=yoO3TP9QU44"},
]
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
from reportlab.lib.utils import ImageReader
import os


# 🔑 Vul je eigen Spotify API gegevens in
CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET as environment variables.")

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
            artist = track["artists"][0]["name"]
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

def create_pdf_front(tracks, filename="qrcards_front.pdf"):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    per_page = 4
    qr_size = 6 * cm

    for i, track in enumerate(tracks):
        page_index = i // per_page
        pos_index = i % per_page

        if pos_index == 0 and i > 0:
            c.showPage()

        positions = [(2*cm, height/2), (width/2, height/2),
                     (2*cm, 2*cm), (width/2, 2*cm)]
        x, y = positions[pos_index]

        qr_img = generate_qr_code(track["url"])
        img_io = io.BytesIO()
        qr_img.save(img_io, format="PNG")
        img_io.seek(0)

        img_reader = ImageReader(img_io)
        c.drawImage(img_reader, x, y, qr_size, qr_size)

    c.save()

def create_pdf_back(tracks, filename="qrcards_back.pdf"):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    per_page = 4
    qr_size = 6 * cm
    # Gebruik dezelfde posities als de voorkant, maar spiegel alleen de rijen (0<->1, 2<->3)
    positions = [(2*cm, height/2), (width/2, height/2), (2*cm, 2*cm), (width/2, 2*cm)]
    row_mirror = [1, 0, 3, 2]

    for i in range(0, len(tracks), per_page):
        subset = tracks[i:i+per_page]
        for pos_index, track_index in enumerate(row_mirror):
            if track_index >= len(subset):
                continue
            track = subset[track_index]
            x, y = positions[pos_index]
            text = f"{track['title']} - {track['artist']} ({track['year']})"
            c.setFont("Helvetica", 10)
            c.drawCentredString(x + qr_size/2, y + 3*cm, text)
        c.showPage()
    c.save()

if __name__ == "__main__":
    # 🎵 Vul hier je Spotify playlist in
    playlist_url = "https://open.spotify.com/playlist/1Uh0IYIezLqWiyQkwyOlU2?si=24d3d2bcebd94aa3"

    tracks = get_playlist_tracks(playlist_url)
    print(f"Gevonden {len(tracks)} nummers uit Spotify.")

    # Voeg handmatige YouTube-tracks toe
    all_tracks = tracks + manual_tracks

    create_pdf_front(all_tracks, "qrcards_front.pdf")
    create_pdf_back(all_tracks, "qrcards_back.pdf")
    print("✅ PDF’s gegenereerd: qrcards_front.pdf en qrcards_back.pdf")
