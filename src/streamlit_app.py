import streamlit as st
import pandas as pd
from pathlib import Path
import ast

CURATED_DIR = Path("data/curated")

# -----------------------------
# Load curated datasets
# -----------------------------
@st.cache_data
def load_data():
    tracks = pd.read_csv(CURATED_DIR / "top_tracks.csv")
    artists = pd.read_csv(CURATED_DIR / "top_artists.csv")
    recently = pd.read_csv(CURATED_DIR / "recently_played.csv")

    genre_summary = pd.read_csv(CURATED_DIR / "genre_summary.csv", header=None, names=["genre", "count"])
    hourly = pd.read_csv(CURATED_DIR / "listening_by_hour.csv", header=None, names=["hour", "count"])
    daily = pd.read_csv(CURATED_DIR / "listening_daily.csv", header=None, names=["date", "count"])
    duration_stats = pd.read_csv(CURATED_DIR / "duration_stats.csv", header=None, names=["metric", "value"])
    artist_freq = pd.read_csv(CURATED_DIR / "artist_frequency.csv", header=None, names=["artist", "count"])

    return {
        "tracks": tracks,
        "artists": artists,
        "recently": recently,
        "genre_summary": genre_summary,
        "hourly": hourly,
        "daily": daily,
        "duration_stats": duration_stats,
        "artist_freq": artist_freq
    }


data = load_data()
tracks = data["tracks"]
artists = data["artists"]
genre = data["genre_summary"]
hourly = data["hourly"]
daily = data["daily"]
duration_stats = data["duration_stats"]
artist_freq = data["artist_freq"]


# -----------------------------
# Page config & Global CSS
# -----------------------------
st.set_page_config(page_title="Personal Spotify Wrapped", layout="wide")

st.markdown("""
<style>

body {
    background: linear-gradient(135deg,
        #D526B7 0%,
        #8338FF 25%,
        #2BFF88 60%,
        #FFDD00 100%
    ) fixed;
    color: white;
}

/* Remove white backgrounds */
.main, .block-container {
    background: transparent !important;
}

h1, h2, h3, h4 {
    font-weight: 800;
    letter-spacing: -1px;
    text-shadow: 0px 0px 12px rgba(0,0,0,0.4);
}

/* Wrapped-style stat cards */
.metric-card {
    padding: 25px;
    border-radius: 24px;
    text-align: center;
    margin-bottom: 25px;

    background: linear-gradient(135deg,
        rgba(255,255,255,0.08),
        rgba(255,255,255,0.02)
    );

    border: 2px solid rgba(255,255,255,0.25);
    backdrop-filter: blur(18px);

    box-shadow: 0 0 25px rgba(255,255,255,0.12);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.metric-card:hover {
    transform: scale(1.04);
    box-shadow: 0 0 40px rgba(255,255,255,0.35);
}


/* Artist cards — Wrapped Edition */
.artist-card {
    display: inline-block;
    background: linear-gradient(160deg,
        rgba(255,255,255,0.08),
        rgba(255,255,255,0.02)
    );
    padding: 18px;
    border-radius: 20px;
    width: 240px;
    margin: 10px 15px 10px 0;

    border: 1px solid rgba(255,255,255,0.15);
    backdrop-filter: blur(14px);

    box-shadow: 0 0 18px rgba(0,0,0,0.25);
    transition: all 0.3s ease;
}

.artist-card:hover {
    transform: translateY(-6px) scale(1.07);
    box-shadow: 0 0 35px rgba(255,255,255,0.35);
}

/* Scrollable horizontal artist list */
::-webkit-scrollbar {
    height: 8px;
}
::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.25);
    border-radius: 4px;
}

</style>
""", unsafe_allow_html=True)



# -----------------------------
# Sidebar Navigation
# -----------------------------
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio(
    "Go to:",
    [
        "🏠 Overview",
        "🎵 Top Tracks",
        "👨‍🎤 Top Artists",
        "🎧 Genre Insights",
        "⏰ Listening Patterns",
        "📈 Daily Trend",
        "⏱ Duration Stats",
    ]
)


# -----------------------------
# Overview Page
# -----------------------------
if page == "🏠 Overview":
    st.title("🎧 Your Personal Spotify Wrapped")
    st.write("A stylish Wrapped recreation built with Python + Spotify API + Streamlit.")

    total_minutes = round(tracks["duration_min"].sum(), 2)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h2>🎵 Total Minutes</h2>
            <h1>{total_minutes}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <h2>🎶 Unique Tracks</h2>
            <h1>{tracks['name'].nunique()}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <h2>👨‍🎤 Unique Artists</h2>
            <h1>{artists['name'].nunique()}</h1>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Top 5 Artists (Frequency)")

    st.bar_chart(artist_freq.set_index("artist")["count"])



# -----------------------------
# Top Tracks Page
# -----------------------------
elif page == "🎵 Top Tracks":
    st.title("🎵 Your Top Tracks")
    st.write("Your most played tracks across all time ranges.")

    st.dataframe(tracks[["name", "artists", "time_range", "duration_min"]])



# -----------------------------
# Top Artists Page — WITH STYLISH CARDS
# -----------------------------
elif page == "👨‍🎤 Top Artists":
    st.title("👨‍🎤 Top Artists")
    st.write("Your top artists, Wrapped-style.")

    st.subheader("🎨 Artist Cards Preview")

    for idx, row in artists.head(10).iterrows():
        name = row["name"]
        genres = row["genres"]

        try:
            genres = ast.literal_eval(genres)
        except:
            genres = []

        with st.container():
            st.markdown(f"""
            <div class='artist-card'>
                <h3>{name}</h3>
                <p><b>Genres:</b> {", ".join(genres[:3])}</p>
                <p><b>Popularity:</b> {row.get('popularity', 'NA')}</p>
            </div>
            """, unsafe_allow_html=True)



# -----------------------------
# Genre Insights
# -----------------------------
elif page == "🎧 Genre Insights":
    st.title("🎧 Genre Insights")
    st.write("Your genre taste breakdown.")

    st.bar_chart(genre.set_index("genre")["count"])



# -----------------------------
# Listening Patterns (Hour of Day)
# -----------------------------
elif page == "⏰ Listening Patterns":
    st.title("⏰ Listening Patterns by Hour")
    st.write("Your hourly listening habits.")

    hourly_sorted = hourly.sort_values("hour")
    hourly_sorted = hourly_sorted.set_index("hour")

    st.bar_chart(hourly_sorted)



# -----------------------------
# Daily Listening Trend
# -----------------------------
elif page == "📈 Daily Trend":
    st.title("📈 Daily Listening Trend")

    daily = pd.read_csv(CURATED_DIR / "listening_daily.csv")

    # Remove header-as-data row
    daily = daily[daily.columns]  # force consistent structure
    daily = daily[daily[daily.columns[0]] != "date"]

    # Convert date column safely
    daily[daily.columns[0]] = pd.to_datetime(daily[daily.columns[0]], errors="coerce")
    daily = daily.dropna(subset=[daily.columns[0]])

    # Rename columns to consistent names
    daily.columns = ["date", "plays"]

    # Set index for plotting
    daily = daily.set_index("date")

    st.line_chart(daily["plays"])




# -----------------------------
# Duration Stats
# -----------------------------
elif page == "⏱ Duration Stats":
    st.title("⏱ Track Duration Stats")

    st.dataframe(duration_stats)

    st.subheader("Track Duration Distribution")
    st.bar_chart(tracks["duration_min"])
