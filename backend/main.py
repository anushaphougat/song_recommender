"""
FastAPI Backend for Song Recommendation System
===============================================
Run with:
    uvicorn main:app --reload --port 8000

Make sure dataset.csv is accessible at the DATASET_PATH below.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

# ── Config ───────────────────────────────────────────────────────────────────
DATASET_PATH = Path(__file__).resolve().parent.parent / "dataset.csv"

FEATURE_COLS = [
    "danceability", "energy", "loudness", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo"
]
POPULARITY_WEIGHT = 0.2

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(title="Song Recommender API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load data once at startup ─────────────────────────────────────────────────
df: pd.DataFrame = None
matrix: np.ndarray = None
pop_norm: np.ndarray = None


@app.on_event("startup")
def load_data():
    global df, matrix, pop_norm
    try:
        df = pd.read_csv(DATASET_PATH, index_col=0)
    except FileNotFoundError:
        raise RuntimeError(f"dataset.csv not found at: {DATASET_PATH}")

    df.columns = df.columns.str.strip()
    df = df.drop_duplicates(subset=["track_name", "artists"])
    df = df.dropna(subset=FEATURE_COLS + ["track_name", "artists", "popularity"])
    df = df.reset_index(drop=True)

    scaler = MinMaxScaler()
    matrix = scaler.fit_transform(df[FEATURE_COLS])
    pop = df["popularity"].values.astype(float)
    pop_norm = (pop - pop.min()) / (pop.max() - pop.min() + 1e-9)


# ── Request / Response models ─────────────────────────────────────────────────
class SongRequest(BaseModel):
    track_name: str
    artist: Optional[str] = None
    n: int = 10
    same_genre: bool = False


class MoodRequest(BaseModel):
    danceability: float = 0.7
    energy: float = 0.8
    valence: float = 0.6
    tempo: float = 120.0
    n: int = 10


# ── Helpers ───────────────────────────────────────────────────────────────────
def _recommend_by_song(track_name: str, artist: Optional[str], n: int, same_genre: bool):
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
    return seed, res


def _recommend_by_mood(dance: float, energy: float, valence: float, tempo: float, n: int):
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
    return res.sort_values("_hybrid", ascending=False).head(n)


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/stats")
def get_stats():
    return {
        "total_songs": int(len(df)),
        "total_genres": int(df["track_genre"].nunique()),
        "total_artists": int(df["artists"].nunique()),
    }


@app.get("/genres")
def get_genres():
    genre_counts = (
        df["track_genre"]
        .value_counts()
        .reset_index()
        .rename(columns={"track_genre": "genre", "count": "count"})
    )
    return genre_counts.to_dict(orient="records")


@app.get("/top-songs")
def get_top_songs():
    top = df.nlargest(10, "popularity")[["track_name", "artists", "popularity", "track_genre"]]
    return top.to_dict(orient="records")


@app.get("/genre-songs")
def get_genre_songs(genre: str, limit: int = 20):
    genre_df = df[df["track_genre"] == genre].nlargest(limit, "popularity")[
        ["track_name", "artists", "popularity"] + FEATURE_COLS[:4]
    ]
    return genre_df.to_dict(orient="records")


@app.post("/recommend/song")
def recommend_by_song(req: SongRequest):
    seed, recs = _recommend_by_song(req.track_name, req.artist, req.n, req.same_genre)
    if recs is None:
        raise HTTPException(status_code=404, detail=f"Song '{req.track_name}' not found.")

    seed_features = {f: round(float(seed[f]), 3) for f in FEATURE_COLS}
    recommendations = []
    for _, row in recs.iterrows():
        recommendations.append({
            "track_name": row["track_name"],
            "artists": row["artists"],
            "track_genre": row["track_genre"],
            "popularity": int(row["popularity"]),
            "similarity": round(float(row["_sim"]), 3),
            "score": round(float(row["_hybrid"]), 3),
        })

    return {
        "seed": {
            "track_name": seed["track_name"],
            "artists": seed["artists"],
            "track_genre": seed["track_genre"],
            "popularity": int(seed["popularity"]),
            "features": seed_features,
        },
        "recommendations": recommendations,
    }


@app.post("/recommend/mood")
def recommend_by_mood(req: MoodRequest):
    recs = _recommend_by_mood(req.danceability, req.energy, req.valence, req.tempo, req.n)
    result = []
    for _, row in recs.iterrows():
        result.append({
            "track_name": row["track_name"],
            "artists": row["artists"],
            "track_genre": row["track_genre"],
            "popularity": int(row["popularity"]),
            "score": round(float(row["_hybrid"]), 3),
        })
    return {"recommendations": result}


@app.get("/")
def root():
    return {"message": "Song Recommender API is running. Visit /docs for API docs."}

