import { useState, useEffect } from 'react'
import { api } from '../api/client'
import type { TrendPoint, GenreSummary } from '../types'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar,
} from 'recharts'

export default function Trends() {
  const [trends, setTrends] = useState<TrendPoint[]>([])
  const [genres, setGenres] = useState<GenreSummary[]>([])
  const [days, setDays] = useState(90)

  useEffect(() => {
    api.dailyTrends(days).then(r => setTrends(r.items))
    api.genreSummary().then(r => setGenres(r.items))
  }, [days])

  const sortedGenres = [...genres].sort((a, b) => b.positive_rate - a.positive_rate)

  return (
    <div className="space-y-6">
      {/* Daily Trends */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold">每日评论趋势</h3>
          <select
            value={days}
            onChange={e => setDays(Number(e.target.value))}
            className="text-xs border border-gray-200 rounded-lg px-2 py-1"
          >
            <option value={30}>近 30 天</option>
            <option value={90}>近 90 天</option>
            <option value={180}>近 180 天</option>
            <option value={365}>近 365 天</option>
          </select>
        </div>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={trends}>
            <XAxis
              dataKey="date"
              tick={{ fontSize: 10 }}
              tickFormatter={(v: string) => v.slice(5)}
            />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip
              contentStyle={{ borderRadius: 8, border: '1px solid #e8ecf0' }}
            />
            <Line
              type="monotone"
              dataKey="count"
              stroke="#059669"
              strokeWidth={2}
              dot={false}
              name="评论数"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Genre Positive Rate */}
      <div className="card">
        <h3 className="text-sm font-semibold mb-4">各类型好评率排名</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={sortedGenres} layout="vertical">
            <XAxis type="number" unit="%" tick={{ fontSize: 11 }} domain={[0, 100]} />
            <YAxis type="category" dataKey="genre" tick={{ fontSize: 11 }} width={80} />
            <Tooltip
              contentStyle={{ borderRadius: 8, border: '1px solid #e8ecf0' }}
              formatter={(value: number) => [`${value.toFixed(1)}%`, '好评率']}
            />
            <Bar dataKey="positive_rate" fill="#059669" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Genre Detail Table */}
      <div className="card">
        <h3 className="text-sm font-semibold mb-4">类型详细数据</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-400 text-xs uppercase tracking-wider border-b border-gray-100">
                <th className="pb-2 font-medium">类型</th>
                <th className="pb-2 font-medium">游戏数</th>
                <th className="pb-2 font-medium">均价</th>
                <th className="pb-2 font-medium">评分</th>
                <th className="pb-2 font-medium">评论数</th>
                <th className="pb-2 font-medium">好评率</th>
              </tr>
            </thead>
            <tbody>
              {sortedGenres.map((g) => (
                <tr key={g.genre} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="py-2.5 font-medium">{g.genre}</td>
                  <td className="py-2.5">{g.game_count.toLocaleString()}</td>
                  <td className="py-2.5">${g.avg_price.toFixed(2)}</td>
                  <td className="py-2.5">{g.avg_metacritic.toFixed(1)}</td>
                  <td className="py-2.5">{g.total_reviews.toLocaleString()}</td>
                  <td className="py-2.5">
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-emerald-500 rounded-full"
                          style={{ width: `${g.positive_rate}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500">{g.positive_rate.toFixed(1)}%</span>
                    </div>
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
