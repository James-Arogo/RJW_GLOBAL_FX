import React from 'react'
import { Wallet, TrendingUp, TrendingDown } from 'lucide-react'
import { formatCurrency, getPLColor } from '../utils/formatting'

export const BalanceCard = ({ balance, dailyPNL, pnlPercent }) => {
  const isPositive = dailyPNL >= 0

  return (
    <div className="card bg-gradient-to-br from-dark-800 to-dark-900">
      <div className="flex items-start justify-between mb-6">
        <div>
          <p className="text-dark-400 text-sm mb-2">Account Balance</p>
          <p className="text-3xl font-display font-bold text-primary-400">
            {formatCurrency(balance, 0)}
          </p>
        </div>
        <Wallet className="w-8 h-8 text-primary-500 opacity-20" />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-dark-900 rounded-lg p-4">
          <p className="text-dark-400 text-xs mb-2">Today's P&L</p>
          <div className="flex items-center gap-2">
            {isPositive ? (
              <TrendingUp className="w-5 h-5 text-success-400" />
            ) : (
              <TrendingDown className="w-5 h-5 text-red-400" />
            )}
            <p className={`font-semibold ${getPLColor(dailyPNL)}`}>
              {isPositive ? '+' : ''}{formatCurrency(dailyPNL, 0)}
            </p>
          </div>
        </div>

        <div className="bg-dark-900 rounded-lg p-4">
          <p className="text-dark-400 text-xs mb-2">Return</p>
          <p className={`font-semibold text-lg ${getPLColor(pnlPercent)}`}>
            {isPositive ? '+' : ''}{pnlPercent?.toFixed(2)}%
          </p>
        </div>
      </div>
    </div>
  )
}
