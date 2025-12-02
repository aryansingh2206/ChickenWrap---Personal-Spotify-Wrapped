import json
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
CURATED_DIR = Path("data/curated")
CURATED_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Helper: load JSON safely
# -----------------------------
def load_json(filename):
    with open(RAW_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


# -----------------------------
# Process top tracks
# -----------------------------
def process_top_tracks():
    print("\n▶ Processing Top Tracks...")

    dfs = []
    for range_name in ["short_term", "medium_term", "long_term"]:
        fn = f"top_tracks_{range_name}.json"
        data = load_json(fn)

        df = pd.json_normalize(data["items"])
        df["time_range"] = range_name
        dfs.append(df)

    tracks_df = pd.concat(dfs, ignore_index=True)

    # Basic duration calculation
    tracks_df["duration_min"] = tracks_df["duration_ms"] / 60000

    tracks_df.to_csv(CURATED_DIR / "top_tracks.csv", index=False)

    print("✔ Saved: data/curated/top_tracks.csv")
    return tracks_df


# -----------------------------
# Process top artists
# -----------------------------
def process_top_artists():
    print("\n▶ Processing Top Artists...")

    dfs = []
    for range_name in ["short_term", "medium_term", "long_term"]:
        fn = f"top_artists_{range_name}.json"
        data = load_json(fn)

        df = pd.json_normalize(data["items"])
        df["time_range"] = range_name
        dfs.append(df)

    artists_df = pd.concat(dfs, ignore_index=True)
    artists_df.to_csv(CURATED_DIR / "top_artists.csv", index=False)

    print("✔ Saved: data/curated/top_artists.csv")
    return artists_df


# -----------------------------
# Process recently played
# -----------------------------
def process_recently_played():
    print("\n▶ Processing Recently Played...")

    data = load_json("recently_played.json")
    df = pd.json_normalize(data["items"])

    # Convert timestamps
    df["played_at"] = pd.to_datetime(df["played_at"])
    df.sort_values("played_at", inplace=True)

    df.to_csv(CURATED_DIR / "recently_played.csv", index=False)

    print("✔ Saved: data/curated/recently_played.csv")
    return df


# -----------------------------
# Compute summary stats (Lite)
# -----------------------------
def compute_summary(tracks_df, recently_df):
    print("\n▶ Computing Summary Insights...")

    summary = {}

    # Total duration (top tracks)
    summary["total_minutes_top_tracks"] = round(
        tracks_df["duration_min"].sum(), 2
    )

    # Top 5 tracks
    summary["top_5_tracks"] = (
        tracks_df["name"]
        .value_counts()
        .head(5)
        .index.tolist()
    )

    # Top 5 artists
    summary["top_5_artists"] = (
        tracks_df["artists"]
        .apply(lambda x: x[0]["name"] if isinstance(x, list) else None)
        .value_counts()
        .head(5)
        .index.tolist()
    )

    # Active listening hour
    recently_df["hour"] = recently_df["played_at"].dt.hour
    summary["most_active_hour"] = int(
        recently_df["hour"].value_counts().idxmax()
    )

    # Save summary
    with open(CURATED_DIR / "wrapped_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("✔ Saved: data/curated/wrapped_summary.json")
    return summary


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("\n==============================")
    print("        ETL Pipeline")
    print("==============================\n")

    top_tracks = process_top_tracks()
    top_artists = process_top_artists()
    recently = process_recently_played()

    # In Lite Mode, no merging necessary
    summary = compute_summary(top_tracks, recently)

    print("\n🎉 ETL complete! Curated data ready.")
