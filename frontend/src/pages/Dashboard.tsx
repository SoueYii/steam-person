import { useState, useEffect, useCallback } from 'react'
import { api } from '../api/client'
import type { GenreSummary, PriceTier, TopGame } from '../types'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts'

const COLORS = ['#059669', '#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#d1fae5',
  '#f59e0b', '#f97316', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4']

export default function Dashboard() {
  const [genres, setGenres] = useState<GenreSummary[]>([])
  const [prices, setPrices] = useState<PriceTier[]>([])
  const [top, setTop] = useState<TopGame[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.genreSummary().then(r => setGenres(r.items)),
      api.priceDistribution().then(r => setPrices(r.items)),
      api.topGames(10).then(r => setTop(r.items)),
    ]).finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400 text-sm">加载中...</div>
      </div>
    )
  }

  const totalGames = genres.reduce((s, g) => s + g.game_count, 0)
  const avgRating = genres.reduce((s, g) => s + g.avg_metacritic * g.game_count, 0) / totalGames || 0

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="card">
          <div className="stat-label">游戏总数</div>
          <div className="stat-value">{totalGames.toLocaleString()}</div>
        </div>
        <div className="card">
          <div className="stat-label">平均评分</div>
          <div className="stat-value">{avgRating.toFixed(1)}</div>
        </div>
        <div className="card">
          <div className="stat-label">游戏类型</div>
          <div className="stat-value">{genres.length}</div>
        </div>
        <div className="card">
          <div className="stat-label">总评论数</div>
          <div className="stat-value">{top.reduce((s, g) => s + g.total_reviews, 0).toLocaleString()}</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Genre Pie */}
        <div className="card">
          <h3 className="text-sm font-semibold mb-4">游戏类型分布</h3>
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Pie
                data={genres.slice(0, 10)}
                dataKey="game_count"
                nameKey="genre"
                cx="50%"
                cy="50%"
                outerRadius={110}
                innerRadius={50}
              >
                {genres.slice(0, 10).map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: number) => value.toLocaleString()}
                contentStyle={{ borderRadius: 8, border: '1px solid #e8ecf0' }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap gap-2 mt-2">
            {genres.slice(0, 10).map((g, i) => (
              <span key={g.genre} className="text-xs text-gray-500 flex items-center gap-1">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                {g.genre}
              </span>
            ))}
          </div>
        </div>

        {/* Price Distribution */}
        <div className="card">
          <h3 className="text-sm font-semibold mb-4">价格段分布</h3>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={prices}>
              <XAxis dataKey="tier" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ borderRadius: 8, border: '1px solid #e8ecf0' }}
              />
              <Bar dataKey="game_count" fill="#059669" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Games */}
      <div className="card">
        <h3 className="text-sm font-semibold mb-4">综合排名 Top 10</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-400 text-xs uppercase tracking-wider border-b border-gray-100">
                <th className="pb-2 font-medium">#</th>
                <th className="pb-2 font-medium">游戏名</th>
                <th className="pb-2 font-medium">价格</th>
                <th className="pb-2 font-medium">评分</th>
                <th className="pb-2 font-medium">评论数</th>
                <th className="pb-2 font-medium">好评率</th>
              </tr>
            </thead>
            <tbody>
              {top.map((g, i) => (
                <tr key={g.appid} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="py-2.5 text-gray-400">{i + 1}</td>
                  <td className="py-2.5 font-medium">{g.name}</td>
                  <td className="py-2.5">${g.price?.toFixed(2)}</td>
                  <td className="py-2.5">{g.metacritic_score ?? '-'}</td>
                  <td className="py-2.5">{g.total_reviews.toLocaleString()}</td>
                  <td className="py-2.5">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      (g.positive_rate ?? 0) >= 80 ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'
                    }`}>
                      {g.positive_rate?.toFixed(1)}%
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
