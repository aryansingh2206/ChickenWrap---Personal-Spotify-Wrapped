# 🎧 Personal Spotify Wrapped

A clean, fast, and fully local recreation of **Spotify Wrapped** — built using Python, Pandas, and Streamlit.  
This project fetches your listening data using the Spotify Web API, processes it via an ETL pipeline, and visualizes insights using a stylish neon-wrapped dashboard.

---

## 🚀 Features

### ✔ Data Fetching (Spotify API)
- Top Tracks (short, medium, long term)
- Top Artists
- Recently Played tracks
- All data saved locally (`data/raw/`)

### ✔ ETL Pipeline
- Normalize track & artist metadata  
- Calculate track durations  
- Extract daily and hourly listening patterns  
- Generate curated datasets (`data/curated/`)

### ✔ Wrapped-Style Analytics
- Top tracks & top artists
- Genre breakdown
- Listening trend by hour
- Daily activity trend
- Duration statistics
- Artist frequency ranking

### ✔ Wrapped-Inspired Dashboard (Streamlit)
- Neon Spotify Wrapped theme  
- Glassmorphism UI  
- Highlight cards (total minutes, top artists, etc.)  
- Horizontal artist cards  
- Gradient backgrounds  
- Interactive charts  

---

## 🏗 Tech Stack

- **Python 3.10+**
- **Pandas**
- **Requests**
- **Streamlit**
- **dotenv**
- **Spotify Web API**

---

## 📁 Project Structure

```

personal-wrapped/
│
├── data/
│   ├── raw/          # Raw Spotify API JSON files
│   └── curated/      # Cleaned CSV + summary outputs
│
├── src/
│   ├── auth.py               # OAuth login (Authorization Code Flow)
│   ├── fetch_data.py         # Data ingestion from Spotify API
│   ├── etl.py                # Transform + summary extraction
│   ├── analysis.py           # Additional derived insights
│   └── streamlit_app.py      # Wrapped-style dashboard
│
├── .env                      # API credentials + tokens
├── .gitignore
├── requirements.txt
└── README.md

````

---

## 🔐 Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/your-username/personal-wrapped.git
cd personal-wrapped
````

### 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Configure Spotify App

Create an app at: [https://developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
Add this Redirect URI:

```
http://127.0.0.1:8888/callback
```

Create `.env` with:

```
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret
REDIRECT_URI=http://127.0.0.1:8888/callback
```

Run login:

```bash
python src/auth.py
```

This will save `ACCESS_TOKEN` and `REFRESH_TOKEN`.

---

## 📥 Fetch Data

```bash
python src/fetch_data.py
```

This generates:

```
data/raw/
  top_tracks_*.json
  top_artists_*.json
  recently_played.json
```

---

## 🔄 Run ETL

```bash
python src/etl.py
```

Generates:

```
data/curated/
  top_tracks.csv
  top_artists.csv
  recently_played.csv
  genre_summary.csv
  listening_by_hour.csv
  listening_daily.csv
  artist_frequency.csv
  wrapped_summary.json
```

---

## 📊 Run the Dashboard

```bash
streamlit run src/streamlit_app.py
```

Then open the app in your browser:

```
http://localhost:8501
```

---

## 📌 Notes

* This version is **Lite Mode** (no audio-features API used).
* 100% local — no cloud dependencies.
* Wrapped theme includes neon gradients, glass cards, and Spotify-style typography.

