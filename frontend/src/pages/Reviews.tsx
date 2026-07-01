import { useState, useEffect } from 'react'
import { api } from '../api/client'
import type { Review } from '../types'

export default function Reviews() {
  const [reviews, setReviews] = useState<Review[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)

  useEffect(() => {
    setLoading(true)
    api.listReviews({ page }).then((r: any) => {
      setReviews(r.items)
      setTotal(r.total)
    }).finally(() => setLoading(false))
  }, [page])

  if (loading) return <div className="text-center py-20 text-gray-400">加载中...</div>

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">最新评论</h3>
        <span className="text-xs text-gray-400">共 {total.toLocaleString()} 条</span>
      </div>

      <div className="space-y-3">
        {reviews.map((r) => (
          <div key={r.id} className="card">
            <div className="flex items-center gap-2 mb-2">
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                r.voted_up ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'
              }`}>
                {r.voted_up ? '推荐' : '不推荐'}
              </span>
              <span className="text-xs text-gray-400">{r.language}</span>
              {r.timestamp_created && (
                <span className="text-xs text-gray-400">{r.timestamp_created.slice(0, 10)}</span>
              )}
            </div>
            <p className="text-sm text-gray-600 line-clamp-3">
              {r.review_text || '(无评论内容)'}
            </p>
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-center gap-2 pt-2">
        <button
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page <= 1}
          className="px-3 py-1 text-sm border border-gray-200 rounded-lg disabled:opacity-40 hover:bg-gray-50"
        >
          上一页
        </button>
        <span className="text-sm text-gray-500">第 {page} 页</span>
        <button
          onClick={() => setPage(p => p + 1)}
          disabled={page * 20 >= total}
          className="px-3 py-1 text-sm border border-gray-200 rounded-lg disabled:opacity-40 hover:bg-gray-50"
        >
          下一页
        </button>
      </div>
    </div>
  )
}
