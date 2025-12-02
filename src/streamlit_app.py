import streamlit as st
import pandas as pd
from pathlib import Path
import ast
import subprocess
import time
import plotly.graph_objects as go
import plotly.io as pio

CURATED_DIR = Path("data/curated")

# ----------------------------------------
# Page Config
# ----------------------------------------
st.set_page_config(
    page_title="Personal Spotify Wrapped",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------------------
# Session State for Navigation
# ----------------------------------------
if "page" not in st.session_state:
    st.session_state["page"] = "Overview"

# ----------------------------------------
# Navbar CSS
# ----------------------------------------
st.markdown("""
<style>

body {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #0F0F12, #121212);
    color: white;
}

header, footer {visibility: hidden;}

/* NAVBAR */
.navbar {
    position: sticky;
    top: 0;
    z-index: 999;
    padding: 18px 28px;
    background: rgba(15,15,20,0.45);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255,255,255,0.05);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-left {
    font-weight: 900;
    font-size: 22px;
}

.nav-buttons {
    display: flex;
    gap: 14px;
}

.nav-btn {
    padding: 8px 16px;
    border-radius: 10px;
    border: 1px solid transparent;
    font-weight: 600;
    color: rgba(255,255,255,0.85);
    background: none;
    cursor: pointer;
    transition: 0.2s ease;
}

.nav-btn:hover {
    background: rgba(255,255,255,0.08);
}

.nav-active {
    background: linear-gradient(135deg, #D526B7, #8338FF);
    box-shadow: 0 0 15px rgba(131,56,255,0.5);
    color: white !important;
}

/* Metric Cards */
.metric-box {
    background: rgba(255,255,255,0.05);
    border-radius: 22px;
    padding: 30px;
    border: 1px solid rgba(255,255,255,0.07);
    text-align: center;
    backdrop-filter: blur(12px);
}

.metric-label {
    font-size: 20px;
    font-weight: 700;
    opacity: 0.85;
}

.metric-value {
    font-size: 42px;
    font-weight: 900;
    margin-top: 10px;
}

/* Section container */
.section {
    margin: 30px 20px;
    padding: 25px;
    border-radius: 18px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
}

/* Artist Cards */
.carousel-container {
    white-space: nowrap;
    overflow-x: auto;
    padding-bottom: 12px;
}

.artist-card {
    display: inline-block;
    width: 220px;
    padding: 16px;
    margin-right: 16px;
    border-radius: 14px;
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(8px);
}

</style>

""", unsafe_allow_html=True)

# ----------------------------------------
# Build Navbar (Streamlit buttons that set session state)
# ----------------------------------------
nav_options = [
    "Overview",
    "Top Tracks",
    "Top Artists",
    "Genre Insights",
    "Listening Patterns",
    "Daily Trend",
    "Duration Stats"
]

cols = st.columns(len(nav_options))
for idx, name in enumerate(nav_options):
    active = st.session_state["page"] == name

    # style string for active/inactive handled by inline CSS injection below
    if cols[idx].button(name, key=f"nav_{name}", help=f"Go to {name}", use_container_width=True):
        st.session_state["page"] = name

    # style the generated button (limited but works)
    if active:
        style = """
            <style>
            div.stButton > button[data-testid="stButton"]{ background: linear-gradient(135deg,#D526B7,#8338FF) !important; color: white; border: none !important; box-shadow: 0 0 15px rgba(131,56,255,0.5); }
            </style>
        """
    else:
        style = """
            <style>
            div.stButton > button[data-testid="stButton"]{ background: rgba(255,255,255,0.05) !important; color: rgba(255,255,255,0.9); border: 1px solid rgba(255,255,255,0.12) !important; }
            </style>
        """
    cols[idx].markdown(style, unsafe_allow_html=True)

# ----------------------------------------
# CSV Loader Helpers
# ----------------------------------------
def robust_read_csv(path):
    df = pd.read_csv(path)

    # Remove header-as-row if present
    if df.shape[0] > 0 and isinstance(df.iloc[0, 0], str):
        if df.iloc[0, 0].strip().lower() in {"date", "genre", "hour", "artist", "plays", "metric"}:
            df = df.iloc[1:].reset_index(drop=True)

    # If single-column with CSV inside, split
    if df.shape[1] == 1 and "," in str(df.iloc[0, 0]):
        df = df[0].str.split(",", expand=True)

    df.columns = [str(c).strip() for c in df.columns]
    return df

def ensure_curated_files():
    required = [
        "top_tracks.csv", "top_artists.csv", "recently_played.csv",
        "genre_summary.csv", "listening_by_hour.csv",
        "listening_daily.csv", "duration_stats.csv",
        "artist_frequency.csv"
    ]
    missing = [f for f in required if not (CURATED_DIR / f).exists()]
    if missing:
        st.warning("Missing curated files — running ETL pipeline...")
        try:
            subprocess.run(["python", "src/etl.py"], check=True)
            time.sleep(1)
            st.success("ETL finished.")
        except Exception as e:
            st.error(f"ETL failed: {e}")
            raise

# ----------------------------------------
# Neon Charts
# ----------------------------------------
def neon_bar_chart(df, x, y, title):
    # Guard against empty df or missing columns
    if df is None or df.empty or x not in df.columns or y not in df.columns:
        return go.Figure()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df[x], y=df[y],
        marker=dict(color="#D526B7", line=dict(color="#2BFF88", width=2))
    ))
    fig.update_layout(
        title=title,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    return fig

def neon_line_chart(df, x, y, title):
    if df is None or df.empty or x not in df.columns or y not in df.columns:
        return go.Figure()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x], y=df[y],
        mode="lines+markers",
        line=dict(color="#8338FF", width=4),
        marker=dict(color="#2BFF88", size=8)
    ))
    fig.update_layout(
        title=title,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    return fig

# ----------------------------------------
# Load Data
# ----------------------------------------
@st.cache_data(ttl=3600)
def load_data():
    ensure_curated_files()

    tracks = robust_read_csv(CURATED_DIR / "top_tracks.csv")
    artists = robust_read_csv(CURATED_DIR / "top_artists.csv")
    recently = robust_read_csv(CURATED_DIR / "recently_played.csv")

    genre = robust_read_csv(CURATED_DIR / "genre_summary.csv")
    # Normalize genre
    if genre.shape[1] >= 2:
        genre = genre.iloc[:, :2]
        genre.columns = ["genre", "count"]
    else:
        genre.columns = ["genre"]
        genre["count"] = 1

    hourly = robust_read_csv(CURATED_DIR / "listening_by_hour.csv")
    if hourly.shape[1] >= 2:
        hourly = hourly.iloc[:, :2]
        hourly.columns = ["hour", "count"]
    else:
        hourly.columns = ["hour"]
        hourly["count"] = 1

    daily = robust_read_csv(CURATED_DIR / "listening_daily.csv")
    if daily.shape[1] >= 2:
        daily = daily.iloc[:, :2]
        daily.columns = ["date", "plays"]
    else:
        daily.columns = ["date"]
        daily["plays"] = 1
    daily["date"] = pd.to_datetime(daily["date"], errors="coerce")
    daily = daily.dropna(subset=["date"]).reset_index(drop=True)

    duration_stats = robust_read_csv(CURATED_DIR / "duration_stats.csv")
    if duration_stats.shape[1] >= 2:
        duration_stats = duration_stats.iloc[:, :2]
        duration_stats.columns = ["metric", "value"]

    artist_freq = robust_read_csv(CURATED_DIR / "artist_frequency.csv")
    if artist_freq.shape[1] >= 2:
        artist_freq = artist_freq.iloc[:, :2]
        artist_freq.columns = ["artist", "count"]
    else:
        artist_freq.columns = ["artist"]
        artist_freq["count"] = 1

    if "duration_min" not in tracks.columns and "duration_ms" in tracks.columns:
        tracks["duration_min"] = tracks["duration_ms"] / 60000

    return tracks, artists, genre, hourly, daily, duration_stats, artist_freq, recently

tracks, artists, genre, hourly, daily, duration_stats, artist_freq, recently = load_data()

# ----------------------------------------
# PAGES
# ----------------------------------------

# -------------------- Overview --------------------
if st.session_state["page"] == "Overview":
    st.markdown("<div class='section'>", unsafe_allow_html=True)

    st.markdown("""
    <h1 style="font-weight:900; letter-spacing:-1px;">🎧 Your Personal Spotify Wrapped</h1>
    <p style="font-size:18px; opacity:0.8;">
        Your personalized listening story, beautifully visualized.
    </p>
    """, unsafe_allow_html=True)

    total_minutes = round(tracks["duration_min"].sum(), 2) if "duration_min" in tracks.columns else 0
    unique_tracks = tracks["name"].nunique() if "name" in tracks.columns else 0
    unique_artists = artists["name"].nunique() if "name" in artists.columns else 0

    c1, c2, c3 = st.columns(3)

    c1.markdown(f"<div class='metric-box'><div class='metric-label'>🎵 Total Minutes</div><div class='metric-value'>{total_minutes}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-box'><div class='metric-label'>🎶 Unique Tracks</div><div class='metric-value'>{unique_tracks}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-box'><div class='metric-label'>🧑‍🎤 Unique Artists</div><div class='metric-value'>{unique_artists}</div></div>", unsafe_allow_html=True)

    st.subheader("Top 5 Artists")
    fig = neon_bar_chart(artist_freq.head(5), "artist", "count", "Top Artists")
    st.plotly_chart(fig, width="stretch")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------- Top Tracks --------------------
elif st.session_state["page"] == "Top Tracks":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.title("Top Tracks")
    st.dataframe(tracks[["name", "artists", "time_range", "duration_min"]].fillna("-"))
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------- Top Artists --------------------
elif st.session_state["page"] == "Top Artists":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.title("Top Artists")
    st.subheader("Artist Carousel")

    st.markdown("<div class='carousel-container'>", unsafe_allow_html=True)

    for _, row in artists.head(15).iterrows():
        name = row.get("name", "Unknown")
        genres_raw = row.get("genres", "[]")
        try:
            genres = ast.literal_eval(genres_raw) if isinstance(genres_raw, str) else genres_raw
        except Exception:
            genres = []
        st.markdown(f"""
        <div class='artist-card'>
            <h4>{name}</h4>
            <p style='font-size:12px; opacity:0.8'>{' • '.join(genres[:3])}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Wrapped Slide")
    # Guard popularity column
    if "popularity" in artists.columns:
        slide = neon_bar_chart(artists.head(5), "name", "popularity", "Your Top Artists")
        st.plotly_chart(slide, width="stretch")
        try:
            png = pio.to_image(slide, format="png")
            st.download_button("Download PNG", png, "top_artists.png", "image/png")
        except Exception:
            st.warning("Install kaleido: pip install kaleido")
    else:
        st.info("Popularity data not available for artists.")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------- Genre Insights --------------------
elif st.session_state["page"] == "Genre Insights":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.title("Genre Insights")
    fig = neon_bar_chart(genre, "genre", "count", "Genres")
    st.plotly_chart(fig, width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------- Listening Patterns --------------------
elif st.session_state["page"] == "Listening Patterns":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.title("Listening Patterns")
    fig = neon_bar_chart(hourly.sort_values("hour"), "hour", "count", "By Hour")
    st.plotly_chart(fig, width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------- Daily Trend --------------------
elif st.session_state["page"] == "Daily Trend":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.title("Daily Trend")
    fig = neon_line_chart(daily.sort_values("date"), "date", "plays", "Daily Listening")
    st.plotly_chart(fig, width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------- Duration Stats --------------------
elif st.session_state["page"] == "Duration Stats":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.title("Duration Statistics")
    st.dataframe(duration_stats)
    fig = neon_bar_chart(tracks.reset_index(), "index", "duration_min", "Track Duration Distribution")
    st.plotly_chart(fig, width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)
