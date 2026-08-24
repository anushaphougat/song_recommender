import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import Sidebar from './components/Sidebar.jsx'
import SongSearch from './components/SongSearch.jsx'
import MoodSearch from './components/MoodSearch.jsx'
import Explore from './components/Explore.jsx'

const API = 'https://song-recommender-j7k1.onrender.com/'
const TABS = [
  { id: 'song',  label: '🎵 Find by Song' },
  { id: 'mood',  label: '🎭 Find by Mood' },
  { id: 'explore', label: '📊 Explore' },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('song')
  const [stats, setStats] = useState(null)
  const [nRecs, setNRecs] = useState(10)
  const [sameGenre, setSameGenre] = useState(false)
  const [apiError, setApiError] = useState(false)

  useEffect(() => {
    axios.get(`${API}/stats`)
      .then(r => setStats(r.data))
      .catch(() => setApiError(true))
  }, [])

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-surface-border bg-surface-card/60 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-3">
          <span className="text-3xl">🎵</span>
          <div>
            <h1 className="text-xl font-bold text-white leading-none">Song Recommender</h1>
            <p className="text-xs text-gray-500 mt-0.5">Hybrid Content-Based + Popularity Filtering · Spotify Tracks Dataset</p>
          </div>
          {apiError && (
            <div className="ml-auto px-3 py-1.5 rounded-lg bg-red-900/40 border border-red-700/50 text-red-400 text-xs">
              ⚠️ Cannot reach backend — start FastAPI on port 8000
            </div>
          )}
        </div>
      </header>

      <div className="flex flex-1 max-w-7xl mx-auto w-full px-6 py-6 gap-6">
        {/* Sidebar */}
        <Sidebar
          stats={stats}
          nRecs={nRecs}
          setNRecs={setNRecs}
          sameGenre={sameGenre}
          setSameGenre={setSameGenre}
        />

        {/* Main content */}
        <main className="flex-1 min-w-0">
          {/* Tabs */}
          <div className="flex gap-2 mb-6">
            {TABS.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`tab-btn ${activeTab === tab.id ? 'tab-btn-active' : 'tab-btn-inactive'}`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab panels */}
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.18 }}
            >
              {activeTab === 'song'    && <SongSearch api={API} nRecs={nRecs} sameGenre={sameGenre} />}
              {activeTab === 'mood'    && <MoodSearch api={API} nRecs={nRecs} />}
              {activeTab === 'explore' && <Explore    api={API} />}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  )
}

