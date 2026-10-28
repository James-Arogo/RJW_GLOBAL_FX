import React, { useEffect, useMemo, useState } from 'react'
import {
  Activity,
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  CandlestickChart,
  DollarSign,
  Info,
  Layers3,
  Radio,
  Send,
  ShieldCheck,
  TimerReset,
  TrendingDown,
  TrendingUp,
} from 'lucide-react'
import { authAPI, marketAPI, tradeAPI } from '../utils/api'
import { useAuth } from '../context/AuthContext'
import { formatCurrency, formatNumber } from '../utils/formatting'

const FALLBACK_PAIR = 'EUR/USD'
const KES_PRESETS = [50, 100, 250, 500, 1000, 2500]

const buildOrderBook = (priceData) => {
  if (!priceData?.price) return { bids: [], asks: [] }

  const basePrice = Number(priceData.price)
  const precision = basePrice > 1000 ? 1 : 4
  const step = Math.max(basePrice * 0.00012, basePrice > 1000 ? 0.5 : 0.0002)

  const asks = Array.from({ length: 6 }, (_, index) => {
    const price = basePrice + step * (index + 1)
    const size = Number((0.25 + index * 0.09).toFixed(3))
    return {
      price: Number(price.toFixed(precision)),
      size,
      total: Number((price * size).toFixed(2)),
    }
  }).reverse()

  const bids = Array.from({ length: 6 }, (_, index) => {
    const price = basePrice - step * (index + 1)
    const size = Number((0.28 + index * 0.08).toFixed(3))
    return {
      price: Number(price.toFixed(precision)),
      size,
      total: Number((price * size).toFixed(2)),
    }
  })

  return { asks, bids }
}

const buildMiniTrend = (basePrice, changePercent) => {
  const seed = Number(basePrice || 1)
  return Array.from({ length: 24 }, (_, index) => {
    const wave = Math.sin((index + 1) / 2.4) * (seed > 1000 ? 45 : 0.0018)
    const drift = ((changePercent || 0) / 100) * seed * (index / 24)
    return Number(basePrice + wave + drift)
  })
}

export const Trade = () => {
  const { user, updateUser } = useAuth()
  const [tradeMode, setTradeMode] = useState('simple')
  const [formData, setFormData] = useState({
    pair: FALLBACK_PAIR,
    tradeType: 'BUY',
    amount: 500,
    leverage: 3,
    entryPrice: 1.085,
    stopLoss: 50,
    takeProfit: 100,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [priceMap, setPriceMap] = useState({})
  const [streamState, setStreamState] = useState('Polling')

  useEffect(() => {
    let mounted = true

    const loadPrices = async () => {
      try {
        const { data } = await marketAPI.getPrices()
        if (!mounted) return

        const prices = data.prices || {}
        setPriceMap(prices)
        if (prices[formData.pair]?.price) {
          setFormData((previous) => ({
            ...previous,
            entryPrice: Number(prices[previous.pair]?.price || previous.entryPrice),
          }))
        }
        setError('')
      } catch (err) {
        if (mounted) {
          setError(err.response?.data?.detail || 'Failed to load market prices')
        }
      }
    }

    loadPrices()
    const interval = setInterval(loadPrices, 8000)

    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [formData.pair])

  useEffect(() => {
    if (!formData.pair) return undefined

    const socket = new WebSocket(marketAPI.getPriceStreamUrl(formData.pair))

    socket.onopen = () => setStreamState('Live')
    socket.onerror = () => setStreamState('Reconnecting')
    socket.onclose = () => setStreamState('Polling')
    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data)
        if (payload.type !== 'price_update') return

        const nextPrice = {
          price: Number(payload.price),
          bid: Number(payload.bid),
          ask: Number(payload.ask),
          change: Number(payload.change),
          change_percent: Number(payload.change_percent),
          volume: Number(payload.volume || 0),
        }

        setPriceMap((previous) => ({
          ...previous,
          [formData.pair]: {
            ...(previous[formData.pair] || {}),
            ...nextPrice,
          },
        }))

        setFormData((previous) => ({
          ...previous,
          entryPrice: nextPrice.price,
        }))
      } catch {
        setStreamState('Polling')
      }
    }

    return () => {
      socket.close()
    }
  }, [formData.pair])

  const handleChange = (event) => {
    const { name, value } = event.target
    setError('')
    setSuccessMessage('')

    setFormData((previous) => ({
      ...previous,
      [name]: name === 'pair' || name === 'tradeType' ? value : Number(value),
    }))
  }

  const handlePairSelect = (pair) => {
    const nextPrice = priceMap[pair]?.price || formData.entryPrice
    setFormData((previous) => ({
      ...previous,
      pair,
      entryPrice: Number(nextPrice),
    }))
  }

  const applyPreset = (amount) => {
    const suggestedStop = Math.max(Math.round(amount * 0.4), 10)
    setError('')
    setSuccessMessage('')
    setFormData((previous) => ({
      ...previous,
      amount,
      stopLoss: suggestedStop,
      takeProfit: suggestedStop * 2,
    }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSuccessMessage('')
    setLoading(true)

    try {
      const direction = formData.tradeType === 'BUY' ? 'long' : 'short'

      await tradeAPI.createTrade({
        pair: formData.pair,
        direction,
        stake_kes: formData.amount,
        leverage: formData.leverage,
        open_price: priceMap[formData.pair]?.price || formData.entryPrice,
        stop_loss_kes: formData.stopLoss,
        take_profit_kes: formData.takeProfit,
      })

      const meResponse = await authAPI.me()
      updateUser(meResponse.data.user)

      setSuccessMessage(`${formData.tradeType === 'BUY' ? 'Long' : 'Short'} position opened on ${formData.pair}.`)
      setFormData((previous) => ({
        ...previous,
        amount: 500,
        leverage: tradeMode === 'simple' ? 3 : 5,
        stopLoss: 50,
        takeProfit: 100,
      }))
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to execute trade')
    } finally {
      setLoading(false)
    }
  }

  const pairs = useMemo(
    () =>
      Object.entries(priceMap).length
        ? Object.entries(priceMap).map(([pair, value]) => ({ value: pair, ...value }))
        : [
            { value: 'EUR/USD', price: 1.085, change_percent: 0.12, volume: 8200 },
            { value: 'GBP/USD', price: 1.2743, change_percent: -0.08, volume: 7600 },
            { value: 'USD/JPY', price: 149.52, change_percent: 0.21, volume: 9300 },
            { value: 'XAU/USD', price: 2050.2, change_percent: 0.44, volume: 6100 },
            { value: 'BTC/USD', price: 42520.5, change_percent: 1.12, volume: 13200 },
          ],
    [priceMap]
  )

  const selectedPrice = priceMap[formData.pair] || {}
  const precision = (selectedPrice.price || formData.entryPrice) > 1000 ? 1 : 4
  const usdKesRate = Number(priceMap['USD/KES']?.price || 129.5)
  const amountApproxUsd = formData.amount / usdKesRate
  const notionalValue = formData.amount * formData.leverage
  const riskRatio = formData.stopLoss ? formData.takeProfit / formData.stopLoss : 0
  const maintenanceBuffer = formData.amount * 0.35
  const liquidationMove = notionalValue ? maintenanceBuffer / (notionalValue / Math.max(formData.entryPrice, 0.0001)) : 0
  const liquidationPrice =
    formData.tradeType === 'BUY'
      ? formData.entryPrice - liquidationMove
      : formData.entryPrice + liquidationMove
  const spread =
    selectedPrice.ask && selectedPrice.bid ? Math.abs(selectedPrice.ask - selectedPrice.bid) : Math.max(formData.entryPrice * 0.0002, 0.0001)
  const microTrend = buildMiniTrend(selectedPrice.price || formData.entryPrice, selectedPrice.change_percent || 0)
  const book = buildOrderBook(selectedPrice)
  const pairSentiment = (selectedPrice.change_percent || 0) >= 0 ? 'Bullish momentum' : 'Bearish pressure'
  const beginnerNote =
    tradeMode === 'simple'
      ? `You are trading from a Kenyan-shilling wallet. Use a small amount like KSh 50 to KSh 500 while learning, and let the platform handle the market-price math.`
      : `Advanced mode shows more market detail, but your balance, margin, and P&L still remain in Kenyan shillings.`

  return (
    <div className="min-h-screen bg-[#02050b] pt-6 pb-12">
      <div className="mx-auto max-w-[1700px] px-4 sm:px-5">
        <section className="mb-6 overflow-hidden rounded-[28px] border border-dark-800 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.16),transparent_28%),radial-gradient(circle_at_top_right,rgba(34,197,94,0.14),transparent_22%),linear-gradient(145deg,#121826_0%,#0a0f19_55%,#06080f_100%)] p-4 sm:p-6">
          <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
            <div>
              <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-dark-300">
                <Radio className="h-4 w-4 text-success-400" />
                {streamState} Feed
              </div>
              <h1 className="text-3xl sm:text-4xl font-display font-bold text-white">Forex Execution Terminal</h1>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-dark-300">
                Execute simulated forex and crypto trades using Kenyan shillings, with student-friendly presets and guided risk controls.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-dark-400">Wallet</p>
                <p className="mt-2 text-xl font-semibold text-white">{formatCurrency(user?.balance || 0, 0)}</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-dark-400">Spread</p>
                <p className="mt-2 text-xl font-semibold text-white">{formatNumber(spread, precision)}</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-dark-400">Student Entry</p>
                <p className="mt-2 text-sm font-semibold text-success-300">From KSh 50</p>
              </div>
            </div>
          </div>
        </section>

        {error && (
          <div className="mb-6 rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        {successMessage && (
          <div className="mb-6 rounded-2xl border border-success-500/30 bg-success-500/10 px-4 py-3 text-sm text-success-300">
            {successMessage}
          </div>
        )}

        <div className="grid gap-6 2xl:grid-cols-[260px_minmax(0,1fr)_340px]">
          <aside className="rounded-2xl border border-dark-800 bg-black/70 p-4">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-sm font-semibold uppercase tracking-[0.16em] text-dark-400">Pairs</h2>
              <Layers3 className="h-4 w-4 text-dark-500" />
            </div>

            <div className="space-y-3">
              {pairs.map((pair) => {
                const active = pair.value === formData.pair
                const positive = (pair.change_percent || 0) >= 0
                return (
                  <button
                    key={pair.value}
                    onClick={() => handlePairSelect(pair.value)}
                    className={`w-full rounded-xl border px-4 py-4 text-left transition ${
                      active
                        ? 'border-primary-500 bg-primary-500/10 shadow-[0_0_0_1px_rgba(59,130,246,0.16)]'
                        : 'border-dark-800 bg-dark-950/80 hover:border-dark-700 hover:bg-dark-900'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <p className="font-semibold text-dark-100">{pair.value}</p>
                      <p className={`text-xs font-semibold ${positive ? 'text-success-400' : 'text-red-400'}`}>
                        {positive ? '+' : ''}
                        {formatNumber(pair.change_percent || 0, 2)}%
                      </p>
                    </div>
                    <div className="mt-3 flex items-end justify-between">
                      <p className="text-lg font-semibold text-dark-100">
                        {formatNumber(pair.price || 0, (pair.price || 0) > 1000 ? 1 : 4)}
                      </p>
                      <p className="text-xs text-dark-500">Vol {formatNumber(pair.volume || 0, 0)}</p>
                    </div>
                  </button>
                )
              })}
            </div>
          </aside>

          <main className="space-y-6">
            <section className="rounded-2xl border border-dark-800 bg-black/70 p-5">
              <div className="mb-5 flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    <h2 className="text-3xl font-semibold text-dark-100">{formData.pair}</h2>
                    <span className="rounded-full bg-dark-900 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-dark-400">
                      Spot simulator
                    </span>
                  </div>
                  <div className="mt-3 flex flex-wrap items-center gap-3">
                    <p className="text-4xl font-semibold text-dark-100">
                      {formatNumber(selectedPrice.price || formData.entryPrice, precision)}
                    </p>
                    <div
                      className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-semibold ${
                        (selectedPrice.change_percent || 0) >= 0 ? 'bg-success-500/10 text-success-400' : 'bg-red-500/10 text-red-400'
                      }`}
                    >
                      {(selectedPrice.change_percent || 0) >= 0 ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
                      {(selectedPrice.change_percent || 0) >= 0 ? '+' : ''}
                      {formatNumber(selectedPrice.change || 0, precision)}
                      <span>
                        {(selectedPrice.change_percent || 0) >= 0 ? '+' : ''}
                        {formatNumber(selectedPrice.change_percent || 0, 2)}%
                      </span>
                    </div>
                  </div>
                </div>

                <div className="grid gap-3 md:grid-cols-4">
                  {[
                    ['Bid', selectedPrice.bid],
                    ['Ask', selectedPrice.ask],
                    ['Volume', selectedPrice.volume],
                    ['Sentiment', pairSentiment],
                  ].map(([label, value]) => (
                    <div key={label} className="rounded-xl border border-dark-800 bg-dark-950/80 px-4 py-3">
                      <p className="text-[11px] uppercase tracking-[0.16em] text-dark-500">{label}</p>
                      <p className="mt-2 text-sm font-semibold text-dark-100">
                        {typeof value === 'number' ? formatNumber(value, label === 'Volume' ? 0 : precision) : value}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-2xl border border-dark-800 bg-[#05070d] p-4">
                <div className="mb-4 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CandlestickChart className="h-5 w-5 text-warning-400" />
                    <p className="font-semibold text-dark-100">Price Pulse</p>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-dark-500">
                    <Activity className="h-4 w-4" />
                    24-tick synthetic overview
                  </div>
                </div>

                <div className="flex h-48 items-end gap-1 rounded-xl border border-dark-800 bg-[linear-gradient(180deg,rgba(255,255,255,0.01),transparent)] p-3">
                  {microTrend.map((point, index) => {
                    const min = Math.min(...microTrend)
                    const max = Math.max(...microTrend)
                    const height = ((point - min) / Math.max(max - min, 1)) * 100
                    const rising = index === 0 ? true : point >= microTrend[index - 1]
                    return (
                      <div key={`${point}-${index}`} className="flex flex-1 items-end justify-center">
                        <div
                          className={`w-full rounded-t ${rising ? 'bg-success-400/80' : 'bg-fuchsia-400/80'}`}
                          style={{ height: `${Math.max(height, 10)}%` }}
                        />
                      </div>
                    )
                  })}
                </div>

                <div className="mt-4 grid gap-3 md:grid-cols-3">
                  <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3">
                    <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Trade Bias</p>
                    <p className={`mt-2 text-sm font-semibold ${(selectedPrice.change_percent || 0) >= 0 ? 'text-success-400' : 'text-red-400'}`}>
                      {(selectedPrice.change_percent || 0) >= 0 ? 'Buy-side strength' : 'Sell-side pressure'}
                    </p>
                  </div>
                  <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3">
                    <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Execution Style</p>
                    <p className="mt-2 text-sm font-semibold text-dark-100">
                      {tradeMode === 'simple' ? 'KES-first guided order' : 'Advanced live market order'}
                    </p>
                  </div>
                  <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3">
                    <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Latency State</p>
                    <p className="mt-2 text-sm font-semibold text-primary-300">{streamState}</p>
                  </div>
                </div>
              </div>
            </section>

            <section className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_300px]">
              <form onSubmit={handleSubmit} className="rounded-2xl border border-dark-800 bg-black/70 p-5">
                <div className="mb-5 flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-dark-100">Order Ticket</h3>
                    <p className="text-sm text-dark-400">Trade in Kenyan shillings first, without forcing students to convert currencies manually.</p>
                  </div>
                  <Send className="h-5 w-5 text-primary-400" />
                </div>

                <div className="mb-5 rounded-2xl border border-dark-800 bg-dark-950/70 p-4">
                  <div className="mb-3 flex items-center gap-2">
                    <Info className="h-4 w-4 text-primary-300" />
                    <p className="text-sm font-medium text-dark-100">Trading Mode</p>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 rounded-xl bg-[#070b14] p-1">
                    <button
                      type="button"
                      onClick={() => {
                        setTradeMode('simple')
                        setFormData((previous) => ({ ...previous, leverage: 3 }))
                      }}
                      className={`rounded-lg px-4 py-3 text-sm font-semibold ${
                        tradeMode === 'simple' ? 'bg-primary-600 text-white' : 'text-dark-300'
                      }`}
                    >
                      Simple Mode
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setTradeMode('advanced')
                        setFormData((previous) => ({ ...previous, leverage: Math.max(previous.leverage, 5) }))
                      }}
                      className={`rounded-lg px-4 py-3 text-sm font-semibold ${
                        tradeMode === 'advanced' ? 'bg-dark-700 text-white' : 'text-dark-300'
                      }`}
                    >
                      Advanced Mode
                    </button>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-dark-400">{beginnerNote}</p>
                </div>

                <div className="mb-5 grid grid-cols-1 sm:grid-cols-2 gap-2 rounded-xl bg-dark-950 p-1">
                  <button
                    type="button"
                    onClick={() => setFormData((previous) => ({ ...previous, tradeType: 'BUY' }))}
                    className={`rounded-lg px-4 py-3 text-sm font-semibold ${
                      formData.tradeType === 'BUY' ? 'bg-success-600 text-white' : 'text-dark-300'
                    }`}
                  >
                    Buy / Long
                  </button>
                  <button
                    type="button"
                    onClick={() => setFormData((previous) => ({ ...previous, tradeType: 'SELL' }))}
                    className={`rounded-lg px-4 py-3 text-sm font-semibold ${
                      formData.tradeType === 'SELL' ? 'bg-red-600 text-white' : 'text-dark-300'
                    }`}
                  >
                    Sell / Short
                  </button>
                </div>

                <div className="mb-5">
                  <label className="mb-2 block text-xs uppercase tracking-[0.16em] text-dark-500">Quick KES Presets</label>
                  <div className="grid grid-cols-2 gap-2 md:grid-cols-6">
                    {KES_PRESETS.map((amount) => (
                      <button
                        key={amount}
                        type="button"
                        onClick={() => applyPreset(amount)}
                        className={`rounded-xl border px-3 py-2 text-sm font-semibold transition ${
                          formData.amount === amount
                            ? 'border-primary-500 bg-primary-500/10 text-primary-300'
                            : 'border-dark-800 bg-dark-950 text-dark-300 hover:border-dark-700'
                        }`}
                      >
                        {amount < 1000 ? `KSh ${amount}` : `KSh ${amount / 1000}k`}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="mb-2 block text-xs uppercase tracking-[0.16em] text-dark-500">Instrument</label>
                    <select name="pair" value={formData.pair} onChange={handleChange} className="input-field">
                      {pairs.map((pair) => (
                        <option key={pair.value} value={pair.value}>
                          {pair.value}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="mb-2 block text-xs uppercase tracking-[0.16em] text-dark-500">Entry Price</label>
                    <div className="rounded-xl border border-dark-800 bg-dark-950 px-4 py-3 text-lg font-semibold text-dark-100">
                      {formatNumber(formData.entryPrice, precision)}
                    </div>
                  </div>
                  <div>
                    <label className="mb-2 block text-xs uppercase tracking-[0.16em] text-dark-500">Margin (KES)</label>
                    <div className="relative">
                      <DollarSign className="absolute left-3 top-3 h-5 w-5 text-dark-500" />
                      <input
                        type="number"
                        name="amount"
                        value={formData.amount}
                        onChange={handleChange}
                        className="input-field pl-10"
                        min="50"
                        step="50"
                        required
                      />
                    </div>
                    <p className="mt-2 text-xs text-dark-500">
                      Approx. ${formatNumber(amountApproxUsd, 2)} equivalent, but the experience stays KES-first.
                    </p>
                  </div>
                  {tradeMode === 'advanced' ? (
                    <div>
                      <label className="mb-2 block text-xs uppercase tracking-[0.16em] text-dark-500">Leverage</label>
                      <input
                        type="number"
                        name="leverage"
                        value={formData.leverage}
                        onChange={handleChange}
                        className="input-field"
                        min="1"
                        max="50"
                        step="1"
                        required
                      />
                    </div>
                  ) : (
                    <div>
                      <label className="mb-2 block text-xs uppercase tracking-[0.16em] text-dark-500">Leverage</label>
                      <div className="rounded-xl border border-dark-800 bg-dark-950 px-4 py-3 text-lg font-semibold text-dark-100">
                        {formData.leverage}x
                      </div>
                      <p className="mt-2 text-xs text-dark-500">Simple mode keeps leverage low for safer student practice.</p>
                    </div>
                  )}
                  <div>
                    <label className="mb-2 block text-xs uppercase tracking-[0.16em] text-dark-500">Stop Loss (KES)</label>
                    <input
                      type="number"
                      name="stopLoss"
                      value={formData.stopLoss}
                      onChange={handleChange}
                      className="input-field"
                      min="0"
                      step="10"
                      required
                    />
                    <p className="mt-2 text-xs text-dark-500">Your planned maximum loss in Kenyan shillings.</p>
                  </div>
                  <div>
                    <label className="mb-2 block text-xs uppercase tracking-[0.16em] text-dark-500">Take Profit (KES)</label>
                    <input
                      type="number"
                      name="takeProfit"
                      value={formData.takeProfit}
                      onChange={handleChange}
                      className="input-field"
                      min="0"
                      step="10"
                      required
                    />
                    <p className="mt-2 text-xs text-dark-500">Your planned target profit in Kenyan shillings.</p>
                  </div>
                </div>

                <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                  <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3">
                    <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Notional</p>
                    <p className="mt-2 text-sm font-semibold text-dark-100">{formatCurrency(notionalValue, 0)}</p>
                  </div>
                  <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3">
                    <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Risk / Reward</p>
                    <p className="mt-2 text-sm font-semibold text-primary-300">1:{formatNumber(riskRatio, 2)}</p>
                  </div>
                  <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3">
                    <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Liquidation</p>
                    <p className="mt-2 text-sm font-semibold text-warning-300">{formatNumber(liquidationPrice, precision)}</p>
                  </div>
                  <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3">
                    <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Free Balance</p>
                    <p className="mt-2 text-sm font-semibold text-dark-100">{formatCurrency((user?.balance || 0) - formData.amount, 0)}</p>
                  </div>
                </div>

                <div className="mt-5 rounded-2xl border border-primary-500/20 bg-primary-500/5 px-4 py-4">
                  <p className="text-sm font-semibold text-primary-300">KES-first explanation</p>
                  <p className="mt-2 text-sm leading-6 text-dark-300">
                    You are using <span className="font-semibold text-dark-100">{formatCurrency(formData.amount, 0)}</span> as margin to control
                    around <span className="font-semibold text-dark-100"> {formatCurrency(notionalValue, 0)}</span> of simulated exposure. Your plan is
                    to cap the downside at <span className="font-semibold text-red-300">{formatCurrency(formData.stopLoss, 0)}</span> and aim for
                    <span className="font-semibold text-success-300"> {formatCurrency(formData.takeProfit, 0)}</span> in profit.
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className={`mt-5 w-full rounded-xl px-4 py-3 text-sm font-semibold text-white ${
                    formData.tradeType === 'BUY' ? 'bg-success-600 hover:bg-success-700' : 'bg-red-600 hover:bg-red-700'
                  } disabled:cursor-not-allowed disabled:opacity-50`}
                >
                  {loading ? 'Executing...' : `${formData.tradeType === 'BUY' ? 'Buy' : 'Sell'} ${formData.pair}`}
                </button>
              </form>

              <div className="space-y-6">
                <section className="rounded-2xl border border-dark-800 bg-black/70 p-5">
                  <div className="mb-4 flex items-center gap-2">
                    <ShieldCheck className="h-5 w-5 text-success-400" />
                    <h3 className="text-lg font-semibold text-dark-100">Student Risk Panel</h3>
                  </div>

                  <div className="space-y-3 text-sm">
                    <div className="flex items-center justify-between rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3">
                      <span className="text-dark-400">Margin Used</span>
                      <span className="font-semibold text-dark-100">{formatCurrency(formData.amount, 0)}</span>
                    </div>
                    <div className="flex items-center justify-between rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3">
                      <span className="text-dark-400">Exposure</span>
                      <span className="font-semibold text-dark-100">{formatCurrency(notionalValue, 0)}</span>
                    </div>
                    <div className="flex items-center justify-between rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3">
                      <span className="text-dark-400">Stop Loss</span>
                      <span className="font-semibold text-red-400">{formatCurrency(formData.stopLoss, 0)}</span>
                    </div>
                    <div className="flex items-center justify-between rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3">
                      <span className="text-dark-400">Take Profit</span>
                      <span className="font-semibold text-success-400">{formatCurrency(formData.takeProfit, 0)}</span>
                    </div>
                    <div className="flex items-center justify-between rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3">
                      <span className="text-dark-400">2% Rule Check</span>
                      <span className={(formData.stopLoss || 0) <= (user?.balance || 0) * 0.02 ? 'font-semibold text-success-400' : 'font-semibold text-red-400'}>
                        {(formData.stopLoss || 0) <= (user?.balance || 0) * 0.02 ? 'Within Rule' : 'Above Rule'}
                      </span>
                    </div>
                    <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3 text-dark-300">
                      <p className="font-medium text-dark-100">Beginner guide</p>
                      <p className="mt-2 leading-6">
                        Start with <span className="text-primary-300">KSh 50 to KSh 500</span>, keep losses small, and build confidence before scaling up.
                      </p>
                    </div>
                  </div>
                </section>

                <section className="rounded-2xl border border-dark-800 bg-black/70 p-5">
                  <div className="mb-4 flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-primary-400" />
                    <h3 className="text-lg font-semibold text-dark-100">Depth Snapshot</h3>
                  </div>

                  <div className="overflow-x-auto">
                    <div className="min-w-[260px]">
                      <div className="grid grid-cols-[1fr_72px_90px] gap-2 border-b border-dark-800 pb-2 text-[11px] uppercase tracking-[0.16em] text-dark-500">
                        <span>Price</span>
                        <span>Size</span>
                        <span>Total</span>
                      </div>

                      <div className="mt-2 space-y-1">
                        {book.asks.map((row) => (
                          <div key={`ask-${row.price}`} className="grid grid-cols-[1fr_72px_90px] gap-2 rounded-lg bg-red-500/6 px-2 py-1.5 text-sm">
                            <span className="text-red-300">{formatNumber(row.price, precision)}</span>
                            <span className="text-dark-300">{formatNumber(row.size, 3)}</span>
                            <span className="text-dark-400">{formatNumber(row.total, 2)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="my-3 rounded-xl border border-dark-800 bg-dark-950/90 px-3 py-3 text-center">
                    <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Mid Price</p>
                    <p className="mt-1 text-xl font-semibold text-dark-100">
                      {formatNumber(selectedPrice.price || formData.entryPrice, precision)}
                    </p>
                  </div>

                  <div className="overflow-x-auto">
                    <div className="min-w-[260px] space-y-1">
                      {book.bids.map((row) => (
                        <div key={`bid-${row.price}`} className="grid grid-cols-[1fr_72px_90px] gap-2 rounded-lg bg-success-500/6 px-2 py-1.5 text-sm">
                          <span className="text-success-300">{formatNumber(row.price, precision)}</span>
                          <span className="text-dark-300">{formatNumber(row.size, 3)}</span>
                          <span className="text-dark-400">{formatNumber(row.total, 2)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </section>
              </div>
            </section>
          </main>

          <aside className="space-y-6">
            <section className="rounded-2xl border border-dark-800 bg-black/70 p-5">
              <div className="mb-4 flex items-center gap-2">
                <TimerReset className="h-5 w-5 text-warning-400" />
                <h3 className="text-lg font-semibold text-dark-100">Execution Notes</h3>
              </div>

              <div className="space-y-3 text-sm">
                <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3 text-dark-300">
                  Orders are sent as market executions against the live simulated quote.
                </div>
                <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3 text-dark-300">
                  The user funds and risk plan stay in Kenyan shillings even when the instrument itself is priced in USD.
                </div>
                <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3 text-dark-300">
                  There is no need for manual conversion. The platform translates KES margin into simulated exposure for the student.
                </div>
              </div>
            </section>

            <section className="rounded-2xl border border-dark-800 bg-black/70 p-5">
              <div className="mb-4 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-success-400" />
                <h3 className="text-lg font-semibold text-dark-100">Student-Friendly Tips</h3>
              </div>

              <div className="space-y-3">
                <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Start Small</p>
                  <p className="mt-2 text-sm text-dark-300">Use KSh 50, KSh 100, or KSh 500 presets while learning price movement and trade discipline.</p>
                </div>
                <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Think in KES</p>
                  <p className="mt-2 text-sm text-dark-300">Plan loss and profit in shillings, not in lot sizes or foreign base currencies.</p>
                </div>
                <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3">
                  <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Upgrade Later</p>
                  <p className="mt-2 text-sm text-dark-300">Move to Advanced Mode only when you want more control over leverage and execution detail.</p>
                </div>
              </div>
            </section>

            <section className="rounded-2xl border border-dark-800 bg-black/70 p-5">
              <div className="mb-4 flex items-center gap-2">
                <TrendingDown className="h-5 w-5 text-red-400" />
                <h3 className="text-lg font-semibold text-dark-100">Risk Warnings</h3>
              </div>

              <ul className="space-y-3 text-sm text-dark-300">
                <li className="rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3">
                  Higher leverage narrows the distance to liquidation.
                </li>
                <li className="rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3">
                  A small wallet should use small stop losses and controlled exposure.
                </li>
                <li className="rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-3">
                  Simulated prices move quickly. Re-check entry and risk every time you switch pairs.
                </li>
              </ul>
            </section>
          </aside>
        </div>
      </div>
    </div>
  )
}
