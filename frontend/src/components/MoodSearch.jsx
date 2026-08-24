import { useState } from 'react'
import axios from 'axios'
import { motion, AnimatePresence } from 'framer-motion'
import SongCard from './SongCard.jsx'

const SLIDERS = [
  { key: 'danceability', label: '💃 Danceability', min: 0, max: 1,   step: 0.05, default: 0.7 },
  { key: 'energy',       label: '⚡ Energy',        min: 0, max: 1,   step: 0.05, default: 0.8 },
  { key: 'valence',      label: '😊 Positivity',    min: 0, max: 1,   step: 0.05, default: 0.6 },
  { key: 'tempo',        label: '🥁 Tempo (BPM)',   min: 60, max: 200, step: 5,  default: 120 },
]

function getMoodLabel(vals) {
  const { energy, danceability, valence } = vals
  if (energy > 0.7 && danceability > 0.7) return { label: '🔥 High-Energy Party', color: 'text-orange-400' }
  if (valence > 0.7 && energy < 0.5)      return { label: '☀️ Happy & Chill',      color: 'text-yellow-400' }
  if (valence < 0.3 && energy < 0.5)      return { label: '🌧️ Melancholic',        color: 'text-blue-400' }
  if (energy > 0.7 && valence < 0.4)      return { label: '💪 Intense Workout',    color: 'text-red-400' }
  return { label: '🎵 Mixed Mood', color: 'text-brand-400' }
}

export default function MoodSearch({ api, nRecs }) {
  const [values, setValues] = useState(
    Object.fromEntries(SLIDERS.map(s => [s.key, s.default]))
  )
  const [loading, setLoading] = useState(false)
  const [recs, setRecs]       = useState([])
  const [error, setError]     = useState(null)

  const mood = getMoodLabel(values)

  function handleSlider(key, val) {
    setValues(v => ({ ...v, [key]: Number(val) }))
  }

  async function handleSearch() {
    setLoading(true)
    setError(null)
    try {
      const { data } = await axios.post(`${api}/recommend/mood`, { ...values, n: nRecs })
      setRecs(data.recommendations)
    } catch {
      setError('Could not reach the backend. Make sure FastAPI is running on port 8000.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-base font-semibold text-gray-200 mb-5">Describe a mood and get song recommendations</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-5 mb-6">
          {SLIDERS.map(s => (
            <div key={s.key}>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm text-gray-300">{s.label}</label>
                <span className="text-sm font-semibold text-brand-400 w-12 text-right">
                  {s.key === 'tempo' ? `${values[s.key]} BPM` : values[s.key].toFixed(2)}
                </span>
              </div>
              <input
                type="range"
                min={s.min} max={s.max} step={s.step}
                value={values[s.key]}
                onChange={e => handleSlider(s.key, e.target.value)}
                className="range-slider"
              />
              <div className="flex justify-between text-xs text-gray-600 mt-1">
                <span>{s.min}</span><span>{s.max}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Mood label */}
        <div className="flex items-center justify-between p-3 rounded-xl bg-surface-elevated border border-surface-border mb-4">
          <p className="text-xs text-gray-500 uppercase tracking-wider">Detected mood</p>
          <p className={`text-sm font-semibold ${mood.color}`}>{mood.label}</p>
        </div>

        <button
          onClick={handleSearch}
          className="btn-primary w-full justify-center"
          disabled={loading}
        >
          {loading ? (
            <>
              <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
              </svg>
              Finding songs…
            </>
          ) : '🎭 Get Mood Recommendations'}
        </button>
      </div>

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            className="px-4 py-3 rounded-xl bg-red-900/30 border border-red-700/50 text-red-300 text-sm"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          >
            ❌ {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results */}
      {recs.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 mb-3 uppercase tracking-wider font-semibold">
            {recs.length} Songs for your mood
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {recs.map((song, i) => (
              <SongCard key={`${song.track_name}-${i}`} song={song} index={i} />
            ))}
          </div>
        </div>
      )}

      {!loading && recs.length === 0 && !error && (
        <div className="text-center py-16 text-gray-600">
          <div className="text-5xl mb-4">🎭</div>
          <p className="text-sm">Adjust the sliders and click the button to find songs for your mood</p>
        </div>
      )}
    </div>
  )
}

