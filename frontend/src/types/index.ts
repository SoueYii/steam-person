export interface Game {
  appid: number
  name: string
  type?: string
  is_free?: boolean
  price?: number
  metacritic_score?: number
  recommendations_total?: number
  developers?: string
  publishers?: string
}

export interface GameDetail extends Game {
  genres: string[]
  review_count: number
  positive_rate?: number
}

export interface GenreSummary {
  genre: string
  game_count: number
  avg_price: number
  avg_metacritic: number
  total_reviews: number
  positive_rate: number
}

export interface PriceTier {
  tier: string
  game_count: number
  avg_rating: number
  total_reviews: number
}

export interface TrendPoint {
  date: string
  count: number
  positive_rate: number
}

export interface TopGame {
  appid: number
  name: string
  price: number
  metacritic_score: number
  total_reviews: number
  positive_rate: number
}

export interface RealtimePlayer {
  appid: number
  player_count: number
  recorded_at: string
}

export interface Review {
  id: number
  appid: number
  voted_up: boolean | null
  review_text: string | null
  language: string | null
  timestamp_created: string | null
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
