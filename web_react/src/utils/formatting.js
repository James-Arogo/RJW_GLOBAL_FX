/**
 * Format currency as Kenyan Shilling (KES)
 */
export const formatCurrency = (value, decimals = 0) => {
  if (value === null || value === undefined) return 'KES 0'

  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

/**
 * Format percentage
 */
export const formatPercent = (value) => {
  if (value === null || value === undefined) return '0%'
  return `${parseFloat(value).toFixed(2)}%`
}

/**
 * Format date and time
 */
export const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-KE', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

/**
 * Format date only
 */
export const formatDateOnly = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-KE', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date)
}

/**
 * Format time ago (e.g., "2 hours ago")
 */
export const formatTimeAgo = (dateString) => {
  if (!dateString) return '-'

  const date = new Date(dateString)
  const now = new Date()
  const seconds = Math.floor((now - date) / 1000)

  let interval = seconds / 31536000
  if (interval > 1) return Math.floor(interval) + 'y ago'

  interval = seconds / 2592000
  if (interval > 1) return Math.floor(interval) + 'mo ago'

  interval = seconds / 86400
  if (interval > 1) return Math.floor(interval) + 'd ago'

  interval = seconds / 3600
  if (interval > 1) return Math.floor(interval) + 'h ago'

  interval = seconds / 60
  if (interval > 1) return Math.floor(interval) + 'm ago'

  return Math.floor(seconds) + 's ago'
}

/**
 * Format number with decimals
 */
export const formatNumber = (value, decimals = 2) => {
  if (value === null || value === undefined) return '0'
  return parseFloat(value).toFixed(decimals)
}

/**
 * Get color for P&L
 */
export const getPLColor = (pnl) => {
  if (pnl > 0) return 'text-success-400'
  if (pnl < 0) return 'text-red-400'
  return 'text-dark-400'
}

/**
 * Get badge color for trade status
 */
export const getStatusBadgeColor = (status) => {
  switch (status?.toUpperCase()) {
    case 'OPEN':
      return 'badge-info'
    case 'CLOSED':
      return 'badge-success'
    case 'CANCELLED':
      return 'badge-danger'
    default:
      return 'badge-warning'
  }
}
