"""
Song Recommendation System — Streamlit Web App
===============================================
Run with:
    streamlit run app.py

Make sure dataset.csv is in the same directory.
"""

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Song Recommender",
    page_icon="●",
    layout="wide",
    initial_sidebar_state="expanded"
)

FEATURE_COLS = [
    "danceability", "energy", "loudness", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo"
]
POPULARITY_WEIGHT = 0.2

# ── Black & white theme ──────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* App background */
    .stApp {
        background-color: #ffffff;
        color: #111111;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #222222;
    }
    section[data-testid="stSidebar"] * {
        color: #f5f5f5 !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #333333;
    }

    /* Titles */
    h1 {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #0a0a0a;
        border-bottom: 2px solid #0a0a0a;
        padding-bottom: 0.4rem;
    }
    h2, h3 {
        font-family: 'Space Grotesk', sans-serif;
        color: #0a0a0a;
        font-weight: 600;
    }

    /* Caption */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #555555 !important;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        font-size: 0.75rem !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 1px solid #dddddd;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #888888;
        font-weight: 600;
        border-radius: 0px;
        padding: 10px 18px;
    }
    .stTabs [aria-selected="true"] {
        color: #0a0a0a !important;
        border-bottom: 2px solid #0a0a0a !important;
        background-color: transparent !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #0a0a0a;
        color: #ffffff;
        border: 1px solid #0a0a0a;
        border-radius: 2px;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        font-size: 0.8rem;
        padding: 0.55rem 1.2rem;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        background-color: #ffffff;
        color: #0a0a0a;
        border: 1px solid #0a0a0a;
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput input {
        border: 1px solid #cccccc !important;
        border-radius: 2px !important;
        background-color: #fafafa !important;
        color: #0a0a0a !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #0a0a0a !important;
        box-shadow: none !important;
    }

    /* Sliders */
    .stSlider [data-baseweb="slider"] > div > div {
        background: #0a0a0a !important;
    }
    .stSlider [role="slider"] {
        background-color: #0a0a0a !important;
        border: 2px solid #0a0a0a !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background-color: #141414;
        border: 1px solid #2a2a2a;
        border-radius: 2px;
        padding: 0.8rem 0.6rem;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
    }
    [data-testid="stMetricLabel"] {
        color: #999999 !important;
        text-transform: uppercase;
        font-size: 0.7rem !important;
        letter-spacing: 0.05em;
    }

    /* Dataframes */
    [data-testid="stDataFrame"] {
        border: 1px solid #dddddd;
        border-radius: 2px;
    }

    /* Alerts (success/warning/error/info) — monochrome */
    div[data-baseweb="notification"], .stAlert {
        border-radius: 2px !important;
        border: 1px solid #0a0a0a !important;
        background-color: #f5f5f5 !important;
        color: #0a0a0a !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #0a0a0a;
        border: 1px solid #dddddd;
        border-radius: 2px;
    }

    /* Divider */
    hr {
        border-color: #dddddd;
    }
</style>
""", unsafe_allow_html=True)

# ─── Data & Model (cached) ───────────────────────────────────────────────────
DATASET_PATH = r"C:\Users\anusha\OneDrive\Documents\Downloads\songrecommender\dataset.csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATASET_PATH, index_col=0)
    except FileNotFoundError:
        st.error(f"dataset.csv not found at: {DATASET_PATH}")
        st.stop()
    df.columns = df.columns.str.strip()
    df = df.drop_duplicates(subset=["track_name", "artists"])
    df = df.dropna(subset=FEATURE_COLS + ["track_name", "artists", "popularity"])
    df = df.reset_index(drop=True)
    return df

@st.cache_data
def build_model(df):
    scaler = MinMaxScaler()
    matrix = scaler.fit_transform(df[FEATURE_COLS])
    pop = df["popularity"].values.astype(float)
    pop_norm = (pop - pop.min()) / (pop.max() - pop.min() + 1e-9)
    return matrix, pop_norm

def get_recommendations(df, matrix, pop_norm, track_name, artist, n, same_genre):
    mask = df["track_name"].str.lower() == track_name.lower()
    if artist:
        mask &= df["artists"].str.lower().str.contains(artist.lower())
    matches = df[mask]
    if matches.empty:
        return None, None
    idx = matches.index[0]
    seed = df.loc[idx]
    seed_vec = matrix[idx].reshape(1, -1)
    sim_scores = cosine_similarity(seed_vec, matrix)[0]
    hybrid = (1 - POPULARITY_WEIGHT) * sim_scores + POPULARITY_WEIGHT * pop_norm
    res = df.copy()
    res["_sim"] = sim_scores
    res["_hybrid"] = hybrid
    res = res[res.index != idx]
    if same_genre:
        res = res[res["track_genre"] == seed["track_genre"]]
    res = res.sort_values("_hybrid", ascending=False).head(n)
    return seed, res[["track_name", "artists", "track_genre", "popularity", "_sim", "_hybrid"]]

def get_mood_recommendations(df, matrix, pop_norm, dance, energy, valence, tempo, n):
    means = df[FEATURE_COLS].mean().to_dict()
    query = {f: means[f] for f in FEATURE_COLS}
    query.update({"danceability": dance, "energy": energy, "valence": valence, "tempo": tempo})
    sc = MinMaxScaler()
    sc.fit(df[FEATURE_COLS])
    q = sc.transform(np.array([[query[f] for f in FEATURE_COLS]]))
    sim = cosine_similarity(q, matrix)[0]
    hybrid = (1 - POPULARITY_WEIGHT) * sim + POPULARITY_WEIGHT * pop_norm
    res = df.copy()
    res["_hybrid"] = hybrid
    return res.sort_values("_hybrid", ascending=False).head(n)[
        ["track_name", "artists", "track_genre", "popularity", "_hybrid"]
    ]

# ─── App Layout ──────────────────────────────────────────────────────────────
st.title("SONG RECOMMENDATION SYSTEM")
st.caption("Hybrid Content-Based + Popularity Filtering · Spotify Tracks Dataset")

df = load_data()
matrix, pop_norm = build_model(df)

# Sidebar
with st.sidebar:
    st.header("Settings")
    n_recs = st.slider("Number of recommendations", 5, 25, 10)
    same_genre = st.checkbox("Restrict to same genre", value=False)
    st.markdown("---")
    st.metric("Total Songs", f"{len(df):,}")
    st.metric("Genres", df["track_genre"].nunique())
    st.metric("Artists", df["artists"].nunique())

# ── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["FIND BY SONG", "FIND BY MOOD", "EXPLORE DATASET"])

# Tab 1 — Song-based
with tab1:
    st.subheader("Recommend based on a song you like")
    col1, col2 = st.columns([2, 1])
    with col1:
        track_input = st.text_input("Song name", placeholder="e.g. Blinding Lights")
    with col2:
        artist_input = st.text_input("Artist (optional)", placeholder="e.g. The Weeknd")

    if st.button("GET RECOMMENDATIONS", key="song_btn"):
        if not track_input:
            st.warning("Please enter a song name.")
        else:
            with st.spinner("Finding similar songs..."):
                seed, recs = get_recommendations(df, matrix, pop_norm, track_input, artist_input, n_recs, same_genre)

            if recs is None:
                st.error(f"Song '{track_input}' not found. Try a different spelling or add the artist name.")
            else:
                st.success(f"Showing recommendations for {seed['track_name']} by {seed['artists']}")

                with st.expander("Seed song audio features"):
                    feat_df = pd.DataFrame({
                        "Feature": FEATURE_COLS,
                        "Value": [round(seed[f], 3) for f in FEATURE_COLS]
                    })
                    st.dataframe(feat_df, use_container_width=True, hide_index=True)

                recs_display = recs.rename(columns={
                    "track_name": "Song", "artists": "Artist",
                    "track_genre": "Genre", "popularity": "Popularity",
                    "_sim": "Similarity", "_hybrid": "Score"
                })
                recs_display["Similarity"] = recs_display["Similarity"].round(3)
                recs_display["Score"] = recs_display["Score"].round(3)
                st.dataframe(recs_display, use_container_width=True, hide_index=True)

# Tab 2 — Mood-based
with tab2:
    st.subheader("Describe a mood and get song recommendations")
    col1, col2 = st.columns(2)
    with col1:
        dance = st.slider("Danceability", 0.0, 1.0, 0.7, 0.05)
        energy = st.slider("Energy", 0.0, 1.0, 0.8, 0.05)
    with col2:
        valence = st.slider("Positivity (Valence)", 0.0, 1.0, 0.6, 0.05)
        tempo = st.slider("Tempo (BPM)", 60, 200, 120, 5)

    if energy > 0.7 and dance > 0.7:
        mood_label = "HIGH-ENERGY PARTY"
    elif valence > 0.7 and energy < 0.5:
        mood_label = "HAPPY & CHILL"
    elif valence < 0.3 and energy < 0.5:
        mood_label = "MELANCHOLIC"
    elif energy > 0.7 and valence < 0.4:
        mood_label = "INTENSE WORKOUT"
    else:
        mood_label = "MIXED MOOD"

    st.info(f"Detected mood: {mood_label}")

    if st.button("GET MOOD RECOMMENDATIONS", key="mood_btn"):
        with st.spinner("Finding songs for your mood..."):
            mood_recs = get_mood_recommendations(df, matrix, pop_norm, dance, energy, valence, tempo, n_recs)

        mood_display = mood_recs.rename(columns={
            "track_name": "Song", "artists": "Artist",
            "track_genre": "Genre", "popularity": "Popularity",
            "_hybrid": "Score"
        })
        mood_display["Score"] = mood_display["Score"].round(3)
        st.dataframe(mood_display, use_container_width=True, hide_index=True)

# Tab 3 — Explore
with tab3:
    st.subheader("Explore the Dataset")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Top 10 Genres**")
        st.dataframe(
            df["track_genre"].value_counts().head(10).reset_index()
              .rename(columns={"track_genre": "Genre", "count": "Songs"}),
            use_container_width=True, hide_index=True
        )
    with col2:
        st.markdown("**Top 10 Most Popular Songs**")
        top_songs = df.nlargest(10, "popularity")[["track_name", "artists", "popularity", "track_genre"]]
        st.dataframe(top_songs.rename(columns={
            "track_name": "Song", "artists": "Artist",
            "popularity": "Popularity", "track_genre": "Genre"
        }), use_container_width=True, hide_index=True)

    st.markdown("**Audio Feature Statistics**")
    st.dataframe(df[FEATURE_COLS + ["popularity"]].describe().round(3), use_container_width=True)

    st.markdown("**Browse by Genre**")
    genre = st.selectbox("Select a genre", sorted(df["track_genre"].unique()))
    genre_df = df[df["track_genre"] == genre].nlargest(20, "popularity")[
        ["track_name", "artists", "popularity"] + FEATURE_COLS[:4]
    ]
    st.dataframe(genre_df.rename(columns={
        "track_name": "Song", "artists": "Artist", "popularity": "Popularity"
    }), use_container_width=True, hide_index=True)