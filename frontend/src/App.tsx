import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import Games from './pages/Games'
import Trends from './pages/Trends'
import Reviews from './pages/Reviews'
import Realtime from './pages/Realtime'

type Page = 'dashboard' | 'games' | 'trends' | 'reviews' | 'realtime'

const NAV_ITEMS: { key: Page; label: string }[] = [
  { key: 'dashboard', label: '概览' },
  { key: 'games', label: '游戏' },
  { key: 'trends', label: '趋势' },
  { key: 'reviews', label: '评论' },
  { key: 'realtime', label: '实时' },
]

export default function App() {
  const [page, setPage] = useState<Page>('dashboard')

  return (
    <div className="min-h-screen bg-surface">
      {/* Header */}
      <header className="bg-white border-b border-border sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xl font-bold tracking-tight">Steam Analytics</span>
          </div>
          <nav className="flex items-center gap-1">
            {NAV_ITEMS.map((item) => (
              <button
                key={item.key}
                onClick={() => setPage(item.key)}
                className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  page === item.key
                    ? 'bg-emerald-50 text-emerald-700'
                    : 'text-gray-500 hover:text-gray-800 hover:bg-gray-50'
                }`}
              >
                {item.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-6 py-6">
        {page === 'dashboard' && <Dashboard />}
        {page === 'games' && <Games />}
        {page === 'trends' && <Trends />}
        {page === 'reviews' && <Reviews />}
        {page === 'realtime' && <Realtime />}
      </main>
    </div>
  )
}
