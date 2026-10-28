import React, { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { TrendingUp, LogOut, Menu, User, Wallet, X } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    setMenuOpen(false)
  }, [location.pathname])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const authenticatedLinks = [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/market', label: 'Market' },
    { to: '/trade', label: 'Trade' },
    { to: '/deposit', label: 'Wallet' },
    { to: '/learning', label: 'Learning Hub' },
  ]

  const guestLinks = [{ to: '/learning', label: 'Learning Hub' }]

  return (
    <nav className="bg-dark-800 border-b border-dark-700 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 py-3 sm:py-4 flex items-center justify-between gap-4">
        <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <TrendingUp className="w-6 h-6 sm:w-7 sm:h-7 text-primary-500" />
          <span className="text-lg sm:text-xl font-display font-bold text-primary-400">RJW FX</span>
        </Link>

        <button
          type="button"
          onClick={() => setMenuOpen((previous) => !previous)}
          className="inline-flex items-center justify-center rounded-lg border border-dark-700 bg-dark-900 p-2 text-dark-200 transition hover:border-dark-600 hover:bg-dark-700 md:hidden"
          aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
        >
          {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>

        <div className="hidden md:flex items-center gap-4">
          {isAuthenticated ? (
            <>
              {authenticatedLinks.map((link) => (
                <Link key={link.to} to={link.to} className="text-dark-300 hover:text-primary-400 transition-colors text-sm font-medium">
                  {link.label}
                </Link>
              ))}

              <div className="flex items-center gap-3 pl-4 border-l border-dark-700">
                <Link to="/profile" className="flex items-center gap-2 text-dark-300 hover:text-primary-400 transition-colors">
                  <User className="w-4 h-4" />
                  <span className="text-sm hidden sm:inline">{user?.username}</span>
                </Link>
                <button
                  onClick={handleLogout}
                  className="text-dark-400 hover:text-red-400 transition-colors p-2"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </>
          ) : (
            <div className="flex items-center gap-3">
              {guestLinks.map((link) => (
                <Link key={link.to} to={link.to} className="text-dark-300 hover:text-primary-400 transition-colors text-sm font-medium">
                  {link.label}
                </Link>
              ))}
              <Link to="/login" className="btn-secondary text-sm">
                Login
              </Link>
              <Link to="/register" className="btn-primary text-sm">
                Register
              </Link>
            </div>
          )}
        </div>
      </div>

      {menuOpen && (
        <div className="border-t border-dark-700 bg-dark-900/95 px-4 py-4 md:hidden">
          {isAuthenticated ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between rounded-xl border border-dark-700 bg-dark-800 px-4 py-3">
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold text-dark-100">{user?.username}</p>
                  <p className="truncate text-xs text-dark-400">{user?.email}</p>
                </div>
                <div className="ml-4 flex items-center gap-2 rounded-full bg-dark-950 px-3 py-1 text-xs font-semibold text-primary-300">
                  <Wallet className="h-3.5 w-3.5" />
                  Wallet
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                {authenticatedLinks.map((link) => (
                  <Link
                    key={link.to}
                    to={link.to}
                    className="rounded-xl border border-dark-700 bg-dark-800 px-4 py-3 text-sm font-medium text-dark-200 transition hover:border-dark-600 hover:text-primary-300"
                  >
                    {link.label}
                  </Link>
                ))}
                <Link
                  to="/profile"
                  className="rounded-xl border border-dark-700 bg-dark-800 px-4 py-3 text-sm font-medium text-dark-200 transition hover:border-dark-600 hover:text-primary-300"
                >
                  Profile
                </Link>
                <button
                  onClick={handleLogout}
                  className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-left text-sm font-medium text-red-300 transition hover:bg-red-500/20"
                >
                  Logout
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {guestLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className="block rounded-xl border border-dark-700 bg-dark-800 px-4 py-3 text-sm font-medium text-dark-200 transition hover:border-dark-600 hover:text-primary-300"
                >
                  {link.label}
                </Link>
              ))}
              <div className="grid grid-cols-2 gap-2">
                <Link to="/login" className="btn-secondary text-center text-sm">
                  Login
                </Link>
                <Link to="/register" className="btn-primary text-center text-sm">
                  Register
                </Link>
              </div>
            </div>
          )}
        </div>
      )}
    </nav>
  )
}
