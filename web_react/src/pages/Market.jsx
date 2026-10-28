import React, { useEffect, useState } from 'react'
import {
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  CandlestickChart,
  Clock3,
  Camera,
  Layers3,
  Settings2,
  TrendingDown,
  TrendingUp,
  Wallet,
} from 'lucide-react'
import { authAPI, marketAPI, tradeAPI } from '../utils/api'
import { useAuth } from '../context/AuthContext'
import { formatCurrency, formatNumber } from '../utils/formatting'

const DEFAULT_PAIR = 'BTC/USD'
const TIMEFRAME_OPTIONS = [
  { label: '1m', value: '1m' },
  { label: '5m', value: '5m' },
  { label: '15m', value: '15m' },
  { label: '1h', value: '1h' },
  { label: '4h', value: '4h' },
  { label: '1D', value: '1d' },
]

const buildCandles = (points = []) => {
  const bucketSize = 4
  const candles = []

  for (let index = 0; index < points.length; index += bucketSize) {
    const chunk = points.slice(index, index + bucketSize)
    if (!chunk.length) continue

    const open = chunk[0].price
    const close = chunk[chunk.length - 1].price
    const high = Math.max(...chunk.map((point) => point.price))
    const low = Math.min(...chunk.map((point) => point.price))
    const volume = chunk.reduce((sum, point) => sum + (point.volume || 0), 0)

    candles.push({
      time: chunk[chunk.length - 1].timestamp,
      open,
      close,
      high,
      low,
      volume,
    })
  }

  return candles.slice(-24)
}

const buildOrderBook = (priceData) => {
  if (!priceData?.price) return { bids: [], asks: [] }

  const basePrice = Number(priceData.price)
  const precision = basePrice > 1000 ? 1 : 4
  const levels = 12
  const spread = Math.max(basePrice * 0.00015, basePrice > 1000 ? 0.5 : 0.0002)

  const asks = Array.from({ length: levels }, (_, index) => {
    const price = basePrice + spread * (index + 1)
    const amount = Math.max(0.001, Number((0.08 + index * 0.013).toFixed(5)))
    return {
      price: Number(price.toFixed(precision)),
      amount,
      total: Number((price * amount).toFixed(2)),
    }
  }).reverse()

  const bids = Array.from({ length: levels }, (_, index) => {
    const price = basePrice - spread * (index + 1)
    const amount = Math.max(0.001, Number((0.09 + index * 0.011).toFixed(5)))
    return {
      price: Number(price.toFixed(precision)),
      amount,
      total: Number((price * amount).toFixed(2)),
    }
  })

  return { bids, asks }
}

const buildRecentTrades = (points = []) =>
  points
    .slice(-18)
    .reverse()
    .map((point, index, arr) => {
      const previous = arr[index + 1]?.price ?? point.price
      return {
        id: `${point.timestamp}-${index}`,
        price: point.price,
        amount: Number((0.01 + (point.volume || 1000) / 500000).toFixed(5)),
        side: point.price >= previous ? 'buy' : 'sell',
        time: new Date(point.timestamp * 1000).toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        }),
      }
    })

const TradingChart = ({ candles, latestPrice, priceChangePercent, pairLabel, timeframe, onTimeframeChange }) => {
  if (!candles.length) {
    return (
      <div className="flex h-[280px] sm:h-[340px] items-center justify-center rounded-2xl border border-dark-800 bg-dark-950/80 text-sm text-dark-500">
        Waiting for live candles...
      </div>
    )
  }

  const chartHeight = 252
  const volumeHeight = 54
  const width = 980
  const axisWidth = 72
  const prices = candles.flatMap((candle) => [candle.high, candle.low])
  const maxPrice = Math.max(...prices)
  const minPrice = Math.min(...prices)
  const paddedMax = maxPrice + (maxPrice - minPrice || maxPrice * 0.002) * 0.16
  const paddedMin = minPrice - (maxPrice - minPrice || maxPrice * 0.002) * 0.16
  const priceRange = Math.max(paddedMax - paddedMin, maxPrice * 0.003)
  const volumeMax = Math.max(...candles.map((candle) => candle.volume), 1)
  const precision = latestPrice > 1000 ? 1 : 4

  const yForPrice = (price) => 22 + ((paddedMax - price) / priceRange) * (chartHeight - 38)
  const candleWidth = (width - axisWidth) / candles.length
  const priceTicks = Array.from({ length: 5 }, (_, index) => paddedMax - (priceRange / 4) * index)
  const ohlc = candles[candles.length - 1]

  return (
    <div className="overflow-hidden rounded-2xl border border-dark-800 bg-[#05070d] shadow-[0_0_0_1px_rgba(255,255,255,0.02)]">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-dark-800 px-4 py-2.5 text-sm">
        <div className="flex items-center gap-2 text-dark-300">
          {TIMEFRAME_OPTIONS.map((item) => (
            <button
              key={item.value}
              onClick={() => onTimeframeChange(item.value)}
              className={`rounded px-2 py-1 text-xs font-semibold ${
                item.value === timeframe ? 'bg-dark-700 text-dark-50' : 'text-dark-400 hover:bg-dark-900'
              }`}
            >
              {item.label}
            </button>
          ))}
          <button className="rounded p-1.5 text-dark-400 hover:bg-dark-900">
            <Settings2 className="h-4 w-4" />
          </button>
          <button className="rounded p-1.5 text-dark-400 hover:bg-dark-900">
            <Camera className="h-4 w-4" />
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-3 text-xs">
          <span className="flex items-center gap-2 text-dark-100">
            <CandlestickChart className="h-4 w-4 text-warning-400" />
            {pairLabel.replace('/USD', '/USDT')} · {TIMEFRAME_OPTIONS.find((item) => item.value === timeframe)?.label || timeframe} · RJW FX
          </span>
          <span className="text-dark-500">O</span>
          <span className="text-dark-200">{formatNumber(ohlc.open, precision)}</span>
          <span className="text-dark-500">H</span>
          <span className="text-success-300">{formatNumber(ohlc.high, precision)}</span>
          <span className="text-dark-500">L</span>
          <span className="text-fuchsia-300">{formatNumber(ohlc.low, precision)}</span>
          <span className="text-dark-500">C</span>
          <span className="text-dark-100">{formatNumber(ohlc.close, precision)}</span>
          <span className={priceChangePercent >= 0 ? 'text-success-400' : 'text-fuchsia-400'}>
            {priceChangePercent >= 0 ? '+' : ''}
            {priceChangePercent.toFixed(2)}%
          </span>
        </div>
      </div>

      <svg viewBox={`0 0 ${width} ${chartHeight + volumeHeight + 28}`} className="h-[280px] sm:h-[340px] w-full bg-[#05070d]">
        {priceTicks.map((tick) => (
          <line
            key={tick}
            x1="0"
            x2={width - axisWidth}
            y1={yForPrice(tick)}
            y2={yForPrice(tick)}
            stroke="rgba(148,163,184,0.09)"
          />
        ))}

        {candles.map((_, index) => {
          const x = index * candleWidth + candleWidth / 2
          return (
            <line
              key={`v-${index}`}
              x1={x}
              x2={x}
              y1="20"
              y2={chartHeight - 10}
              stroke="rgba(148,163,184,0.05)"
            />
          )
        })}

        {candles.map((candle, index) => {
          const x = index * candleWidth + candleWidth / 2
          const bodyTop = yForPrice(Math.max(candle.open, candle.close))
          const bodyBottom = yForPrice(Math.min(candle.open, candle.close))
          const wickTop = yForPrice(candle.high)
          const wickBottom = yForPrice(candle.low)
          const isBull = candle.close >= candle.open
          const fill = isBull ? '#a3e635' : '#f472b6'
          const volumeBarHeight = (candle.volume / volumeMax) * volumeHeight

          return (
            <g key={candle.time}>
              <line
                x1={x}
                x2={x}
                y1={wickTop}
                y2={wickBottom}
                stroke={fill}
                strokeWidth="1.35"
              />
              <rect
                x={x - candleWidth * 0.28}
                y={Math.min(bodyTop, bodyBottom)}
                width={Math.max(candleWidth * 0.56, 3)}
                height={Math.max(Math.abs(bodyBottom - bodyTop), 2.5)}
                rx="0.8"
                fill={fill}
              />
              <rect
                x={x - candleWidth * 0.28}
                y={chartHeight + volumeHeight - volumeBarHeight + 24}
                width={Math.max(candleWidth * 0.56, 3)}
                height={volumeBarHeight}
                rx="0.8"
                fill={isBull ? 'rgba(163,230,53,0.45)' : 'rgba(244,114,182,0.45)'}
              />
            </g>
          )
        })}

        <line
          x1="0"
          x2={width - axisWidth}
          y1={yForPrice(latestPrice)}
          y2={yForPrice(latestPrice)}
          stroke="rgba(244,114,182,0.72)"
          strokeDasharray="3 4"
        />

        <rect
          x={width - axisWidth + 2}
          y={yForPrice(latestPrice) - 11}
          width={axisWidth - 6}
          height="20"
          rx="3"
          fill="#ec4899"
        />
        <text
          x={width - axisWidth / 2}
          y={yForPrice(latestPrice) + 4}
          textAnchor="middle"
          fontSize="11"
          fontWeight="700"
          fill="white"
        >
          {formatNumber(latestPrice, precision)}
        </text>

        {priceTicks.map((tick) => (
          <text
            key={`label-${tick}`}
            x={width - 8}
            y={yForPrice(tick) + 4}
            textAnchor="end"
            fontSize="11"
            fill="#9ca3af"
          >
            {formatNumber(tick, precision)}
          </text>
        ))}

        <line
          x1="0"
          x2={width - axisWidth}
          y1={chartHeight + 14}
          y2={chartHeight + 14}
          stroke="rgba(148,163,184,0.12)"
        />
        <text x="0" y={chartHeight + 10} fontSize="11" fill="#d1d5db">
          Volume
        </text>
      </svg>
    </div>
  )
}

export const Market = () => {
  const { user, updateUser } = useAuth()
  const [prices, setPrices] = useState({})
  const [priceHistory, setPriceHistory] = useState({})
  const [selectedPair, setSelectedPair] = useState(DEFAULT_PAIR)
  const [selectedTimeframe, setSelectedTimeframe] = useState('15m')
  const [candles, setCandles] = useState([])
  const [positions, setPositions] = useState({
    open_positions: 0,
    used_margin_kes: 0,
    total_notional_kes: 0,
    unrealized_pnl_kes: 0,
    positions: [],
  })
  const [streamStatus, setStreamStatus] = useState('polling')
  const [error, setError] = useState('')
  const [ticketLoading, setTicketLoading] = useState(false)
  const [ticketMessage, setTicketMessage] = useState('')
  const [ticket, setTicket] = useState({
    side: 'buy',
    stake: 500,
    leverage: 5,
    stopLoss: 50,
    takeProfit: 100,
  })

  useEffect(() => {
    let mounted = true

    const loadPrices = async () => {
      try {
        const { data } = await marketAPI.getPrices()
        if (!mounted) return

        const nextPrices = data.prices || {}
        setPrices(nextPrices)
        setPriceHistory((previous) => {
          const updated = { ...previous }

          Object.entries(nextPrices).forEach(([pair, value]) => {
            const nextPoint = {
              price: Number(value.price),
              volume: Number(value.volume || 0),
              timestamp: Number(value.timestamp || Date.now() / 1000),
            }

            updated[pair] = [...(updated[pair] || []), nextPoint].slice(-96)
          })

          return updated
        })
        setError('')
      } catch (err) {
        if (mounted) {
          setError(err.response?.data?.detail || 'Unable to load live prices')
        }
      }
    }

    loadPrices()
    const interval = setInterval(loadPrices, 8000)

    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [])

  useEffect(() => {
    if (!prices[selectedPair]) {
      const firstPair = Object.keys(prices)[0]
      if (firstPair) setSelectedPair(firstPair)
    }
  }, [prices, selectedPair])

  useEffect(() => {
    let mounted = true

    const loadCandles = async () => {
      try {
        const { data } = await marketAPI.getCandles(selectedPair, selectedTimeframe, 72)
        if (mounted) {
          setCandles((data.candles || []).map((candle) => ({ ...candle, time: candle.timestamp })))
        }
      } catch {
        if (mounted) {
          setCandles([])
        }
      }
    }

    loadCandles()

    return () => {
      mounted = false
    }
  }, [selectedPair, selectedTimeframe])

  useEffect(() => {
    let mounted = true

    const loadPositions = async () => {
      try {
        const { data } = await tradeAPI.getOpenPositions()
        if (mounted) {
          setPositions(data)
        }
      } catch {
        if (mounted) {
          setPositions({
            open_positions: 0,
            used_margin_kes: 0,
            total_notional_kes: 0,
            unrealized_pnl_kes: 0,
            positions: [],
          })
        }
      }
    }

    loadPositions()
    const interval = setInterval(loadPositions, 4000)

    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [])

  useEffect(() => {
    if (!selectedPair) return undefined

    const socket = new WebSocket(marketAPI.getPriceStreamUrl(selectedPair))

    socket.onopen = () => setStreamStatus('live')
    socket.onerror = () => setStreamStatus('reconnecting')
    socket.onclose = () => setStreamStatus('polling')
    socket.onmessage = async (event) => {
      try {
        const payload = JSON.parse(event.data)
        if (payload.type !== 'price_update') return

        const nextValue = {
          price: Number(payload.price),
          bid: Number(payload.bid),
          ask: Number(payload.ask),
          change: Number(payload.change),
          change_percent: Number(payload.change_percent),
          volume: Number(payload.volume || 0),
          timestamp: Number(payload.timestamp || Date.now() / 1000),
        }

        setPrices((previous) => ({
          ...previous,
          [selectedPair]: {
            ...(previous[selectedPair] || {}),
            ...nextValue,
          },
        }))

        setPriceHistory((previous) => ({
          ...previous,
          [selectedPair]: [...(previous[selectedPair] || []), nextValue].slice(-140),
        }))

        const candleResponse = await marketAPI.getCandles(selectedPair, selectedTimeframe, 72)
        setCandles((candleResponse.data.candles || []).map((candle) => ({ ...candle, time: candle.timestamp })))
      } catch {
        setStreamStatus('polling')
      }
    }

    return () => {
      socket.close()
    }
  }, [selectedPair, selectedTimeframe])

  const selectedPrice = prices[selectedPair]
  const selectedHistory = priceHistory[selectedPair] || []
  const resolvedCandles = candles.length ? candles : buildCandles(selectedHistory)
  const orderBook = buildOrderBook(selectedPrice)
  const recentTrades = buildRecentTrades(selectedHistory)
  const notionalExposure = ticket.stake * Math.max(ticket.leverage || 1, 1)
  const riskReward = ticket.stopLoss ? (ticket.takeProfit / ticket.stopLoss).toFixed(2) : '0.00'

  const handleTicketChange = (event) => {
    const { name, value } = event.target
    setTicket((previous) => ({
      ...previous,
      [name]: name === 'side' ? value : Number(value),
    }))
  }

  const submitTicket = async () => {
    if (!selectedPrice?.price) return

    setTicketLoading(true)
    setTicketMessage('')

    try {
      await tradeAPI.createTrade({
        pair: selectedPair,
        direction: ticket.side === 'buy' ? 'long' : 'short',
        stake_kes: ticket.stake,
        leverage: ticket.leverage,
        open_price: selectedPrice.price,
        stop_loss_kes: ticket.stopLoss,
        take_profit_kes: ticket.takeProfit,
      })

      const [{ data }, positionsResponse] = await Promise.all([authAPI.me(), tradeAPI.getOpenPositions()])
      updateUser(data.user)
      setPositions(positionsResponse.data)
      setTicketMessage(`${ticket.side === 'buy' ? 'Buy' : 'Sell'} order opened successfully.`)
    } catch (err) {
      setTicketMessage(err.response?.data?.detail || 'Unable to submit trade ticket')
    } finally {
      setTicketLoading(false)
    }
  }

  const handleCloseTrade = async (tradeId) => {
    try {
      await tradeAPI.closeTrade(tradeId, selectedPrice?.price || undefined)
      const [{ data }, positionsResponse] = await Promise.all([authAPI.me(), tradeAPI.getOpenPositions()])
      updateUser(data.user)
      setPositions(positionsResponse.data)
      setTicketMessage('Position closed successfully.')
    } catch (err) {
      setTicketMessage(err.response?.data?.detail || 'Unable to close position')
    }
  }

  return (
    <div className="min-h-screen bg-[#02050b] pt-4 pb-8">
      <div className="mx-auto max-w-[1700px] px-3 sm:px-4">
        <div className="mb-3 rounded-2xl border border-dark-800 bg-black/70 px-4 py-3 shadow-[0_20px_80px_rgba(0,0,0,0.35)]">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-center gap-3">
              <div className="rounded-2xl bg-warning-500/15 p-2 text-warning-300">
                <BarChart3 className="h-5 w-5" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-dark-100">Pro Trading Workspace</h1>
                <p className="text-sm text-dark-400">Live simulated market with exchange-style depth, tape, and quick execution</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
              <div className="rounded-xl border border-dark-800 bg-dark-950/90 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Account</p>
                <p className="mt-1 text-sm font-semibold text-dark-100">{user?.username || 'Guest'}</p>
              </div>
              <div className="rounded-xl border border-dark-800 bg-dark-950/90 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Balance</p>
                <p className="mt-1 text-sm font-semibold text-dark-100">{formatCurrency(user?.balance || 0, 0)}</p>
              </div>
              <div className="rounded-xl border border-dark-800 bg-dark-950/90 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Selected</p>
                <p className="mt-1 text-sm font-semibold text-dark-100">{selectedPair}</p>
              </div>
              <div className="rounded-xl border border-dark-800 bg-dark-950/90 px-4 py-3">
                <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Feed</p>
                <p className="mt-1 flex items-center gap-2 text-sm font-semibold text-success-400">
                  <span className="h-2 w-2 rounded-full bg-success-400 shadow-[0_0_18px_rgba(74,222,128,0.8)]" />
                  {streamStatus}
                </p>
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-3 rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        <div className="grid gap-3 2xl:grid-cols-[220px_minmax(0,1fr)_320px]">
          <aside className="rounded-2xl border border-dark-800 bg-black/70 p-3">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-semibold uppercase tracking-[0.16em] text-dark-400">Markets</h2>
              <Layers3 className="h-4 w-4 text-dark-500" />
            </div>

            <div className="space-y-2">
              {Object.entries(prices).map(([pair, value]) => {
                const active = pair === selectedPair
                const isPositive = value.change >= 0

                return (
                  <button
                    key={pair}
                    onClick={() => setSelectedPair(pair)}
                    className={`w-full rounded-xl border px-3 py-3 text-left transition-all ${
                      active
                        ? 'border-primary-500 bg-primary-500/10 shadow-[0_0_0_1px_rgba(59,130,246,0.15)]'
                        : 'border-dark-800 bg-dark-950/70 hover:border-dark-700 hover:bg-dark-900/80'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-dark-100">{pair}</span>
                      <span className={`text-xs font-semibold ${isPositive ? 'text-success-400' : 'text-fuchsia-400'}`}>
                        {isPositive ? '+' : ''}
                        {value.change_percent.toFixed(2)}%
                      </span>
                    </div>
                    <div className="mt-2 flex items-end justify-between">
                      <p className="text-lg font-semibold text-dark-100">
                        {formatNumber(value.price, value.price > 1000 ? 1 : 4)}
                      </p>
                      <p className="text-xs text-dark-500">Vol {formatNumber(value.volume || 0, 0)}</p>
                    </div>
                  </button>
                )
              })}
            </div>
          </aside>

          <main className="space-y-3">
            <section className="rounded-2xl border border-dark-800 bg-black/70 p-4">
              <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    <h2 className="text-2xl sm:text-3xl font-semibold text-dark-100 break-words">{selectedPair}</h2>
                    <span className="rounded-full bg-dark-900 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-dark-400">
                      Simulated spot
                    </span>
                  </div>
                  <div className="mt-3 flex flex-wrap items-center gap-3">
                    <p className="text-3xl sm:text-4xl font-semibold text-dark-100">
                      {selectedPrice ? formatNumber(selectedPrice.price, selectedPrice.price > 1000 ? 1 : 4) : '--'}
                    </p>
                    <div className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-semibold ${
                      (selectedPrice?.change || 0) >= 0 ? 'bg-success-500/10 text-success-400' : 'bg-fuchsia-500/10 text-fuchsia-400'
                    }`}>
                      {(selectedPrice?.change || 0) >= 0 ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
                      {(selectedPrice?.change || 0) >= 0 ? '+' : ''}
                      {selectedPrice ? formatNumber(selectedPrice.change, selectedPrice.price > 1000 ? 1 : 4) : '--'}
                      <span>
                        {(selectedPrice?.change || 0) >= 0 ? '+' : ''}
                        {selectedPrice?.change_percent?.toFixed(2) || '0.00'}%
                      </span>
                    </div>
                  </div>
                </div>

                <div className="grid w-full grid-cols-2 gap-3 md:grid-cols-4">
                  {[
                    { label: 'Bid', value: selectedPrice ? formatNumber(selectedPrice.bid, selectedPrice.price > 1000 ? 1 : 4) : '--' },
                    { label: 'Ask', value: selectedPrice ? formatNumber(selectedPrice.ask, selectedPrice.price > 1000 ? 1 : 4) : '--' },
                    { label: '24h Low', value: resolvedCandles.length ? formatNumber(Math.min(...resolvedCandles.map((c) => c.low)), selectedPrice?.price > 1000 ? 1 : 4) : '--' },
                    { label: '24h High', value: resolvedCandles.length ? formatNumber(Math.max(...resolvedCandles.map((c) => c.high)), selectedPrice?.price > 1000 ? 1 : 4) : '--' },
                  ].map((item) => (
                    <div key={item.label} className="rounded-xl border border-dark-800 bg-dark-950/80 px-3 py-3">
                      <p className="text-[11px] uppercase tracking-[0.16em] text-dark-500">{item.label}</p>
                      <p className="mt-1 text-sm font-semibold text-dark-100">{item.value}</p>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            <section className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_280px]">
              <TradingChart
                candles={resolvedCandles}
                latestPrice={selectedPrice?.price || 0}
                priceChangePercent={selectedPrice?.change_percent || 0}
                pairLabel={selectedPair}
                timeframe={selectedTimeframe}
                onTimeframeChange={setSelectedTimeframe}
              />

              <div className="rounded-2xl border border-dark-800 bg-black/70 p-4">
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-dark-100">Quick Ticket</h3>
                    <p className="text-sm text-dark-400">Open a simulated position at the live quote</p>
                  </div>
                  <Wallet className="h-5 w-5 text-primary-400" />
                </div>

                <div className="mb-4 grid grid-cols-2 gap-2 rounded-xl bg-dark-950 p-1">
                  <button
                    onClick={() => setTicket((previous) => ({ ...previous, side: 'buy' }))}
                    className={`rounded-lg px-3 py-2 text-sm font-semibold ${
                      ticket.side === 'buy' ? 'bg-success-500 text-white' : 'text-dark-300'
                    }`}
                  >
                    Buy / Long
                  </button>
                  <button
                    onClick={() => setTicket((previous) => ({ ...previous, side: 'sell' }))}
                    className={`rounded-lg px-3 py-2 text-sm font-semibold ${
                      ticket.side === 'sell' ? 'bg-fuchsia-500 text-white' : 'text-dark-300'
                    }`}
                  >
                    Sell / Short
                  </button>
                </div>

                <div className="space-y-3">
                  <div>
                    <label className="mb-2 block text-xs uppercase tracking-[0.16em] text-dark-500">Entry</label>
                    <div className="rounded-xl border border-dark-800 bg-dark-950 px-4 py-3 text-lg font-semibold text-dark-100">
                      {selectedPrice ? formatNumber(selectedPrice.price, selectedPrice.price > 1000 ? 1 : 4) : '--'}
                    </div>
                  </div>

                  <div>
                    <label className="mb-2 block text-xs uppercase tracking-[0.16em] text-dark-500">Stake (KES)</label>
                    <input name="stake" type="number" min="50" step="50" value={ticket.stake} onChange={handleTicketChange} className="input-field" />
                  </div>

                  <div>
                    <label className="mb-2 block text-xs uppercase tracking-[0.16em] text-dark-500">Leverage</label>
                    <input name="leverage" type="number" min="1" max="50" step="1" value={ticket.leverage} onChange={handleTicketChange} className="input-field" />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="mb-2 block text-xs uppercase tracking-[0.16em] text-dark-500">Stop loss</label>
                      <input name="stopLoss" type="number" min="0" step="10" value={ticket.stopLoss} onChange={handleTicketChange} className="input-field" />
                    </div>
                    <div>
                      <label className="mb-2 block text-xs uppercase tracking-[0.16em] text-dark-500">Take profit</label>
                      <input name="takeProfit" type="number" min="0" step="10" value={ticket.takeProfit} onChange={handleTicketChange} className="input-field" />
                    </div>
                  </div>
                </div>

                <div className="mt-4 rounded-xl border border-dark-800 bg-dark-950/70 p-3 text-sm">
                  <div className="mb-2 flex items-center justify-between text-dark-400">
                    <span>Estimated exposure</span>
                    <span>{formatCurrency(notionalExposure, 0)}</span>
                  </div>
                  <div className="mb-2 flex items-center justify-between text-dark-400">
                    <span>Risk / reward</span>
                    <span>1:{riskReward}</span>
                  </div>
                  <div className="mb-2 flex items-center justify-between text-dark-400">
                    <span>Margin used</span>
                    <span>{formatCurrency(ticket.stake, 0)}</span>
                  </div>
                  <div className="flex items-center justify-between text-dark-400">
                    <span>Volume</span>
                    <span>{selectedPrice?.volume ? formatNumber(selectedPrice.volume, 0) : '--'}</span>
                  </div>
                </div>

                {ticketMessage && (
                  <div className={`mt-4 rounded-xl border px-3 py-3 text-sm ${
                    ticketMessage.toLowerCase().includes('successfully')
                      ? 'border-success-500/30 bg-success-500/10 text-success-300'
                      : 'border-red-500/30 bg-red-500/10 text-red-300'
                  }`}>
                    {ticketMessage}
                  </div>
                )}

                <button
                  onClick={submitTicket}
                  disabled={ticketLoading || !selectedPrice?.price}
                  className={`mt-4 w-full rounded-xl px-4 py-3 text-sm font-semibold text-white transition ${
                    ticket.side === 'buy'
                      ? 'bg-success-600 hover:bg-success-700'
                      : 'bg-fuchsia-600 hover:bg-fuchsia-700'
                  } disabled:cursor-not-allowed disabled:opacity-50`}
                >
                  {ticketLoading ? 'Submitting...' : `${ticket.side === 'buy' ? 'Buy' : 'Sell'} ${selectedPair}`}
                </button>
              </div>
            </section>

            <section className="rounded-2xl border border-dark-800 bg-black/70 p-4">
              <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-dark-100">Open Positions</h3>
                  <p className="text-sm text-dark-400">Live P&L, margin, and close controls for active trades.</p>
                </div>

                <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
                  <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-3 py-3">
                    <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Used Margin</p>
                    <p className="mt-1 text-sm font-semibold text-dark-100">{formatCurrency(positions.used_margin_kes || 0, 0)}</p>
                  </div>
                  <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-3 py-3">
                    <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Notional</p>
                    <p className="mt-1 text-sm font-semibold text-dark-100">{formatCurrency(positions.total_notional_kes || 0, 0)}</p>
                  </div>
                  <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-3 py-3">
                    <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Unrealized P&L</p>
                    <p className={`mt-1 text-sm font-semibold ${(positions.unrealized_pnl_kes || 0) >= 0 ? 'text-success-400' : 'text-fuchsia-400'}`}>
                      {(positions.unrealized_pnl_kes || 0) >= 0 ? '+' : ''}
                      {formatCurrency(positions.unrealized_pnl_kes || 0, 0)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                {!positions.positions?.length && (
                  <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-4 py-5 text-sm text-dark-400">
                    No open positions yet. Your live leveraged trades will appear here.
                  </div>
                )}

                {positions.positions?.map((position) => (
                  <div key={position.id} className="rounded-xl border border-dark-800 bg-dark-950/80 px-4 py-4">
                    <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                      <div>
                        <div className="flex flex-wrap items-center gap-3">
                          <p className="font-semibold text-dark-100">{position.pair}</p>
                          <span className={`rounded-full px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] ${
                            position.direction === 'long' ? 'bg-success-500/10 text-success-400' : 'bg-fuchsia-500/10 text-fuchsia-400'
                          }`}>
                            {position.direction}
                          </span>
                          <span className="rounded-full bg-dark-900 px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-dark-400">
                            {position.leverage}x
                          </span>
                        </div>
                        <p className="mt-2 text-sm text-dark-400">
                          Entry {formatNumber(position.open_price, position.open_price > 1000 ? 1 : 4)} · Current {formatNumber(position.current_price, position.current_price > 1000 ? 1 : 4)} · Liq. {formatNumber(position.liquidation_price, position.liquidation_price > 1000 ? 1 : 4)}
                        </p>
                      </div>

                      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                        <div>
                          <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Margin</p>
                          <p className="mt-1 text-sm font-semibold text-dark-100">{formatCurrency(position.margin_required_kes, 0)}</p>
                        </div>
                        <div>
                          <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Notional</p>
                          <p className="mt-1 text-sm font-semibold text-dark-100">{formatCurrency(position.notional_value_kes, 0)}</p>
                        </div>
                        <div>
                          <p className="text-xs uppercase tracking-[0.16em] text-dark-500">P&L</p>
                          <p className={`mt-1 text-sm font-semibold ${position.unrealized_pnl_kes >= 0 ? 'text-success-400' : 'text-fuchsia-400'}`}>
                            {position.unrealized_pnl_kes >= 0 ? '+' : ''}
                            {formatCurrency(position.unrealized_pnl_kes, 0)}
                          </p>
                        </div>
                        <button
                          onClick={() => handleCloseTrade(position.id)}
                          className="rounded-xl bg-primary-600 px-4 py-3 text-sm font-semibold text-white hover:bg-primary-700"
                        >
                          Close
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </main>

          <aside className="space-y-3 2xl:space-y-3">
            <section className="rounded-2xl border border-dark-800 bg-black/70 p-4">
              <div className="mb-4 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-dark-100">Order Book</h3>
                <Layers3 className="h-5 w-5 text-dark-500" />
              </div>

              <div className="overflow-x-auto">
                <div className="min-w-[280px]">
                  <div className="grid grid-cols-[1fr_80px_90px] gap-2 border-b border-dark-800 pb-2 text-[11px] uppercase tracking-[0.16em] text-dark-500">
                    <span>Price</span>
                    <span>Amount</span>
                    <span>Total</span>
                  </div>

                  <div className="mt-2 space-y-1">
                    {orderBook.asks.map((row) => (
                      <div key={`ask-${row.price}`} className="grid grid-cols-[1fr_80px_90px] gap-2 rounded-lg bg-fuchsia-500/6 px-2 py-1.5 text-sm">
                        <span className="text-fuchsia-300">{formatNumber(row.price, row.price > 1000 ? 1 : 4)}</span>
                        <span className="text-dark-300">{formatNumber(row.amount, 5)}</span>
                        <span className="text-dark-400">{formatNumber(row.total, 2)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="my-3 rounded-xl border border-dark-800 bg-dark-950/90 px-3 py-3 text-center">
                <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Mid price</p>
                <p className="mt-1 text-xl font-semibold text-dark-100">
                  {selectedPrice ? formatNumber(selectedPrice.price, selectedPrice.price > 1000 ? 1 : 4) : '--'}
                </p>
              </div>

              <div className="overflow-x-auto">
                <div className="min-w-[280px] space-y-1">
                  {orderBook.bids.map((row) => (
                    <div key={`bid-${row.price}`} className="grid grid-cols-[1fr_80px_90px] gap-2 rounded-lg bg-success-500/6 px-2 py-1.5 text-sm">
                      <span className="text-success-300">{formatNumber(row.price, row.price > 1000 ? 1 : 4)}</span>
                      <span className="text-dark-300">{formatNumber(row.amount, 5)}</span>
                      <span className="text-dark-400">{formatNumber(row.total, 2)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            <section className="rounded-2xl border border-dark-800 bg-black/70 p-4">
              <div className="mb-4 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-dark-100">Recent Trades</h3>
                <Clock3 className="h-5 w-5 text-dark-500" />
              </div>

              <div className="overflow-x-auto">
                <div className="min-w-[250px]">
                  <div className="grid grid-cols-[1fr_78px_68px] gap-2 border-b border-dark-800 pb-2 text-[11px] uppercase tracking-[0.16em] text-dark-500">
                    <span>Price</span>
                    <span>Size</span>
                    <span>Time</span>
                  </div>

                  <div className="mt-2 space-y-1">
                    {recentTrades.map((trade) => (
                      <div key={trade.id} className="grid grid-cols-[1fr_78px_68px] gap-2 rounded-lg px-2 py-1.5 text-sm hover:bg-dark-900/80">
                        <span className={trade.side === 'buy' ? 'text-success-300' : 'text-fuchsia-300'}>
                          {formatNumber(trade.price, trade.price > 1000 ? 1 : 4)}
                        </span>
                        <span className="text-dark-300">{formatNumber(trade.amount, 5)}</span>
                        <span className="text-dark-500">{trade.time}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </section>

            <section className="rounded-2xl border border-dark-800 bg-black/70 p-4">
              <div className="mb-3 flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-success-400" />
                <p className="text-sm font-semibold text-dark-100">Bullish flow</p>
              </div>
              <p className="text-sm text-dark-400">
                Bid/ask depth and the tape are generated from the live simulated feed to create a more exchange-like execution feel.
              </p>

              <div className="mt-4 grid grid-cols-2 gap-3">
                <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-3 py-3">
                  <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Momentum</p>
                  <p className="mt-1 flex items-center gap-2 text-sm font-semibold text-success-400">
                    <TrendingUp className="h-4 w-4" />
                    Buy pressure
                  </p>
                </div>
                <div className="rounded-xl border border-dark-800 bg-dark-950/70 px-3 py-3">
                  <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Risk</p>
                  <p className="mt-1 flex items-center gap-2 text-sm font-semibold text-warning-400">
                    <TrendingDown className="h-4 w-4" />
                    Sim only
                  </p>
                </div>
              </div>
            </section>
          </aside>
        </div>
      </div>
    </div>
  )
}
