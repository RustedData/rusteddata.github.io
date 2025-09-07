
import matplotlib.pyplot as plt
import json
from manual_tracks import manual_tracks

if __name__ == "__main__":
	# Read tracks from spotify_tracks.json
	with open("spotify_tracks.json", "r", encoding="utf-8") as f:
		spotify_tracks = json.load(f)
	# Combine with manual_tracks
	tracks = spotify_tracks + manual_tracks
	# Gather years
	years = [int(t['year']) for t in tracks if 'year' in t and str(t['year']).isdigit()]
	if not years:
		print("No valid years found in tracks.")
	else:
		plt.figure(figsize=(10,6))
		plt.hist(years, bins=range(min(years), max(years)+2), align='left', rwidth=0.8, color='skyblue', edgecolor='black')
		plt.xlabel('Year')
		plt.ylabel('Number of Tracks')
		plt.title('Histogram of Track Years (Spotify + Manual)')
		plt.xticks(range(min(years), max(years)+1))
		plt.grid(axis='y', linestyle='--', alpha=0.7)
		plt.tight_layout()
		plt.show()