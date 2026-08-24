import { useState, useEffect } from 'react'
import axios from 'axios'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell
} from 'recharts'

const PURPLE_SHADES = [
  '#a855f7','#9333ea','#7c3aed','#6d28d9','#5b21b6',
  '#4c1d95','#a21caf','#86198f','#701a75','#c026d3',
]

function CustomTooltip({ active, payload }) {
  if (active && payload?.length) {
    return (
      <div className="bg-surface-card border border-surface-border rounded-lg px-3 py-2 text-xs">
        <p className="text-white font-semibold">{payload[0].payload.genre}</p>
        <p className="text-gray-400">{payload[0].value} songs</p>
      </div>
    )
  }
  return null
}

export default function Explore({ api }) {
  const [genres, setGenres]       = useState([])
  const [topSongs, setTopSongs]   = useState([])
  const [genreList, setGenreList] = useState([])
  const [selectedGenre, setSelectedGenre] = useState('')
  const [genreSongs, setGenreSongs] = useState([])
  const [loading, setLoading]     = useState(true)
  const [loadingGenre, setLoadingGenre] = useState(false)

  useEffect(() => {
    Promise.all([
      axios.get(`${api}/genres`),
      axios.get(`${api}/top-songs`),
    ]).then(([g, t]) => {
      setGenres(g.data.slice(0, 10))
      setTopSongs(t.data)
      // build sorted genre list for dropdown
      const sorted = g.data.map(r => r.genre).sort()
      setGenreList(sorted)
      if (sorted.length) setSelectedGenre(sorted[0])
    }).finally(() => setLoading(false))
  }, [api])

  useEffect(() => {
    if (!selectedGenre) return
    setLoadingGenre(true)
    axios.get(`${api}/genre-songs`, { params: { genre: selectedGenre, limit: 20 } })
      .then(r => setGenreSongs(r.data))
      .finally(() => setLoadingGenre(false))
  }, [selectedGenre, api])

  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-pulse">
        {[1,2].map(i => <div key={i} className="card h-72 bg-surface-elevated" />)}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Top row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Genre bar chart */}
        <div className="card">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">🎸 Top 10 Genres</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={genres} layout="vertical" margin={{ left: 0, right: 16, top: 0, bottom: 0 }}>
              <XAxis type="number" tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis
                type="category"
                dataKey="genre"
                width={90}
                tick={{ fill: '#9ca3af', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(139,92,246,0.08)' }} />
              <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                {genres.map((_, i) => (
                  <Cell key={i} fill={PURPLE_SHADES[i % PURPLE_SHADES.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Top 10 songs table */}
        <div className="card">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">🏆 Top 10 Most Popular Songs</h3>
          <div className="space-y-2">
            {topSongs.map((song, i) => (
              <div key={i} className="flex items-center gap-3 py-1.5">
                <span className="text-sm font-bold text-gray-700 w-5 shrink-0">{i + 1}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white font-medium truncate leading-snug">{song.track_name}</p>
                  <p className="text-xs text-gray-500 truncate">{song.artists}</p>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-sm font-semibold text-brand-400">{song.popularity}</p>
                  <p className="text-xs text-gray-600">pop</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Genre browser */}
      <div className="card">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
          <h3 className="text-sm font-semibold text-gray-300">🎵 Browse by Genre</h3>
          <select
            className="input-field w-auto min-w-[200px]"
            value={selectedGenre}
            onChange={e => setSelectedGenre(e.target.value)}
          >
            {genreList.map(g => <option key={g} value={g}>{g}</option>)}
          </select>
        </div>

        {loadingGenre ? (
          <div className="space-y-2 animate-pulse">
            {[...Array(5)].map((_, i) => <div key={i} className="h-10 bg-surface-elevated rounded-lg" />)}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-500 uppercase tracking-wider border-b border-surface-border">
                  <th className="text-left py-2 pr-4">#</th>
                  <th className="text-left py-2 pr-4">Song</th>
                  <th className="text-left py-2 pr-4">Artist</th>
                  <th className="text-right py-2 pr-4">Pop.</th>
                  <th className="text-right py-2 pr-4">Dance</th>
                  <th className="text-right py-2 pr-4">Energy</th>
                  <th className="text-right py-2 pr-4">Valence</th>
                  <th className="text-right py-2">Speech.</th>
                </tr>
              </thead>
              <tbody>
                {genreSongs.map((song, i) => (
                  <tr key={i} className="border-b border-surface-border/50 hover:bg-surface-elevated/50 transition-colors">
                    <td className="py-2.5 pr-4 text-gray-600">{i + 1}</td>
                    <td className="py-2.5 pr-4 text-white font-medium max-w-[200px] truncate">{song.track_name}</td>
                    <td className="py-2.5 pr-4 text-gray-400 max-w-[140px] truncate">{song.artists}</td>
                    <td className="py-2.5 pr-4 text-right text-brand-400 font-semibold">{song.popularity}</td>
                    <td className="py-2.5 pr-4 text-right text-gray-400">{song.danceability?.toFixed(2)}</td>
                    <td className="py-2.5 pr-4 text-right text-gray-400">{song.energy?.toFixed(2)}</td>
                    <td className="py-2.5 pr-4 text-right text-gray-400">{song.valence?.toFixed(2)}</td>
                    <td className="py-2.5 text-right text-gray-400">{song.speechiness?.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

