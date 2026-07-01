import { useState, useEffect, useRef } from 'react'
import { api } from '../api/client'
import type { RealtimePlayer } from '../types'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function Realtime() {
  const [players, setPlayers] = useState<RealtimePlayer[]>([])
  const [wsStatus, setWsStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected')
  const wsRef = useRef<WebSocket | null>(null)

  // Fetch initial data
  useEffect(() => {
    api.realtimePlayers(20).then(r => {
      if (r.items?.length) setPlayers(r.items)
    })

    // WebSocket connection
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws/live`
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => setWsStatus('connected')
    ws.onclose = () => {
      setWsStatus('disconnected')
      wsRef.current = null
    }
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'realtime_players' && data.data) {
          setPlayers(data.data)
        }
      } catch {}
    }

    return () => ws.close()
  }, [])

  return (
    <div className="space-y-6">
      {/* Status */}
      <div className="flex items-center gap-3">
        <h3 className="text-sm font-semibold">实时在线玩家</h3>
        <div className="flex items-center gap-1.5">
          <span className={`w-2 h-2 rounded-full ${
            wsStatus === 'connected' ? 'bg-emerald-500' :
            wsStatus === 'connecting' ? 'bg-amber-500' : 'bg-gray-400'
          }`} />
          <span className="text-xs text-gray-400">
            {wsStatus === 'connected' ? '实时连接中' :
             wsStatus === 'connecting' ? '连接中...' : '未连接'}
          </span>
        </div>
      </div>

      {/* Player Count Chart */}
      <div className="card">
        <h4 className="text-xs text-gray-400 uppercase tracking-wider mb-3">当前在线玩家</h4>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={players} layout="vertical">
            <XAxis type="number" tick={{ fontSize: 10 }} />
            <YAxis type="category" dataKey="appid" tick={{ fontSize: 10 }} width={60} />
            <Tooltip
              contentStyle={{ borderRadius: 8, border: '1px solid #e8ecf0' }}
              formatter={(value: number) => [value.toLocaleString(), '在线玩家']}
            />
            <Bar dataKey="player_count" fill="#059669" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Player Table */}
      <div className="card">
        <h4 className="text-xs text-gray-400 uppercase tracking-wider mb-3">详情</h4>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-400 text-xs uppercase tracking-wider border-b border-gray-100">
                <th className="pb-2 font-medium">AppID</th>
                <th className="pb-2 font-medium">在线玩家</th>
                <th className="pb-2 font-medium">记录时间</th>
              </tr>
            </thead>
            <tbody>
              {players.map((p) => (
                <tr key={p.appid} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="py-2 font-medium">{p.appid}</td>
                  <td className="py-2">
                    <span className="font-semibold text-emerald-700">{p.player_count.toLocaleString()}</span>
                  </td>
                  <td className="py-2 text-gray-400 text-xs">{p.recorded_at}</td>
                </tr>
              ))}
              {players.length === 0 && (
                <tr>
                  <td colSpan={3} className="py-8 text-center text-gray-400 text-sm">
                    暂无实时数据。配置 STEAM_API_KEY 后自动采集。
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
