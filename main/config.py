"""Global configuration for scripts in `main/`.

This module exposes `PLAYLIST_URL` and `get_playlist_url()`.

Usage:
- Import `PLAYLIST_URL` or call `get_playlist_url()` from other modules.
- You can override the default by setting the environment variable `PLAYLIST_URL`.

Do not store secrets in this file. It's fine to keep the playlist URL here
since it's not a secret; if you prefer runtime override, set `PLAYLIST_URL` env var.
"""
import os

# Default playlist URL used when no environment override is provided.
# Replace the string below with your desired playlist URL if you want a
# repository-tracked default. Otherwise set the `PLAYLIST_URL` environment
# variable to override at runtime.
DEFAULT_PLAYLIST_URL = "https://open.spotify.com/playlist/0YmI56lLbxm0Fq9cMX6TZR?si=95f02622779a4d6e"

def get_playlist_url():
    """Return the playlist URL.

    Order of preference:
    - Environment variable `PLAYLIST_URL` if set
    - `DEFAULT_PLAYLIST_URL` otherwise
    """
    return os.environ.get("PLAYLIST_URL", DEFAULT_PLAYLIST_URL)

# Convenience constant; modules can import this directly.
PLAYLIST_URL = get_playlist_url()

# File and output configuration
SPOTIFY_TRACKS_JSON = os.environ.get("SPOTIFY_TRACKS_JSON", "spotify_tracks.json")
# Templates for per-playlist files. Use `str.format(playlist_slug=...)` to create names.
# Default: store per-playlist JSON under `main/playlist_list/` and name by playlist title slug.
SPOTIFY_TRACKS_JSON_TEMPLATE = os.environ.get(
    "SPOTIFY_TRACKS_JSON_TEMPLATE",
    os.path.join(os.path.dirname(__file__), "playlist_list", "spotify_tracks_{playlist_slug}.json"),
)
QR_OUTPUT_PDF_TEMPLATE = os.environ.get(
    "QR_OUTPUT_PDF_TEMPLATE",
    os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "output", "{playlist_slug}", "qrcards_{playlist_slug}_with_bg.pdf")),
)
TEXT_OUTPUT_PDF_TEMPLATE = os.environ.get(
    "TEXT_OUTPUT_PDF_TEMPLATE",
    os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "output", "{playlist_slug}", "qrcards_{playlist_slug}_text_side.pdf")),
)
COMBINED_OUTPUT_PDF_TEMPLATE = os.environ.get(
    "COMBINED_OUTPUT_PDF_TEMPLATE",
    os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "output", "{playlist_slug}", "qrcards_{playlist_slug}_combined.pdf")),
)
_THIS_DIR = os.path.dirname(__file__)
# Default background images live in the `main/documents/` folder.
QR_BG_IMAGE = os.environ.get("QR_BG_IMAGE", os.path.join(_THIS_DIR, "documents", "QR side.png"))
TEXT_BG_IMAGE = os.environ.get("TEXT_BG_IMAGE", os.path.join(_THIS_DIR, "documents", "Text side.png"))
QR_OUTPUT_PDF = os.environ.get(
    "QR_OUTPUT_PDF",
    os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "output", "qrcards_with_bg.pdf")),
)
TEXT_OUTPUT_PDF = os.environ.get(
    "TEXT_OUTPUT_PDF",
    os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "output", "qrcards_text_side.pdf")),
)
PNG_OUTPUT_DIR = os.environ.get("PNG_OUTPUT_DIR", "card_pngs")
COMBINED_OUTPUT_PDF = os.environ.get("COMBINED_OUTPUT_PDF", "qrcards_combined.pdf")

# Template for per-playlist PNG output directory. Use with `.format(playlist_slug=...)`.
PNG_OUTPUT_DIR_TEMPLATE = os.environ.get(
    "PNG_OUTPUT_DIR_TEMPLATE",
    os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "output", "{playlist_slug}", "card_pngs")),
)

# Layout / card constants
# Card size in centimeters (each card is square)
CARD_SIZE_CM = float(os.environ.get("CARD_SIZE_CM", 6.5))
# Default grid size (columns x rows) when fixed layout is used
CARDS_COLS = int(os.environ.get("CARDS_COLS", 3))
CARDS_ROWS = int(os.environ.get("CARDS_ROWS", 4))

