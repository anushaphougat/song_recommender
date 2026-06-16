# 🎵 Song Recommendation System

A hybrid content-based + popularity-weighted music recommender built on the
**Spotify Tracks Dataset** (~114k songs, 114 genres, 9 audio features).

---

## Project Structure

```
song_recommender/
├── recommender.py      ← Core ML model (content similarity + hybrid scoring)
├── eda.py              ← Exploratory data analysis (7 plots saved to ./plots/)
├── app.py              ← Streamlit web app
└── plots/              ← Auto-created by eda.py
```

---

## 1. Dataset Setup

Download the **Spotify Tracks Dataset** from Kaggle:

🔗 https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset

Rename the file to `dataset.csv` and place it in the `song_recommender/` folder.

**Key columns used:**
| Column | Description |
|---|---|
| `track_name` | Song title |
| `artists` | Artist name(s) |
| `track_genre` | Genre label |
| `popularity` | Spotify popularity (0–100) |
| `danceability` | How suitable for dancing (0–1) |
| `energy` | Perceptual measure of intensity (0–1) |
| `valence` | Musical positivity/happiness (0–1) |
| `tempo` | Beats per minute |
| + 5 more audio features | loudness, speechiness, acousticness, instrumentalness, liveness |

---

## 2. Usage

### Option A — Run the core recommender (CLI)

```bash
python recommender.py
```

This runs two demos:
- Recommendations for **"Blinding Lights"** by The Weeknd
- Mood-based recommendations (high energy + danceability)

### Option B — Run EDA to explore the dataset

```bash
python eda.py
```

Generates 7 analysis plots in `./plots/`:
1. Audio feature distributions
2. Correlation heatmap
3. Top genres by track count
4. Popularity distribution & by genre
5. Energy vs. valence scatter
6. PCA of feature space
7. Radar chart of genre audio profiles

### Option C — Launch the Streamlit web app

```bash
streamlit run app.py
```

Opens a browser UI with three tabs:
- **Find by Song** — enter a song name and get similar songs
- **Find by Mood** — tune sliders for energy/danceability/valence/tempo
- **Explore Dataset** — browse genres, top songs, stats

---

## 3. How the Model Works

### Step 1 — Feature Extraction
9 audio features are selected: `danceability`, `energy`, `loudness`,
`speechiness`, `acousticness`, `instrumentalness`, `liveness`, `valence`, `tempo`.

### Step 2 — Normalization
All features are scaled to [0, 1] using `MinMaxScaler` so no single feature
dominates the similarity calculation.

### Step 3 — Cosine Similarity
Pairwise cosine similarity is computed across all songs, producing an
N × N similarity matrix.

### Step 4 — Hybrid Scoring
```
hybrid_score = (1 - w) × content_similarity + w × popularity_norm
```
where `w = 0.2` (20% popularity boost). This ensures recommendations are
both sonically similar *and* reasonably well-known.

### Step 5 — Ranking
Top-N songs with highest hybrid scores are returned (excluding the seed song).

---

## 4. Extending the Project

| Idea | How |
|---|---|
| Add user ratings | Implement collaborative filtering with `surprise` library |
| Use embeddings | Replace cosine similarity with neural embeddings (e.g., Sentence-BERT on lyrics) |
| Cluster genres | Apply K-Means / UMAP to group songs visually |
| Add lyrics | Scrape lyrics → TF-IDF or BERT → blend with audio features |
| Deploy online | Push Streamlit app to [Streamlit Cloud](https://streamlit.io/cloud) for free |

---

## 5. Example Output

```
🎵 Seed song : Blinding Lights — The Weeknd (synth-pop)
   Features  : danceability=0.51, energy=0.73, valence=0.33, tempo=171 BPM

Song                   Artist           Genre       Popularity  Similarity  Score
Save Your Tears        The Weeknd       pop         87          0.9821      0.8015
Ghost                  Justin Bieber    pop         82          0.9743      0.7961
Levitating             Dua Lipa         disco       90          0.9689      0.7934
...
```
