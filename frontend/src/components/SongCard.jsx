import { motion } from 'framer-motion'

const GENRE_COLORS = {
  pop: 'bg-pink-900/40 text-pink-300 border-pink-800/50',
  rock: 'bg-red-900/40 text-red-300 border-red-800/50',
  'hip-hop': 'bg-yellow-900/40 text-yellow-300 border-yellow-800/50',
  jazz: 'bg-blue-900/40 text-blue-300 border-blue-800/50',
  classical: 'bg-indigo-900/40 text-indigo-300 border-indigo-800/50',
  electronic: 'bg-cyan-900/40 text-cyan-300 border-cyan-800/50',
  default: 'bg-brand-900/40 text-brand-300 border-brand-800/50',
}

function genreClass(genre) {
  if (!genre) return GENRE_COLORS.default
  const key = genre.toLowerCase()
  return GENRE_COLORS[key] || GENRE_COLORS.default
}

function PopBar({ value, max = 100 }) {
  const pct = Math.round((value / max) * 100)
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-surface-elevated rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-brand-600 to-purple-500 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        />
      </div>
      <span className="text-xs text-gray-500 w-6 text-right">{value}</span>
    </div>
  )
}

export default function SongCard({ song, index, showSimilarity = false }) {
  return (
    <motion.div
      className="card group cursor-default"
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04, duration: 0.25 }}
    >
      {/* Rank + title */}
      <div className="flex items-start gap-3">
        <span className="text-2xl font-bold text-gray-700 w-8 shrink-0 text-right leading-none mt-0.5">
          {index + 1}
        </span>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-white truncate text-sm leading-snug">{song.track_name}</p>
          <p className="text-xs text-gray-400 truncate mt-0.5">{song.artists}</p>
        </div>
      </div>

      {/* Genre badge + popularity */}
      <div className="mt-3 space-y-2">
        <div className="flex items-center justify-between">
          <span className={`badge border ${genreClass(song.track_genre)}`}>
            {song.track_genre}
          </span>
          {showSimilarity && song.similarity !== undefined && (
            <span className="text-xs text-brand-400 font-medium">
              {Math.round(song.similarity * 100)}% match
            </span>
          )}
          {!showSimilarity && song.score !== undefined && (
            <span className="text-xs text-purple-400 font-medium">
              ♪ {song.score.toFixed(3)}
            </span>
          )}
        </div>

        {/* Popularity bar */}
        <div>
          <p className="text-xs text-gray-600 mb-1">Popularity</p>
          <PopBar value={song.popularity} />
        </div>
      </div>
    </motion.div>
  )
}

