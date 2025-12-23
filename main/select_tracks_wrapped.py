#!/usr/bin/env python3
"""Select wrapped tracks in a round-robin fashion.

Rules implemented:
- Read `playlist_list/spotify_tracks_wrapped_full.json` and `input files/wrapped_hitster.json` (to preserve name order)
- Round-robin: for each full pass, loop over all names in the wrapped list order, then check stop condition
- Per name: add the most "popular" song not yet in result (popularity = earliest `order` across all lists)
- Do not add if song URL already in result
- Do not add if there are already 3 songs by the same first artist in the result
- If a song appears on multiple persons' lists, the `name` field in the result will be the comma-separated persons
- Stop when result size == number_of_persons * 30 OR no more additions possible
- Output to `playlist_list/spotify_tracks_wrapped_selected.json`
"""
from collections import defaultdict
import json
import os
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
IN_FULL = os.path.join(ROOT, "playlist_list", "spotify_tracks_wrapped_full.json")
WRAPPED = os.path.join(ROOT, "input files", "wrapped_hitster.json")
OUT = os.path.join(ROOT, "playlist_list", "spotify_tracks_wrapped_selected.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_first_artist(artist_field):
    if not artist_field:
        return ""
    return artist_field.split(",")[0].strip()


def to_int_safe(v, default=9999999):
    try:
        return int(v)
    except Exception:
        return default


def main():
    if not os.path.exists(IN_FULL):
        print("Missing input:", IN_FULL)
        sys.exit(1)
    if not os.path.exists(WRAPPED):
        print("Missing wrapped list (name order):", WRAPPED)
        sys.exit(1)

    full = load_json(IN_FULL)
    wrapped = load_json(WRAPPED)

    # preserve persons order from wrapped file
    persons = [p.get("name") for p in wrapped if p.get("name")]
    persons = [p for p in persons if p]
    if not persons:
        # fallback to names in full file
        persons = sorted({t.get("name") for t in full if t.get("name")})

    num_persons = len(persons)
    target_size = num_persons * 34

    # Build mappings
    url_to_items = defaultdict(list)
    name_to_items = defaultdict(list)

    for t in full:
        url = (t.get("url") or "").strip()
        name = t.get("name")
        order = to_int_safe(t.get("order"))
        url_to_items[url].append({"item": t, "name": name, "order": order})
        if name:
            name_to_items[name].append({"item": t, "order": order})

    # Precompute min order per url (popularity)
    url_min_order = {}
    for url, items in url_to_items.items():
        url_min_order[url] = min(it["order"] for it in items if isinstance(it.get("order"), int) or isinstance(it.get("order"), float) or isinstance(it.get("order"), int))

    # For each person, sort their candidate URLs by min_order then by their personal order
    person_candidates = {}
    for name in persons:
        cand = []
        for entry in name_to_items.get(name, []):
            it = entry["item"]
            url = (it.get("url") or "").strip()
            if not url:
                continue
            min_o = url_min_order.get(url, to_int_safe(it.get("order")))
            cand.append((min_o, to_int_safe(entry.get("order")), url, it))
        # sort by (global popularity, personal order)
        cand.sort(key=lambda x: (x[0], x[1]))
        person_candidates[name] = cand

    result = []
    result_urls = set()

    # Helper to count first-artist occurrences in result
    def artist_count(first_artist):
        if not first_artist:
            return 0
        cnt = 0
        for r in result:
            fa = get_first_artist(r.get("artist", ""))
            if fa and fa.lower() == first_artist.lower():
                cnt += 1
        return cnt

    # Helper to check if an album is already present in result
    def album_exists(album_name):
        if not album_name:
            return False
        for r in result:
            a = (r.get("album") or "").strip()
            if a and a.lower() == album_name.lower():
                return True
        return False

    # Round-robin loop: complete a full pass over persons before checking stop
    while True:
        added_this_round = 0
        for name in persons:
            # find first candidate for this person that satisfies rules
            cand_list = person_candidates.get(name, [])
            chosen = None
            for (gmin, personal_order, url, it) in cand_list:
                if not url or url in result_urls:
                    continue
                # album constraint: skip if another song from same album already selected
                album_name = (it.get("album") or "").strip()
                if album_exists(album_name):
                    continue
                # artist constraint
                first_artist = get_first_artist(it.get("artist", ""))
                if artist_count(first_artist) >= 3:
                    continue
                # passed checks -> choose this
                chosen = (url, it)
                break

            if chosen:
                url, it = chosen
                # combine names: collect all distinct names this url appears under
                names = sorted({entry["name"] for entry in url_to_items.get(url, []) if entry.get("name")})
                combined_name = ", ".join(names) if names else name
                out_item = {
                    "title": it.get("title", ""),
                    "artist": it.get("artist", ""),
                    "album": it.get("album", ""),
                    "year": it.get("year", ""),
                    "url": url,
                    "checked": False,
                    "name": combined_name,
                    # store minimal order across lists
                    "order": url_min_order.get(url, to_int_safe(it.get("order")))
                }
                result.append(out_item)
                result_urls.add(url)
                added_this_round += 1

            # stop early if we reached target? requirement: finish full pass then check, so we don't break here

        # after full pass
        if len(result) >= target_size:
            break
        if added_this_round == 0:
            # nothing more can be added
            break

    # write output
    out_dir = os.path.dirname(OUT)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(result)} tracks to {OUT} (target {target_size})")


if __name__ == "__main__":
    main()
