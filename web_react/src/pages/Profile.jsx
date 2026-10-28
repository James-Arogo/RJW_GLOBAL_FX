import React, { useEffect, useState } from 'react'
import {
  Bell,
  Calendar,
  ChevronRight,
  Info,
  KeyRound,
  LogOut,
  Mail,
  MonitorSmartphone,
  MoonStar,
  ShieldAlert,
  Save,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  User,
  Wallet,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { authAPI, dashboardAPI } from '../utils/api'
import { formatCurrency, formatDateOnly } from '../utils/formatting'

const SETTINGS_KEY = 'profilePreferences'

const loadPreferences = () => {
  try {
    const stored = localStorage.getItem(SETTINGS_KEY)
    if (!stored) {
      return {
        emailAlerts: true,
        pricePopups: true,
        soundEffects: false,
        darkTerminal: true,
        weeklyDigest: true,
      }
    }
    return JSON.parse(stored)
  } catch {
      return {
        emailAlerts: true,
        pricePopups: true,
        soundEffects: false,
        darkTerminal: true,
        weeklyDigest: true,
      }
  }
}

export const Profile = () => {
  const { user, logout, updateUser } = useAuth()
  const navigate = useNavigate()
  const [stats, setStats] = useState({
    totalTrades: 0,
    winRate: 0,
    totalPNL: 0,
    level: 'Beginner',
    equity: 0,
    unrealizedPNL: 0,
  })
  const [profileForm, setProfileForm] = useState({
    username: user?.username || '',
    email: user?.email || '',
  })
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  })
  const [preferences, setPreferences] = useState(loadPreferences)
  const [riskMode, setRiskMode] = useState('balanced')
  const [profileMessage, setProfileMessage] = useState('')
  const [passwordMessage, setPasswordMessage] = useState('')
  const [savingProfile, setSavingProfile] = useState(false)
  const [savingPassword, setSavingPassword] = useState(false)

  useEffect(() => {
    setProfileForm({
      username: user?.username || '',
      email: user?.email || '',
    })
  }, [user?.username, user?.email])

  useEffect(() => {
    let mounted = true

    const loadStats = async () => {
      try {
        const { data } = await dashboardAPI.getSummary()
        if (!mounted) return

        const totalTrades = data.statistics.total_trades
        setStats({
          totalTrades,
          winRate: data.statistics.win_rate_percent,
          totalPNL: data.profitability.total_profit_kes,
          level: totalTrades >= 20 ? 'Advanced' : totalTrades >= 6 ? 'Intermediate' : 'Beginner',
          equity: data.account?.equity_kes || data.user?.balance_kes || 0,
          unrealizedPNL: data.account?.unrealized_pnl_kes || 0,
        })
      } catch {
        // Keep account settings usable even if stats are unavailable.
      }
    }

    loadStats()

    return () => {
      mounted = false
    }
  }, [])

  useEffect(() => {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(preferences))
  }, [preferences])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const handleProfileChange = (event) => {
    const { name, value } = event.target
    setProfileMessage('')
    setProfileForm((previous) => ({ ...previous, [name]: value }))
  }

  const handlePasswordChange = (event) => {
    const { name, value } = event.target
    setPasswordMessage('')
    setPasswordForm((previous) => ({ ...previous, [name]: value }))
  }

  const submitProfile = async (event) => {
    event.preventDefault()
    setSavingProfile(true)
    setProfileMessage('')

    try {
      const payload = {
        username: profileForm.username.trim(),
        email: profileForm.email.trim().toLowerCase(),
      }
      const { data } = await authAPI.updateMe(payload)
      updateUser(data.user)
      setProfileMessage('Account details updated successfully.')
    } catch (err) {
      setProfileMessage(err.response?.data?.detail || 'Unable to update account details')
    } finally {
      setSavingProfile(false)
    }
  }

  const submitPassword = async (event) => {
    event.preventDefault()
    setPasswordMessage('')

    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setPasswordMessage('New password and confirmation do not match.')
      return
    }

    setSavingPassword(true)
    try {
      const { data } = await authAPI.changePassword({
        current_password: passwordForm.currentPassword,
        new_password: passwordForm.newPassword,
      })
      setPasswordMessage(data.message || 'Password updated successfully.')
      setPasswordForm({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      })
    } catch (err) {
      setPasswordMessage(err.response?.data?.detail || 'Unable to update password')
    } finally {
      setSavingPassword(false)
    }
  }

  const togglePreference = (key) => {
    setPreferences((previous) => ({
      ...previous,
      [key]: !previous[key],
    }))
  }

  return (
    <div className="min-h-screen bg-dark-950 pt-8 pb-12">
      <div className="mx-auto max-w-6xl px-4 sm:px-5">
        <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h1 className="text-2xl sm:text-3xl font-display font-bold text-dark-100">Account Settings</h1>
            <p className="mt-2 text-dark-400">Manage your profile, security, and trading preferences from one place.</p>
          </div>

          <button onClick={handleLogout} className="btn-danger inline-flex items-center gap-2">
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>

        <section className="mb-6 overflow-hidden rounded-[28px] border border-dark-700 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.16),transparent_34%),linear-gradient(135deg,#121a2b_0%,#0b1020_45%,#0a0f1a_100%)] p-6">
          <div className="flex flex-col gap-6 xl:flex-row xl:items-center xl:justify-between">
            <div className="flex items-start gap-4">
              <div className="flex h-18 w-18 items-center justify-center rounded-3xl bg-white/5 text-primary-300 shadow-[0_10px_30px_rgba(0,0,0,0.25)]">
                <User className="h-9 w-9" />
              </div>
              <div>
                <div className="flex flex-wrap items-center gap-3">
                  <h2 className="text-2xl font-semibold text-white">{user?.username || 'Trader'}</h2>
                  <span className="rounded-full border border-success-500/30 bg-success-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-success-300">
                    Account Active
                  </span>
                  <span className="rounded-full border border-primary-500/30 bg-primary-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-primary-300">
                    {stats.level}
                  </span>
                </div>
                <p className="mt-2 text-sm text-dark-300">{user?.email}</p>
                <p className="mt-3 max-w-2xl text-sm leading-6 text-dark-400">
                  This is your control center for account identity, trading preferences, and platform safety. Changes here update your active trading profile immediately.
                </p>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-dark-400">Wallet</p>
                <p className="mt-2 text-xl font-semibold text-white">{formatCurrency(user?.balance || 0, 0)}</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-dark-400">Equity</p>
                <p className="mt-2 text-xl font-semibold text-white">{formatCurrency(stats.equity, 0)}</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-dark-400">Unrealized P&L</p>
                <p className={`mt-2 text-xl font-semibold ${stats.unrealizedPNL >= 0 ? 'text-success-300' : 'text-red-300'}`}>
                  {stats.unrealizedPNL >= 0 ? '+' : ''}
                  {formatCurrency(stats.unrealizedPNL, 0)}
                </p>
              </div>
            </div>
          </div>
        </section>

        <div className="mb-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-2xl border border-dark-700 bg-dark-800 p-5">
            <div className="flex items-center gap-2 text-dark-400">
              <User className="h-4 w-4" />
              <span className="text-sm">Username</span>
            </div>
            <p className="mt-3 text-lg font-semibold text-dark-100">{user?.username || 'Trader'}</p>
          </div>
          <div className="rounded-2xl border border-dark-700 bg-dark-800 p-5">
            <div className="flex items-center gap-2 text-dark-400">
              <Wallet className="h-4 w-4" />
              <span className="text-sm">Wallet Balance</span>
            </div>
            <p className="mt-3 text-lg font-semibold text-dark-100">{formatCurrency(user?.balance || 0, 0)}</p>
          </div>
          <div className="rounded-2xl border border-dark-700 bg-dark-800 p-5">
            <div className="flex items-center gap-2 text-dark-400">
              <ShieldCheck className="h-4 w-4" />
              <span className="text-sm">Equity</span>
            </div>
            <p className="mt-3 text-lg font-semibold text-dark-100">{formatCurrency(stats.equity, 0)}</p>
          </div>
          <div className="rounded-2xl border border-dark-700 bg-dark-800 p-5">
            <div className="flex items-center gap-2 text-dark-400">
              <Calendar className="h-4 w-4" />
              <span className="text-sm">Member Since</span>
            </div>
            <p className="mt-3 text-lg font-semibold text-dark-100">
              {user?.created_at ? formatDateOnly(user.created_at) : 'Today'}
            </p>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
          <div className="space-y-6">
            <section className="rounded-2xl border border-dark-700 bg-dark-800 p-6">
              <div className="mb-6 flex items-center gap-3">
                <div className="rounded-xl bg-primary-500/10 p-2 text-primary-400">
                  <User className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-dark-100">Profile Details</h2>
                  <p className="text-sm text-dark-400">Update the identity other users and your trading dashboard see.</p>
                </div>
              </div>

              <form onSubmit={submitProfile} className="space-y-4">
                {profileMessage && (
                  <div className={`rounded-xl border px-4 py-3 text-sm ${
                    profileMessage.toLowerCase().includes('success')
                      ? 'border-success-500/30 bg-success-500/10 text-success-300'
                      : 'border-red-500/30 bg-red-500/10 text-red-300'
                  }`}>
                    {profileMessage}
                  </div>
                )}

                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="mb-2 block text-sm font-medium text-dark-300">Username</label>
                    <input
                      name="username"
                      value={profileForm.username}
                      onChange={handleProfileChange}
                      className="input-field"
                      required
                    />
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium text-dark-300">Email Address</label>
                    <input
                      name="email"
                      type="email"
                      value={profileForm.email}
                      onChange={handleProfileChange}
                      className="input-field"
                      required
                    />
                  </div>
                </div>

                <button type="submit" disabled={savingProfile} className="btn-primary inline-flex items-center gap-2">
                  <Save className="h-4 w-4" />
                  {savingProfile ? 'Saving...' : 'Save Profile'}
                </button>
              </form>
            </section>

            <section className="rounded-2xl border border-dark-700 bg-dark-800 p-6">
              <div className="mb-6 flex items-center gap-3">
                <div className="rounded-xl bg-warning-500/10 p-2 text-warning-400">
                  <KeyRound className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-dark-100">Security</h2>
                  <p className="text-sm text-dark-400">Keep your account safe with a fresh password.</p>
                </div>
              </div>

              <form onSubmit={submitPassword} className="space-y-4">
                {passwordMessage && (
                  <div className={`rounded-xl border px-4 py-3 text-sm ${
                    passwordMessage.toLowerCase().includes('success')
                      ? 'border-success-500/30 bg-success-500/10 text-success-300'
                      : 'border-red-500/30 bg-red-500/10 text-red-300'
                  }`}>
                    {passwordMessage}
                  </div>
                )}

                <div>
                  <label className="mb-2 block text-sm font-medium text-dark-300">Current Password</label>
                  <input
                    name="currentPassword"
                    type="password"
                    value={passwordForm.currentPassword}
                    onChange={handlePasswordChange}
                    className="input-field"
                    required
                  />
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="mb-2 block text-sm font-medium text-dark-300">New Password</label>
                    <input
                      name="newPassword"
                      type="password"
                      value={passwordForm.newPassword}
                      onChange={handlePasswordChange}
                      className="input-field"
                      required
                    />
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium text-dark-300">Confirm New Password</label>
                    <input
                      name="confirmPassword"
                      type="password"
                      value={passwordForm.confirmPassword}
                      onChange={handlePasswordChange}
                      className="input-field"
                      required
                    />
                  </div>
                </div>

                <button type="submit" disabled={savingPassword} className="btn-primary inline-flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4" />
                  {savingPassword ? 'Updating...' : 'Update Password'}
                </button>
              </form>
            </section>

            <section className="rounded-2xl border border-dark-700 bg-dark-800 p-6">
              <div className="mb-6 flex items-center gap-3">
                <div className="rounded-xl bg-success-500/10 p-2 text-success-400">
                  <Sparkles className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-dark-100">Trading Style</h2>
                  <p className="text-sm text-dark-400">Choose how aggressive the interface should feel while you trade.</p>
                </div>
              </div>

              <div className="grid gap-3 md:grid-cols-3">
                {[
                  ['conservative', 'Conservative', 'Lower-noise setup with fewer interruptions.'],
                  ['balanced', 'Balanced', 'Steady defaults for most simulated traders.'],
                  ['aggressive', 'Aggressive', 'High-alert style for active market monitoring.'],
                ].map(([value, label, helper]) => (
                  <button
                    key={value}
                    onClick={() => setRiskMode(value)}
                    className={`rounded-2xl border px-4 py-4 text-left transition ${
                      riskMode === value
                        ? 'border-primary-500 bg-primary-500/10 shadow-[0_0_0_1px_rgba(59,130,246,0.16)]'
                        : 'border-dark-700 bg-dark-900 hover:border-dark-600'
                    }`}
                  >
                    <p className="font-semibold text-dark-100">{label}</p>
                    <p className="mt-2 text-sm text-dark-400">{helper}</p>
                  </button>
                ))}
              </div>
            </section>
          </div>

          <div className="space-y-6">
            <section className="rounded-2xl border border-dark-700 bg-dark-800 p-6">
              <div className="mb-5 flex items-center gap-3">
                <div className="rounded-xl bg-success-500/10 p-2 text-success-400">
                  <SlidersHorizontal className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-dark-100">Trading Preferences</h2>
                  <p className="text-sm text-dark-400">Local controls for how the platform feels in your browser.</p>
                </div>
              </div>

              <div className="space-y-3">
                {[
                  ['emailAlerts', 'Email Alerts', 'Receive account and trading notifications in-app.'],
                  ['pricePopups', 'Price Popups', 'Show live market change prompts while you trade.'],
                  ['soundEffects', 'Sound Effects', 'Enable quick execution sounds on ticket actions.'],
                  ['darkTerminal', 'Dark Terminal Mode', 'Keep the trading workspace optimized for low-light sessions.'],
                  ['weeklyDigest', 'Weekly Digest', 'Show a recurring summary of your simulator performance.'],
                ].map(([key, label, helper]) => (
                  <button
                    key={key}
                    onClick={() => togglePreference(key)}
                    className="flex w-full items-center justify-between rounded-xl border border-dark-700 bg-dark-900 px-4 py-4 text-left"
                  >
                    <div>
                      <p className="font-medium text-dark-100">{label}</p>
                      <p className="mt-1 text-sm text-dark-400">{helper}</p>
                    </div>
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      preferences[key] ? 'bg-success-500/10 text-success-400' : 'bg-dark-700 text-dark-400'
                    }`}>
                      {preferences[key] ? 'On' : 'Off'}
                    </span>
                  </button>
                ))}
              </div>
            </section>

            <section className="rounded-2xl border border-dark-700 bg-dark-800 p-6">
              <div className="mb-5 flex items-center gap-3">
                <div className="rounded-xl bg-primary-500/10 p-2 text-primary-400">
                  <Bell className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-dark-100">Account Snapshot</h2>
                  <p className="text-sm text-dark-400">A quick look at your current trading standing.</p>
                </div>
              </div>

              <div className="space-y-4">
                <div className="rounded-xl border border-dark-700 bg-dark-900 px-4 py-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Trading Level</p>
                  <p className="mt-2 text-lg font-semibold text-warning-400">{stats.level}</p>
                </div>
                <div className="rounded-xl border border-dark-700 bg-dark-900 px-4 py-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Win Rate</p>
                  <p className="mt-2 text-lg font-semibold text-success-400">{stats.winRate.toFixed(1)}%</p>
                </div>
                <div className="rounded-xl border border-dark-700 bg-dark-900 px-4 py-4">
                  <p className="text-xs uppercase tracking-[0.16em] text-dark-500">Total P&L</p>
                  <p className={`mt-2 text-lg font-semibold ${stats.totalPNL >= 0 ? 'text-success-400' : 'text-red-400'}`}>
                    {formatCurrency(stats.totalPNL, 0)}
                  </p>
                </div>
                <div className="rounded-xl border border-dark-700 bg-dark-900 px-4 py-4">
                  <div className="flex items-center gap-2 text-dark-400">
                    <Mail className="h-4 w-4" />
                    <span className="text-sm">Primary Contact</span>
                  </div>
                  <p className="mt-2 text-sm font-medium text-dark-100">{user?.email}</p>
                </div>
              </div>
            </section>

            <section className="rounded-2xl border border-dark-700 bg-dark-800 p-6">
              <div className="mb-5 flex items-center gap-3">
                <div className="rounded-xl bg-warning-500/10 p-2 text-warning-400">
                  <MonitorSmartphone className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-dark-100">Access & Support</h2>
                  <p className="text-sm text-dark-400">Helpful account actions and recovery shortcuts.</p>
                </div>
              </div>

              <div className="space-y-3">
                {[
                  [ShieldCheck, 'Review Security Activity', 'Check recent account actions and login health.'],
                  [Info, 'Get Help With Deposits', 'Review payment steps for M-Pesa, card, or bank funding.'],
                  [MoonStar, 'Workspace Display Tips', 'Tune the simulator layout for desktop and mobile trading.'],
                ].map(([Icon, label, helper]) => (
                  <div key={label} className="flex items-center justify-between rounded-xl border border-dark-700 bg-dark-900 px-4 py-4">
                    <div className="flex items-start gap-3">
                      <div className="rounded-lg bg-dark-800 p-2 text-dark-300">
                        <Icon className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="font-medium text-dark-100">{label}</p>
                        <p className="mt-1 text-sm text-dark-400">{helper}</p>
                      </div>
                    </div>
                    <ChevronRight className="h-4 w-4 text-dark-500" />
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-2xl border border-red-500/20 bg-red-500/5 p-6">
              <div className="mb-4 flex items-center gap-3">
                <div className="rounded-xl bg-red-500/10 p-2 text-red-400">
                  <ShieldAlert className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-dark-100">Danger Zone</h2>
                  <p className="text-sm text-dark-400">High-impact actions should stay deliberate and easy to understand.</p>
                </div>
              </div>

              <div className="rounded-xl border border-red-500/20 bg-dark-900/70 px-4 py-4">
                <p className="font-medium text-dark-100">Account Deletion</p>
                <p className="mt-2 text-sm leading-6 text-dark-400">
                  This flow is intentionally disabled until a full account export and confirmation step is implemented. That protects users from accidental destructive actions.
                </p>
                <button className="mt-4 rounded-xl border border-red-500/30 px-4 py-3 text-sm font-semibold text-red-300 opacity-70">
                  Delete Account Coming Soon
                </button>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  )
}
