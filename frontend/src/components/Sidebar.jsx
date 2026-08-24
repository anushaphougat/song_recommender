export default function Sidebar({ stats, nRecs, setNRecs, sameGenre, setSameGenre }) {
  return (
    <aside className="w-56 shrink-0 space-y-4">
      {/* Settings card */}
      <div className="card space-y-5">
        <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">⚙️ Settings</h2>

        {/* N recs slider */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="text-xs text-gray-400">Recommendations</label>
            <span className="text-sm font-semibold text-brand-400">{nRecs}</span>
          </div>
          <input
            type="range"
            min={5} max={25} step={1}
            value={nRecs}
            onChange={e => setNRecs(Number(e.target.value))}
            className="range-slider"
          />
          <div className="flex justify-between text-xs text-gray-600 mt-1">
            <span>5</span><span>25</span>
          </div>
        </div>

        {/* Same genre toggle */}
        <label className="flex items-center gap-3 cursor-pointer group">
          <div className="relative">
            <input
              type="checkbox"
              className="sr-only peer"
              checked={sameGenre}
              onChange={e => setSameGenre(e.target.checked)}
            />
            <div className="w-9 h-5 rounded-full bg-surface-border peer-checked:bg-brand-600 transition-colors duration-200" />
            <div className="absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform duration-200 peer-checked:translate-x-4" />
          </div>
          <span className="text-xs text-gray-400 group-hover:text-gray-200 transition-colors">Same genre only</span>
        </label>
      </div>

      {/* Stats card */}
      {stats ? (
        <div className="card space-y-3">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">📊 Dataset</h2>
          <div className="stat-card">
            <p className="text-2xl font-bold text-white">{stats.total_songs.toLocaleString()}</p>
            <p className="text-xs text-gray-500 mt-0.5">Total Songs</p>
          </div>
          <div className="stat-card">
            <p className="text-2xl font-bold text-brand-400">{stats.total_genres}</p>
            <p className="text-xs text-gray-500 mt-0.5">Genres</p>
          </div>
          <div className="stat-card">
            <p className="text-2xl font-bold text-purple-400">{stats.total_artists.toLocaleString()}</p>
            <p className="text-xs text-gray-500 mt-0.5">Artists</p>
          </div>
        </div>
      ) : (
        <div className="card animate-pulse space-y-3">
          {[1,2,3].map(i => (
            <div key={i} className="h-16 bg-surface-elevated rounded-xl" />
          ))}
        </div>
      )}

      {/* Footer note */}
      <p className="text-xs text-gray-600 text-center px-2">
        Backend running on<br />
        <span className="text-gray-500">localhost:8000</span>
      </p>
    </aside>
  )
}

