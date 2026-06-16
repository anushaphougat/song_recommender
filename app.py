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
    page_title="🎵 Song Recommender",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

FEATURE_COLS = [
    "danceability", "energy", "loudness", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo"
]
POPULARITY_WEIGHT = 0.2


# ─── Data & Model (cached) ───────────────────────────────────────────────────
DATASET_PATH = r"C:\Users\anusha\OneDrive\Documents\Downloads\songrecommender\dataset.csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATASET_PATH, index_col=0)
    except FileNotFoundError:
        st.error(f"❌ dataset.csv not found at: {DATASET_PATH}")
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
st.title("🎵 Song Recommendation System")
st.caption("Hybrid Content-Based + Popularity Filtering · Spotify Tracks Dataset")

df = load_data()
matrix, pop_norm = build_model(df)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    n_recs = st.slider("Number of recommendations", 5, 25, 10)
    same_genre = st.checkbox("Restrict to same genre", value=False)
    st.markdown("---")
    st.metric("Total Songs", f"{len(df):,}")
    st.metric("Genres", df["track_genre"].nunique())
    st.metric("Artists", df["artists"].nunique())

# ── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🎵 Find by Song", "🎭 Find by Mood", "📊 Explore Dataset"])

# Tab 1 — Song-based
with tab1:
    st.subheader("Recommend based on a song you like")
    col1, col2 = st.columns([2, 1])
    with col1:
        track_input = st.text_input("Song name", placeholder="e.g. Blinding Lights")
    with col2:
        artist_input = st.text_input("Artist (optional)", placeholder="e.g. The Weeknd")

    if st.button("🔍 Get Recommendations", key="song_btn"):
        if not track_input:
            st.warning("Please enter a song name.")
        else:
            with st.spinner("Finding similar songs..."):
                seed, recs = get_recommendations(df, matrix, pop_norm, track_input, artist_input, n_recs, same_genre)
            if recs is None:
                st.error(f"Song **'{track_input}'** not found. Try a different spelling or add the artist name.")
            else:
                st.success(f"Showing recommendations for **{seed['track_name']}** by {seed['artists']}")

                # Seed song info
                with st.expander("🎵 Seed song audio features"):
                    feat_df = pd.DataFrame({
                        "Feature": FEATURE_COLS,
                        "Value": [round(seed[f], 3) for f in FEATURE_COLS]
                    })
                    st.dataframe(feat_df, use_container_width=True, hide_index=True)

                # Recommendations table
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
        dance = st.slider("💃 Danceability", 0.0, 1.0, 0.7, 0.05)
        energy = st.slider("⚡ Energy", 0.0, 1.0, 0.8, 0.05)
    with col2:
        valence = st.slider("😊 Positivity (Valence)", 0.0, 1.0, 0.6, 0.05)
        tempo = st.slider("🥁 Tempo (BPM)", 60, 200, 120, 5)

    # Mood label
    if energy > 0.7 and dance > 0.7:
        mood_label = "🔥 High-Energy Party"
    elif valence > 0.7 and energy < 0.5:
        mood_label = "☀️ Happy & Chill"
    elif valence < 0.3 and energy < 0.5:
        mood_label = "🌧️ Melancholic"
    elif energy > 0.7 and valence < 0.4:
        mood_label = "💪 Intense Workout"
    else:
        mood_label = "🎵 Mixed Mood"
    st.info(f"Detected mood: **{mood_label}**")

    if st.button("🔍 Get Mood Recommendations", key="mood_btn"):
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

    # Genre filter
    st.markdown("**Browse by Genre**")
    genre = st.selectbox("Select a genre", sorted(df["track_genre"].unique()))
    genre_df = df[df["track_genre"] == genre].nlargest(20, "popularity")[
        ["track_name", "artists", "popularity"] + FEATURE_COLS[:4]
    ]
    st.dataframe(genre_df.rename(columns={
        "track_name": "Song", "artists": "Artist", "popularity": "Popularity"
    }), use_container_width=True, hide_index=True)