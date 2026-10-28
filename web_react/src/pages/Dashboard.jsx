import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { BarChart3, TrendingUp, TrendingDown, Eye } from 'lucide-react'
import { BalanceCard } from '../components/BalanceCard'
import { StatCard } from '../components/StatCard'
import { useAuth } from '../context/AuthContext'
import { formatCurrency } from '../utils/formatting'
import { dashboardAPI } from '../utils/api'

export const Dashboard = () => {
  const { user, updateUser } = useAuth()
  const [stats, setStats] = useState({
    totalTrades: 0,
    winRate: 0,
    totalPNL: 0,
    dailyPNL: 0,
  })
  const [recentTrades, setRecentTrades] = useState([])
  const [openPositions, setOpenPositions] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    let mounted = true

    const loadDashboard = async () => {
      try {
        const [summaryResponse, tradesResponse, positionsResponse] = await Promise.all([
          dashboardAPI.getSummary(),
          dashboardAPI.getRecentTrades(5),
          dashboardAPI.getOpenTrades(),
        ])

        if (!mounted) return

        const summary = summaryResponse.data
        setStats({
          totalTrades: summary.statistics.total_trades,
          winRate: summary.statistics.win_rate_percent,
          totalPNL: summary.profitability.total_profit_kes,
          dailyPNL: summary.profitability.daily_profit_kes,
        })
        setRecentTrades(summary.statistics.total_trades ? tradesResponse.data.trades : [])
        setOpenPositions(positionsResponse.data.positions || [])
        updateUser(summary.user)
        setError('')
      } catch (err) {
        if (mounted) {
          setError(err.response?.data?.detail || 'Failed to load dashboard')
        }
      }
    }

    loadDashboard()
  }, [])

  return (
    <div className="min-h-screen bg-dark-950 pt-8 pb-12">
      <div className="max-w-7xl mx-auto px-4">
        {/* Welcome */}
        <div className="mb-8">
          <h1 className="text-3xl font-display font-bold text-dark-100 mb-2">
            Welcome back, {user?.username}! 👋
          </h1>
          <p className="text-dark-400">Here's your trading performance overview</p>
        </div>

        {error && (
          <div className="mb-6 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
            {error}
          </div>
        )}

        {/* Balance Card */}
        <div className="mb-8">
          <BalanceCard
            balance={user?.balance ?? 0}
            dailyPNL={stats.dailyPNL}
            pnlPercent={(stats.dailyPNL / Math.max(user?.balance || 1, 1)) * 100}
          />
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            icon={Eye}
            label="Total Trades"
            value={stats.totalTrades}
            subtext="since you started"
            color="primary"
          />
          <StatCard
            icon={TrendingUp}
            label="Win Rate"
            value={`${stats.winRate}%`}
            subtext={`${Math.ceil(stats.totalTrades * stats.winRate / 100)} wins`}
            color="success"
          />
          <StatCard
            icon={BarChart3}
            label="Total P&L"
            value={formatCurrency(stats.totalPNL, 0)}
            subtext="all time"
            color="success"
          />
          <StatCard
            icon={TrendingDown}
            label="Level"
            value="🥈 Intermediate"
            subtext="6-20 trades"
            color="warning"
          />
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="text-lg font-bold text-dark-100 mb-4">Recent Activity</h3>
            <div className="space-y-3">
              {recentTrades.length === 0 && (
                <div className="rounded-lg bg-dark-900 p-3 text-sm text-dark-400">
                  No trades yet. Open your first simulated position to start tracking performance.
                </div>
              )}
              {recentTrades.map((trade) => (
                <div key={trade.id} className="flex items-center justify-between p-3 bg-dark-900 rounded-lg">
                  <div className="flex-1">
                    <p className="font-semibold text-dark-100">{trade.pair}</p>
                    <p className="text-xs text-dark-400">
                      {trade.direction?.toUpperCase()} {formatCurrency(trade.stake_kes, 0)}
                    </p>
                  </div>
                  <p className={`font-bold ${(trade.profit_kes || 0) >= 0 ? 'text-success-400' : 'text-red-400'}`}>
                    {(trade.profit_kes || 0) >= 0 ? '+' : ''}{formatCurrency(trade.profit_kes || 0, 0)}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-bold text-dark-100 mb-4">Open Positions</h3>
            <div className="space-y-3">
              {openPositions.length === 0 && (
                <div className="rounded-lg bg-dark-900 p-3 text-sm text-dark-400">
                  No live positions open right now.
                </div>
              )}
              {openPositions.map((position) => (
                <div key={position.id} className="rounded-lg bg-dark-900 p-3">
                  <div className="flex items-center justify-between">
                    <p className="font-semibold text-dark-100">{position.pair}</p>
                    <p className={`font-bold ${position.unrealized_pnl_kes >= 0 ? 'text-success-400' : 'text-red-400'}`}>
                      {position.unrealized_pnl_kes >= 0 ? '+' : ''}
                      {formatCurrency(position.unrealized_pnl_kes, 0)}
                    </p>
                  </div>
                  <p className="mt-1 text-xs text-dark-400">
                    {position.direction?.toUpperCase()} · {position.leverage}x · Margin {formatCurrency(position.margin_required_kes, 0)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-8 rounded-2xl border border-dark-700 bg-dark-800 p-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h3 className="text-xl font-bold text-dark-100">Learning Hub</h3>
              <p className="mt-2 max-w-3xl text-sm text-dark-400">
                Use the platform beyond trading: university course support, student trading club competitions, a 4-week self-learning plan, hackathon project framing, portfolio storytelling, and financial-literacy training.
              </p>
            </div>
            <Link to="/learning" className="btn-primary">
              Open Learning Hub
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
