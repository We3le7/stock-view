import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

export const quoteApi = {
  getRealtime: (symbols: string) => api.get(`/quote/realtime?symbols=${symbols}`),
  getList: (params: Record<string, any>) => api.get('/quote/list', { params }),
  getKline: (params: Record<string, any>) => api.get('/quote/kline', { params }),
  getTimeline: (symbol: string) => api.get(`/quote/timeline?symbol=${symbol}`),
  getOrderbook: (symbol: string) => api.get(`/quote/orderbook?symbol=${symbol}`),
}

export const stockApi = {
  search: (keyword: string, limit = 10) => api.get(`/stock/search?keyword=${keyword}&limit=${limit}`),
}

export const watchlistApi = {
  getList: () => api.get('/watchlist'),
  add: (symbol: string, market = 'sh') => api.post('/watchlist', { symbol, market }),
  remove: (symbol: string) => api.delete(`/watchlist/${symbol}`),
  sort: (items: { symbol: string; sort_order: number }[]) => api.put('/watchlist/sort', { items }),
}

export const aiApi = {
  analyze: (symbol: string, analysisType = 'comprehensive', periodDays = 30) =>
    api.post(`/ai/analyze?symbol=${symbol}&analysis_type=${analysisType}&period_days=${periodDays}`),
  getModelInfo: () => api.get('/ai/model-info'),
}

export default api