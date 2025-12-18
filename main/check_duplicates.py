# Save and run as e.g. find_title_url_duplicates.py at repository root
import json, os, sys
import re
from collections import defaultdict

p = os.path.join("main", "playlist_list", "spotify_tracks_wrapped_full.json")
if not os.path.exists(p):
    print("File not found:", p)
    sys.exit(1)

with open(p, "r", encoding="utf-8") as f:
    tracks = json.load(f)

# Try rapidfuzz for better fuzzy matching, fall back to difflib
try:
    from rapidfuzz import fuzz
    def similarity(a, b):
        return fuzz.token_set_ratio(a, b)
except Exception:
    from difflib import SequenceMatcher
    def similarity(a, b):
        return int(SequenceMatcher(None, a, b).ratio() * 100)


def normalize(s):
    if not s:
        return ""
    s = s.lower()
    # remove parenthetical/bracketed info like (remastered), [live], etc.
    s = re.sub(r"[\(\[\{].*?[\)\]\}]", "", s)
    # remove common suffixes/words that don't change identity
    s = re.sub(r"\b(remastered|remaster|edit|live|version|single|mono|stereo)\b", "", s)
    # strip punctuation, extra whitespace
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# Prepare normalized title/artist for each track
items = []
for t in tracks:
    title = (t.get("title") or "").strip()
    artist = (t.get("artist") or "").strip()
    url = (t.get("url") or "").strip()
    norm_title = normalize(title)
    norm_artist = normalize(artist)
    items.append({
        "orig": t,
        "title": title,
        "artist": artist,
        "url": url,
        "norm_title": norm_title,
        "norm_artist": norm_artist,
    })

n = len(items)
# Disjoint set (union-find) for grouping fuzzy-equal tracks
parent = list(range(n))
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[rb] = ra

# Thresholds (percent)
TITLE_THRESH = 85
ARTIST_THRESH = 75

for i in range(n):
    for j in range(i+1, n):
        ti = items[i]["norm_title"]
        tj = items[j]["norm_title"]
        ai = items[i]["norm_artist"]
        aj = items[j]["norm_artist"]

        if not ti or not tj:
            continue

        title_sim = similarity(ti, tj)
        artist_sim = similarity(ai, aj) if (ai or aj) else 100  # no artist -> be lenient

        # Consider match if both title and artist similar enough,
        # or title very similar even if artist slightly different.
        if (title_sim >= TITLE_THRESH and artist_sim >= ARTIST_THRESH) or (title_sim >= 92 and artist_sim >= 60):
            union(i, j)

# Collect groups
groups = defaultdict(list)
for idx in range(n):
    groups[find(idx)].append(items[idx])

# Find groups where same (fuzzy) title+artist map to multiple URLs
collisions = []
for gid, group_items in groups.items():
    urls = defaultdict(list)
    for it in group_items:
        urls[it["url"]].append(it)
    if len(urls) > 1:
        collisions.append((group_items, urls))

if not collisions:
    print("No fuzzy title+artist collisions with different URLs found.")
else:
    for group_items, urls in collisions:
        # representative
        rep_titles = sorted({it["title"] for it in group_items if it["title"]})
        rep_artists = sorted({it["artist"] for it in group_items if it["artist"]})
        print("====")
        print("REP TITLES:", rep_titles[:3])
        print("REP ARTISTS:", rep_artists[:3])
        print(f"{len(group_items)} occurrences across {len(urls)} URLs")
        for url, items_for_url in urls.items():
            names = sorted({itm["orig"].get("name","") for itm in items_for_url})
            orders = sorted({str(itm["orig"].get("order","")) for itm in items_for_url}, key=lambda x: int(x) if x.isdigit() else x)
            variants = sorted({f'{itm["title"]} — {itm["artist"]}' for itm in items_for_url})
            print(f"  - {url} occurrences={len(items_for_url)} names={names} orders={orders} variants={variants}")
        print()