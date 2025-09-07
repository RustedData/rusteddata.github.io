
from qr_on_bg import create_pdf_with_qr_images, OUTPUT_PDF as QR_PDF
from text_on_bg import create_pdf_with_text_images_rightmost_first, OUTPUT_PDF as TEXT_PDF
from manual_tracks import manual_tracks
import json

if __name__ == "__main__":
    # Read tracks from spotify_tracks.json
    with open("spotify_tracks.json", "r", encoding="utf-8") as f:
        spotify_tracks = json.load(f)
    # Combine with manual_tracks
    tracks = spotify_tracks + manual_tracks
    print(f"Gevonden {len(tracks)} nummers (spotify + handmatig).")
    create_pdf_with_qr_images(tracks, QR_PDF)
    print(f"✅ QR PDF gegenereerd: {QR_PDF}")
    create_pdf_with_text_images_rightmost_first(tracks, TEXT_PDF)
    print(f"✅ Tekst PDF gegenereerd: {TEXT_PDF}")
