import pandas as pd
import json
from pathlib import Path

CURATED_DIR = Path("data/curated")


# -----------------------------
# Load curated data
# -----------------------------
def load_curated():
    tracks = pd.read_csv(CURATED_DIR / "top_tracks.csv")
    artists = pd.read_csv(CURATED_DIR / "top_artists.csv")
    recently = pd.read_csv(CURATED_DIR / "recently_played.csv")

    recently["played_at"] = pd.to_datetime(recently["played_at"])

    return tracks, artists, recently


# -----------------------------
# Extract genres summary
# -----------------------------
def genre_summary(artists_df):
    print("\n▶ Computing genre distribution...")

    # Each row contains a list of genres → convert to a flat list
    all_genres = []
    for _, row in artists_df.iterrows():
        try:
            genres = eval(row["genres"]) if isinstance(row["genres"], str) else []
            all_genres.extend(genres)
        except:
            continue

    genre_counts = pd.Series(all_genres).value_counts().head(10)

    genre_counts.to_csv(CURATED_DIR / "genre_summary.csv")

    print("✔ Saved: data/curated/genre_summary.csv")
    return genre_counts


# -----------------------------
# Time-of-day listening heatmap
# -----------------------------
def listening_by_hour(recently_df):
    print("\n▶ Computing hourly listening pattern...")

    recently_df["hour"] = recently_df["played_at"].dt.hour
    hourly = recently_df["hour"].value_counts().sort_index()

    hourly.to_csv(CURATED_DIR / "listening_by_hour.csv")

    print("✔ Saved: data/curated/listening_by_hour.csv")
    return hourly


# -----------------------------
# Daily listening trend
# -----------------------------
def listening_daily(recently_df):
    print("\n▶ Computing daily listening trend...")

    recently_df["date"] = recently_df["played_at"].dt.date
    daily = recently_df.groupby("date").size()

    daily.to_csv(CURATED_DIR / "listening_daily.csv")

    print("✔ Saved: data/curated/listening_daily.csv")
    return daily


# -----------------------------
# Track duration stats
# -----------------------------
def duration_stats(tracks_df):
    print("\n▶ Computing track duration statistics...")

    stats = tracks_df["duration_min"].describe()

    stats.to_csv(CURATED_DIR / "duration_stats.csv")

    print("✔ Saved: data/curated/duration_stats.csv")
    return stats


# -----------------------------
# Artist frequency (how often they appear)
# -----------------------------
def artist_frequency(tracks_df):
    print("\n▶ Computing artist frequency...")

    def extract_artist_name(a):
        try:
            # Artists is a list of objects → take first one
            return eval(a)[0]["name"]
        except:
            return None

    artists = tracks_df["artists"].apply(extract_artist_name)
    counts = artists.value_counts().head(10)

    counts.to_csv(CURATED_DIR / "artist_frequency.csv")

    print("✔ Saved: data/curated/artist_frequency.csv")
    return counts


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("\n==============================")
    print("      Analysis Pipeline")
    print("==============================\n")

    tracks, artists, recently = load_curated()

    genre_summary(artists)
    listening_by_hour(recently)
    listening_daily(recently)
    duration_stats(tracks)
    artist_frequency(tracks)

    print("\n🎉 Analysis complete! Charts/data ready for visualization.")
