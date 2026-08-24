import { useState } from 'react'
import axios from 'axios'
import { motion, AnimatePresence } from 'framer-motion'
import SongCard from './SongCard.jsx'

const FEATURE_LABELS = {
  danceability: 'Danceability', energy: 'Energy', loudness: 'Loudness',
  speechiness: 'Speechiness', acousticness: 'Acousticness',
  instrumentalness: 'Instrumentalness', liveness: 'Liveness',
  valence: 'Valence (Positivity)', tempo: 'Tempo (BPM)',
}

export default function SongSearch({ api, nRecs, sameGenre }) {
  const [trackInput, setTrackInput]   = useState('')
  const [artistInput, setArtistInput] = useState('')
  const [loading, setLoading]         = useState(false)
  const [error, setError]             = useState(null)
  const [seed, setSeed]               = useState(null)
  const [recs, setRecs]               = useState([])
  const [showFeatures, setShowFeatures] = useState(false)

  async function handleSearch(e) {
    e.preventDefault()
    if (!trackInput.trim()) return
    setLoading(true)
    setError(null)
    setSeed(null)
    setRecs([])
    try {
      const { data } = await axios.post(`${api}/recommend/song`, {
        track_name: trackInput.trim(),
        artist:     artistInput.trim() || null,
        n:          nRecs,
        same_genre: sameGenre,
      })
      setSeed(data.seed)
      setRecs(data.recommendations)
    } catch (err) {
      if (err.response?.status === 404) {
        setError(`Song "${trackInput}" not found. Try a different spelling or add the artist name.`)
      } else {
        setError('Could not reach the backend. Make sure FastAPI is running on port 8000.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-base font-semibold text-gray-200 mb-4">Recommend based on a song you like</h2>
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3">
          <input
            className="input-field flex-[2]"
            placeholder="Song name (e.g. Blinding Lights)"
            value={trackInput}
            onChange={e => setTrackInput(e.target.value)}
          />
          <input
            className="input-field flex-1"
            placeholder="Artist (optional)"
            value={artistInput}
            onChange={e => setArtistInput(e.target.value)}
          />
          <button type="submit" className="btn-primary shrink-0" disabled={loading || !trackInput.trim()}>
            {loading ? (
              <>
                <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                </svg>
                Searching…
              </>
            ) : '🔍 Search'}
          </button>
        </form>
      </div>

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            className="px-4 py-3 rounded-xl bg-red-900/30 border border-red-700/50 text-red-300 text-sm"
            initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
          >
            ❌ {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Seed song info */}
      <AnimatePresence>
        {seed && (
          <motion.div
            className="card border-brand-700/50 bg-brand-900/20"
            initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }}
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs text-brand-400 font-semibold uppercase tracking-wider mb-1">Seed Song</p>
                <h3 className="text-lg font-bold text-white">{seed.track_name}</h3>
                <p className="text-sm text-gray-400">{seed.artists} · <span className="text-brand-300">{seed.track_genre}</span></p>
              </div>
              <button
                onClick={() => setShowFeatures(v => !v)}
                className="text-xs text-gray-500 hover:text-brand-400 transition-colors px-3 py-1.5 rounded-lg border border-surface-border hover:border-brand-700"
              >
                {showFeatures ? 'Hide' : 'Show'} features
              </button>
            </div>

            <AnimatePresence>
              {showFeatures && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="overflow-hidden"
                >
                  <div className="mt-4 grid grid-cols-3 gap-2 pt-4 border-t border-surface-border">
                    {Object.entries(seed.features).map(([key, val]) => (
                      <div key={key} className="bg-surface-elevated rounded-lg p-2.5 text-center">
                        <p className="text-xs text-gray-500 mb-1">{FEATURE_LABELS[key] || key}</p>
                        <p className="text-sm font-semibold text-white">{val}</p>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results grid */}
      {recs.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 mb-3 uppercase tracking-wider font-semibold">
            {recs.length} Recommendations
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {recs.map((song, i) => (
              <SongCard key={`${song.track_name}-${i}`} song={song} index={i} showSimilarity />
            ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && recs.length === 0 && !seed && (
        <div className="text-center py-20 text-gray-600">
          <div className="text-5xl mb-4">🎵</div>
          <p className="text-sm">Enter a song name above to get recommendations</p>
        </div>
      )}
    </div>
  )
}

