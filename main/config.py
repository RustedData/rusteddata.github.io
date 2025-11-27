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
# Leave empty to force interactive input when no env var is set.
DEFAULT_PLAYLIST_URL = ""


def get_playlist_url():
    """Return the playlist URL.

    Order of preference:
    - Environment variable `PLAYLIST_URL` if set and non-empty
    - If `DEFAULT_PLAYLIST_URL` is non-empty, use it
    - Otherwise prompt the user interactively until a non-empty URL is provided

    In non-interactive environments (no stdin), a RuntimeError is raised.
    """
    # 1) environment override
    env_url = os.environ.get("PLAYLIST_URL")
    if env_url:
        return env_url.strip()

    # 2) configured repository default (if present)
    if DEFAULT_PLAYLIST_URL:
        return DEFAULT_PLAYLIST_URL.strip()

    # 3) interactive prompt (required)
    prompt = (
        "Enter Spotify playlist URL (e.g. https://open.spotify.com/playlist/...): "
    )
    try:
        while True:
            url = input(prompt).strip()
            if not url:
                print("Playlist URL is required. Please enter a valid Spotify playlist URL.")
                continue
            # Basic sanity check for a URL
            if not (url.startswith("http://") or url.startswith("https://")):
                print("That doesn't look like a valid URL. Please enter a full URL starting with http:// or https://")
                continue
            return url
    except (EOFError, KeyboardInterrupt):
        # Non-interactive environment or user cancelled
        raise RuntimeError(
            "No PLAYLIST_URL provided (env var not set) and input is not available. Please set PLAYLIST_URL." 
        )

# Convenience constant; modules can import this directly.
# Do not call get_playlist_url() at import time (it may prompt). Instead prefer
# the environment/default value here. Call `get_playlist_url()` explicitly
# in scripts that want to prompt the user.
PLAYLIST_URL = os.environ.get("PLAYLIST_URL", DEFAULT_PLAYLIST_URL)

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

