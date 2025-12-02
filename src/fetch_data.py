import os
import json
import time
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

BASE_URL = "https://api.spotify.com/v1"
HEADERS = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------
# Helper: save JSON
# -------------------------------
def save_json(data, filename):
    path = RAW_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✔ Saved: {path}")


# -------------------------------
# Helper: GET request with retry
# -------------------------------
def spotify_get(url, params=None):
    response = requests.get(url, headers=HEADERS, params=params)

    # Token expired
    if response.status_code == 401:
        raise Exception("❌ Access token expired — refresh token needed.")

    # Rate limited
    if response.status_code == 429:
        wait = int(response.headers.get("Retry-After", 2))
        print(f"⏳ Rate limited, waiting {wait}s...")
        time.sleep(wait)
        return spotify_get(url, params)

    response.raise_for_status()
    return response.json()


# -------------------------------
# Fetch Top Tracks
# -------------------------------
def fetch_top_tracks():
    time_ranges = ["short_term", "medium_term", "long_term"]
    
    all_tracks = {}

    for tr in time_ranges:
        print(f"\n▶ Fetching Top Tracks ({tr})")
        data = spotify_get(
            f"{BASE_URL}/me/top/tracks",
            params={"limit": 50, "time_range": tr}
        )
        all_tracks[tr] = data

        save_json(data, f"top_tracks_{tr}.json")

    return all_tracks


# -------------------------------
# Fetch Top Artists
# -------------------------------
def fetch_top_artists():
    time_ranges = ["short_term", "medium_term", "long_term"]
    
    all_artists = {}

    for tr in time_ranges:
        print(f"\n▶ Fetching Top Artists ({tr})")
        data = spotify_get(
            f"{BASE_URL}/me/top/artists",
            params={"limit": 50, "time_range": tr}
        )
        all_artists[tr] = data

        save_json(data, f"top_artists_{tr}.json")

    return all_artists


# -------------------------------
# Fetch Recently Played
# -------------------------------
def fetch_recently_played():
    print("\n▶ Fetching Recently Played (up to last ~50 tracks)")
    
    data = spotify_get(
        f"{BASE_URL}/me/player/recently-played",
        params={"limit": 50}
    )

    save_json(data, "recently_played.json")

    return data


# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":

    print("\n==============================")
    print("  Spotify Data Fetch Script")
    print("==============================\n")

    top_tracks = fetch_top_tracks()
    top_artists = fetch_top_artists()
    recently = fetch_recently_played()

    print("\nSkipping audio features (Lite Mode enabled).")
    print("🎉 All data fetched and saved in data/raw/")
