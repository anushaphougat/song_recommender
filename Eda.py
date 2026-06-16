"""
Song Recommendation System — EDA & Analysis
============================================
Run this script to explore the dataset before training the recommender.
Generates charts saved as PNG files in the ./plots/ directory.

Install deps first:
    pip install pandas numpy matplotlib seaborn scikit-learn
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

# ── Style ───────────────────────────────────────────────────────────────────
sns.set_theme(style="darkgrid", palette="muted")
PLOT_DIR = "./plots"
os.makedirs(PLOT_DIR, exist_ok=True)

FEATURE_COLS = [
    "danceability", "energy", "loudness", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo"
]

CSV_PATH = r"c:\Users\anusha\OneDrive\Documents\Downloads\songrecommender\dataset.csv"  


def load(path):
    df = pd.read_csv(path)
    df = df.drop_duplicates(subset=["track_name", "artists"])
    df = df.dropna(subset=FEATURE_COLS + ["track_name", "artists", "popularity"])
    df = df.reset_index(drop=True)
    print(f"Loaded {len(df):,} tracks | {df['track_genre'].nunique()} genres")
    return df


# ─── 1. Distribution of Audio Features ────────────────────────────────────────
def plot_feature_distributions(df):
    fig, axes = plt.subplots(3, 3, figsize=(14, 10))
    fig.suptitle("Distribution of Audio Features", fontsize=16, fontweight="bold")
    for ax, feat in zip(axes.flatten(), FEATURE_COLS):
        ax.hist(df[feat], bins=50, color="#4c72b0", edgecolor="none", alpha=0.85)
        ax.set_title(feat.capitalize())
        ax.set_xlabel(feat)
        ax.set_ylabel("Count")
    plt.tight_layout()
    path = f"{PLOT_DIR}/01_feature_distributions.png"
    plt.savefig(path, dpi=150)
    print(f"Saved: {path}")
    plt.close()


# ─── 2. Correlation Heatmap ────────────────────────────────────────────────────
def plot_correlation(df):
    corr = df[FEATURE_COLS + ["popularity"]].corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
                linewidths=0.5, ax=ax)
    ax.set_title("Audio Feature Correlation Matrix", fontsize=14, fontweight="bold")
    plt.tight_layout()
    path = f"{PLOT_DIR}/02_correlation_heatmap.png"
    plt.savefig(path, dpi=150)
    print(f"Saved: {path}")
    plt.close()


# ─── 3. Top Genres by Track Count ─────────────────────────────────────────────
def plot_top_genres(df, top_n=20):
    top = df["track_genre"].value_counts().head(top_n)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=top.values, y=top.index, palette="Blues_d", ax=ax)
    ax.set_title(f"Top {top_n} Genres by Track Count", fontsize=14, fontweight="bold")
    ax.set_xlabel("Number of Tracks")
    plt.tight_layout()
    path = f"{PLOT_DIR}/03_top_genres.png"
    plt.savefig(path, dpi=150)
    print(f"Saved: {path}")
    plt.close()


# ─── 4. Popularity Distribution ───────────────────────────────────────────────
def plot_popularity(df):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].hist(df["popularity"], bins=50, color="#dd8452", edgecolor="none", alpha=0.9)
    axes[0].set_title("Popularity Distribution")
    axes[0].set_xlabel("Popularity Score (0–100)")

    # Average popularity by genre (top 15)
    avg_pop = df.groupby("track_genre")["popularity"].mean().sort_values(ascending=False).head(15)
    sns.barplot(x=avg_pop.values, y=avg_pop.index, palette="Oranges_d", ax=axes[1])
    axes[1].set_title("Avg Popularity by Genre (Top 15)")
    axes[1].set_xlabel("Avg Popularity")

    fig.suptitle("Song Popularity Analysis", fontsize=14, fontweight="bold")
    plt.tight_layout()
    path = f"{PLOT_DIR}/04_popularity.png"
    plt.savefig(path, dpi=150)
    print(f"Saved: {path}")
    plt.close()


# ─── 5. Energy vs. Valence Scatter ────────────────────────────────────────────
def plot_energy_valence(df, sample_n=3000):
    sample = df.sample(min(sample_n, len(df)), random_state=42)
    fig, ax = plt.subplots(figsize=(9, 6))
    scatter = ax.scatter(
        sample["energy"], sample["valence"],
        c=sample["popularity"], cmap="viridis",
        alpha=0.6, s=15, edgecolors="none"
    )
    plt.colorbar(scatter, ax=ax, label="Popularity")
    ax.set_xlabel("Energy")
    ax.set_ylabel("Valence (Positivity)")
    ax.set_title("Energy vs. Valence (colored by Popularity)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    path = f"{PLOT_DIR}/05_energy_valence.png"
    plt.savefig(path, dpi=150)
    print(f"Saved: {path}")
    plt.close()


# ─── 6. PCA — 2D Feature Space ────────────────────────────────────────────────
def plot_pca(df, sample_n=5000):
    sample = df.sample(min(sample_n, len(df)), random_state=42)
    scaler = MinMaxScaler()
    X = scaler.fit_transform(sample[FEATURE_COLS])

    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X)

    fig, ax = plt.subplots(figsize=(9, 7))
    sc = ax.scatter(
        coords[:, 0], coords[:, 1],
        c=sample["popularity"].values, cmap="plasma",
        alpha=0.5, s=10, edgecolors="none"
    )
    plt.colorbar(sc, ax=ax, label="Popularity")
    ax.set_title(
        f"PCA of Audio Features  (explained var: {pca.explained_variance_ratio_.sum():.1%})",
        fontsize=13, fontweight="bold"
    )
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%})")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%})")
    plt.tight_layout()
    path = f"{PLOT_DIR}/06_pca_feature_space.png"
    plt.savefig(path, dpi=150)
    print(f"Saved: {path}")
    plt.close()


# ─── 7. Average Feature Radar by Genre (top 6) ────────────────────────────────
def plot_genre_radar(df, top_n=6):
    RADAR_FEATS = ["danceability", "energy", "acousticness", "valence", "speechiness", "instrumentalness"]
    top_genres = df["track_genre"].value_counts().head(top_n).index.tolist()
    genre_avg = df[df["track_genre"].isin(top_genres)].groupby("track_genre")[RADAR_FEATS].mean()

    angles = np.linspace(0, 2 * np.pi, len(RADAR_FEATS), endpoint=False).tolist()
    angles += angles[:1]

    fig, axes = plt.subplots(2, 3, figsize=(13, 8), subplot_kw=dict(polar=True))
    fig.suptitle("Audio Feature Profile by Genre", fontsize=14, fontweight="bold")
    colors = sns.color_palette("tab10", top_n)

    for ax, (genre, color) in zip(axes.flatten(), zip(top_genres, colors)):
        values = genre_avg.loc[genre].tolist()
        values += values[:1]
        ax.plot(angles, values, color=color, linewidth=2)
        ax.fill(angles, values, color=color, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(RADAR_FEATS, size=8)
        ax.set_yticks([0.25, 0.5, 0.75])
        ax.set_title(genre, size=10, fontweight="bold", pad=10)

    plt.tight_layout()
    path = f"{PLOT_DIR}/07_genre_radar.png"
    plt.savefig(path, dpi=150)
    print(f"Saved: {path}")
    plt.close()


# ─── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    try:
        df = load(CSV_PATH)
    except FileNotFoundError:
        print(f"\n❌ Dataset not found at '{CSV_PATH}'.")
        print(r"c:\Users\anusha\OneDrive\Documents\Downloads\songrecommender\dataset.csv\n")
        sys.exit(1)

    print("\n📊 Running EDA — generating plots...\n")
    plot_feature_distributions(df)
    plot_correlation(df)
    plot_top_genres(df)
    plot_popularity(df)
    plot_energy_valence(df)
    plot_pca(df)
    plot_genre_radar(df)

    print(f"\n✅ All plots saved to '{PLOT_DIR}/'")
    print("\nDataset Summary:")
    print(df[FEATURE_COLS + ["popularity"]].describe().round(3).to_string())