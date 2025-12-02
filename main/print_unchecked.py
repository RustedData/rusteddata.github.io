import json
from pprint import pprint

path = "main/playlist_list/spotify_tracks_oud_en_nieuw_hitster.json"

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    if not item.get("checked", False):
        pprint(item)
