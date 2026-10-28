import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
export const API_ROOT = API_URL.replace(/\/api$/, '')
export const WS_ROOT = API_ROOT.replace(/^http/, 'ws')

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add JWT token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth endpoints
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
  updateMe: (data) => api.put('/auth/me', data),
  changePassword: (data) => api.post('/auth/change-password', data),
}

// Trade endpoints
export const tradeAPI = {
  createTrade: (data) => api.post('/trades/', data),
  getUserTrades: (limit = 50) => api.get(`/trades/?limit=${limit}`),
  getOpenTrades: () => api.get('/trades/open'),
  getOpenPositions: () => api.get('/trades/open/positions'),
  getTrade: (tradeId) => api.get(`/trades/${tradeId}`),
  closeTrade: (tradeId, exitPrice) =>
    api.post(`/trades/${tradeId}/close${exitPrice ? `?exit_price=${exitPrice}` : ''}`),
}

export const dashboardAPI = {
  getSummary: () => api.get('/dashboard/user/summary'),
  getRecentTrades: (limit = 20) => api.get(`/dashboard/user/trades?limit=${limit}`),
  getOpenTrades: () => api.get('/dashboard/user/open-trades'),
}

export const marketAPI = {
  getPrices: () => api.get('/market/prices'),
  getPairPrice: (pair) => api.get(`/market/prices/${encodeURIComponent(pair)}`),
  getCandles: (pair, timeframe = '15m', limit = 120) =>
    api.get(`/market/candles/${encodeURIComponent(pair)}?timeframe=${timeframe}&limit=${limit}`),
  getPairs: () => api.get('/market/pairs'),
  getPriceStreamUrl: (pair) => `${WS_ROOT}/api/market/ws/prices/${pair}`,
}

export const paymentAPI = {
  createDeposit: (data) => api.post('/payments/deposits', data),
  createWithdrawal: (data) => api.post('/payments/withdrawals', data),
  confirmDeposit: (depositId, data) => api.post(`/payments/deposits/${depositId}/confirm`, data),
  getDeposits: (limit = 20) => api.get(`/payments/deposits?limit=${limit}`),
}

// Health endpoint
export const healthAPI = {
  check: () => api.get('/health', { baseURL: API_ROOT || 'http://localhost:8000' }),
}

export default api
