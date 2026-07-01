import { useState, useEffect, useCallback } from 'react'
import { api } from '../api/client'
import type { GenreSummary } from '../types'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  ScatterChart, Scatter, ZAxis,
} from 'recharts'

export default function Games() {
  const [genres, setGenres] = useState<GenreSummary[]>([])
  const [cross, setCross] = useState<any[]>([])
  const [search, setSearch] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.genreSummary().then(r => setGenres(r.items)),
      api.genreCross().then(r => setCross(r.items)),
    ]).finally(() => setLoading(false))
  }, [])

  const handleSearch = useCallback(async (q: string) => {
    setSearch(q)
    if (q.length < 2) {
      setSearchResults([])
      return
    }
    const res = await api.searchGames(q, 10)
    setSearchResults(res.items)
  }, [])

  if (loading) return <div className="text-center py-20 text-gray-400">加载中...</div>

  return (
    <div className="space-y-6">
      {/* Search */}
      <div className="card">
        <h3 className="text-sm font-semibold mb-3">搜索游戏</h3>
        <input
          type="text"
          value={search}
          onChange={e => handleSearch(e.target.value)}
          placeholder="输入游戏名称..."
          className="w-full px-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-emerald-500"
        />
        {searchResults.length > 0 && (
          <div className="mt-3 space-y-1">
            {searchResults.map((g) => (
              <div key={g.appid} className="flex items-center justify-between py-2 px-3 hover:bg-gray-50 rounded-lg text-sm">
                <span className="font-medium">{g.name}</span>
                <span className="text-gray-400">${g.price?.toFixed(2)} / 评分: {g.metacritic_score ?? '-'}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Genre vs Price vs Rating */}
      <div className="card">
        <h3 className="text-sm font-semibold mb-4">类型分析：价格 vs 评分</h3>
        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart>
            <XAxis
              dataKey="avg_price"
              name="均价"
              unit="$"
              tick={{ fontSize: 11 }}
            />
            <YAxis
              dataKey="avg_metacritic"
              name="评分"
              domain={[0, 100]}
              tick={{ fontSize: 11 }}
            />
            <ZAxis dataKey="game_count" range={[60, 400]} />
            <Tooltip
              contentStyle={{ borderRadius: 8, border: '1px solid #e8ecf0' }}
              formatter={(value: any, name: string) => {
                if (name === 'avg_price') return [`$${value}`, '均价']
                if (name === 'avg_metacritic') return [value, '评分']
                return [value, name]
              }}
            />
            <Scatter data={genres} fill="#059669">
              {genres.map((_, i) => (
                <cell key={i} fill={['#059669', '#10b981', '#34d399', '#6ee7b7', '#f59e0b', '#f97316', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4'][i % 10]} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
        <div className="flex flex-wrap gap-2 mt-2">
          {genres.map((g) => (
            <span key={g.genre} className="text-xs text-gray-500 px-2 py-1 bg-gray-50 rounded">
              {g.genre}: {g.game_count} 款
            </span>
          ))}
        </div>
      </div>

      {/* Genre Cross: Price Tier Breakdown */}
      <div className="card">
        <h3 className="text-sm font-semibold mb-4">类型 x 价格段 交叉分析</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-400 text-xs uppercase tracking-wider border-b border-gray-100">
                <th className="pb-2 font-medium">类型</th>
                <th className="pb-2 font-medium">价格段</th>
                <th className="pb-2 font-medium">游戏数</th>
                <th className="pb-2 font-medium">平均评分</th>
              </tr>
            </thead>
            <tbody>
              {cross.slice(0, 30).map((item, i) => (
                <tr key={i} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="py-2 font-medium">{item.genre}</td>
                  <td className="py-2 text-gray-500">{item.price_tier}</td>
                  <td className="py-2">{item.game_count}</td>
                  <td className="py-2">
                    <span className={item.avg_metacritic >= 70 ? 'text-emerald-600' : 'text-amber-600'}>
                      {item.avg_metacritic}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
