from typing import Any

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity


class SongRecommender:
    def __init__(self, df):
        self.df = df.copy()

        # Features used for recommendation
        self.features = [
            "danceability", "energy", "valence",
            "tempo", "acousticness", "liveness"
        ]

        # Fill missing values
        self.df[self.features] = self.df[self.features].fillna(0)

        # Scale features
        self.scaler = StandardScaler()
        self.feature_matrix = self.scaler.fit_transform(self.df[self.features])

    # 🔍 Find song index
    def _get_index(self, song_name, artist=None):
        if artist:
            match = self.df[
                (self.df["track_name"].str.lower() == song_name.lower()) &
                (self.df["artists"].str.lower() == artist.lower())
            ]
        else:
            match = self.df[
                self.df["track_name"].str.lower() == song_name.lower()
            ]

        if match.empty:
            raise ValueError("Song not found")

        return match.index[0]

    # 🎵 Recommend by song
    def recommend(self, song_name, artist=None, n=10):
        idx = self._get_index(song_name, artist)

        # 👉 ONLY compare this song to others (NOT full matrix)
        query_vec = self.feature_matrix[idx].reshape(1, -1)
        similarities = cosine_similarity(query_vec, self.feature_matrix)[0]

        # Sort by similarity
        similar_indices = np.argsort(similarities)[::-1][1:n+1]

        return self.df.iloc[similar_indices][

            ["track_name", "artists"]

        ]

    # 🎯 Recommend by mood/features
    def recommend_by_features(self, n=10, **kwargs):
        # Create input vector
        input_vec = np.zeros(len(self.features))

        for i, feature in enumerate(self.features):
            if feature in kwargs:
                input_vec[i] = kwargs[feature]

        # Scale input same as dataset
        input_vec = self.scaler.transform([input_vec])

        similarities = cosine_similarity(input_vec, self.feature_matrix)[0]
        similar_indices = np.argsort(similarities)[::-1][:n]

        return self.df.iloc[similar_indices][
            ["track_name", "artists"]
        ]


# =========================
# 🚀 RUN DEMO
# =========================
if __name__ == "__main__":
    df = pd.read_csv(r"c:\Users\anusha\OneDrive\Documents\Downloads\songrecommender\dataset.csv")  

    rec = SongRecommender(df)

    print("=" * 60)
    print("DEMO 1 – Recommend by song name")
    print("=" * 60)

    try:
        recs = rec.recommend("Blinding Lights", artist="The Weeknd", n=10)
        print(recs.to_string(index=False))
    except ValueError as e:
        print(f"⚠️ {e}")

    print("\n" + "=" * 60)
    print("DEMO 2 – Mood-based: high energy, high danceability")
    print("=" * 60)

    mood_recs = rec.recommend_by_features(
        danceability=0.85,
        energy=0.9,
        valence=0.75,
        tempo=130,
        n=10
    )

    print(mood_recs.to_string(index=False))