import React from 'react'

export const StatCard = ({ icon: Icon, label, value, subtext, color = 'primary' }) => {
  const colorClasses = {
    primary: 'text-primary-400 bg-primary-500/10',
    success: 'text-success-400 bg-success-500/10',
    warning: 'text-warning-400 bg-warning-500/10',
    danger: 'text-red-400 bg-red-500/10',
  }

  return (
    <div className="card-sm">
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="text-dark-400 text-sm">{label}</p>
          <p className="text-2xl font-bold text-dark-100 mt-1">{value}</p>
          {subtext && <p className="text-xs text-dark-500 mt-1">{subtext}</p>}
        </div>
        {Icon && (
          <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
    </div>
  )
}
