import json
from qr_on_bg import get_playlist_tracks

if __name__ == "__main__":
    playlist_url = "https://open.spotify.com/playlist/0YmI56lLbxm0Fq9cMX6TZR?si=95f02622779a4d6e"
    # Fetch latest tracks from Spotify (with all artists)
    latest_tracks = get_playlist_tracks(playlist_url)
    # Build a dict for fast lookup by url
    url_to_artists = {t['url']: t['artist'] for t in latest_tracks}

    # Load existing JSON
    with open("spotify_tracks.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    for item in data:
        url = item.get('url')
        if url in url_to_artists:
            old_artist = item.get('artist', '')
            new_artist = url_to_artists[url]
            if old_artist != new_artist:
                item['artist'] = new_artist
                updated += 1

    with open("spotify_tracks.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Updated {updated} artist fields in spotify_tracks.json.")
