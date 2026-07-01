const BASE = '/api'

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(`${BASE}${url}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.url}`)
  return res.json()
}

export const api = {
  // Games
  listGames: (page = 1, sort = 'name', order = 'asc') =>
    fetchJSON(`/games?page=${page}&page_size=20&sort=${sort}&order=${order}`),

  getGame: (appid: number) =>
    fetchJSON(`/games/${appid}`),

  searchGames: (q: string, limit = 20) =>
    fetchJSON(`/games/search?q=${encodeURIComponent(q)}&limit=${limit}`),

  // Analytics
  genreSummary: () =>
    fetchJSON('/analytics/genre-summary'),

  priceDistribution: () =>
    fetchJSON('/analytics/price-distribution'),

  dailyTrends: (days = 90) =>
    fetchJSON(`/analytics/daily-trends?days=${days}`),

  topGames: (limit = 20) =>
    fetchJSON(`/analytics/top-games?limit=${limit}`),

  genreCross: () =>
    fetchJSON('/analytics/genre-cross'),

  realtimePlayers: (limit = 20) =>
    fetchJSON(`/analytics/realtime-players?limit=${limit}`),

  // Reviews
  listReviews: (params: { appid?: number; page?: number }) => {
    const q = new URLSearchParams()
    if (params.appid) q.set('appid', String(params.appid))
    if (params.page) q.set('page', String(params.page))
    return fetchJSON(`/reviews?${q}`)
  },
}
