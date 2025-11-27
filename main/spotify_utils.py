"""Spotify helper utilities.

Provide a single `get_playlist_tracks(playlist_url)` implementation used by
multiple scripts in `main/`.

This module reads `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` from the
environment and raises a `RuntimeError` if they are not present.
"""
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials


def _get_spotify_client():
    CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
    CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError("Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET as environment variables.")
    return Spotify(auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    ))


def get_playlist_tracks(playlist_url):
    """Return a list of tracks for the given Spotify playlist URL.

    Each returned track is a dict with keys: `title`, `artist`, `year`, `url`.
    """
    sp = _get_spotify_client()

    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    results = sp.playlist_items(playlist_id, additional_types=["track"])

    tracks = []
    while results:
        for item in results.get("items", []):
            track = item.get("track")
            if not track:
                continue
            title = track.get("name", "")
            artists = track.get("artists", [])
            artist_names = ', '.join([a.get("name", "") for a in artists])
            release_year = ""
            album = track.get("album")
            if album:
                release_year = album.get("release_date", "").split("-")[0]
            url = track.get("external_urls", {}).get("spotify", "")
            tracks.append({
                "title": title,
                "artist": artist_names,
                "year": release_year,
                "url": url
            })
        if results.get("next"):
            results = sp.next(results)
        else:
            results = None
    return tracks


def get_playlist_slug(playlist_url):
    """Return a simple slug for the playlist name.

    - Try to fetch the playlist name via the Spotify API.
    - If available, lowercase it and replace spaces with underscores.
    - If not available, fall back to the playlist id (last segment of URL).
    """
    # derive raw id for fallback
    pid = playlist_url.split("/")[-1].split("?")[0] if playlist_url else ""

    # try API for name
    name = ""
    try:
        sp = _get_spotify_client()
        data = sp.playlist(pid)
        name = data.get("name", "") if data else ""
    except Exception:
        name = ""

    if not name:
        name = pid

    s = name.lower().replace(" ", "_")
    import re
    s = re.sub(r"[^a-z0-9_\-]", "", s)
    s = s[:64].strip("_-") or "playlist"
    return s