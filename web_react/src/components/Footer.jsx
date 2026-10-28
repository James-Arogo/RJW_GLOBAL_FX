import React from 'react'
import { Link } from 'react-router-dom'
import { GraduationCap, Landmark, ShieldAlert, TrendingUp } from 'lucide-react'

export const Footer = () => {
  return (
    <footer className="border-t border-dark-800 bg-[#05070d]">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-5">
        <div className="grid gap-8 lg:grid-cols-[minmax(0,1.3fr)_repeat(3,minmax(0,1fr))]">
          <div>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-6 w-6 text-primary-500" />
              <span className="text-lg font-display font-bold text-primary-400">RJW FX</span>
            </div>
            <p className="mt-4 max-w-md text-sm leading-6 text-dark-400">
              A student-friendly trading simulator built for learning, practice, competitions, and financial literacy with a KES-first experience.
            </p>
            <div className="mt-5 inline-flex items-center gap-2 rounded-full border border-warning-500/20 bg-warning-500/10 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] text-warning-300">
              <ShieldAlert className="h-3.5 w-3.5" />
              Simulated Trading Only
            </div>
          </div>

          <div>
            <h2 className="text-sm font-semibold uppercase tracking-[0.16em] text-dark-200">Platform</h2>
            <div className="mt-4 space-y-3 text-sm text-dark-400">
              <Link to="/" className="block transition hover:text-primary-300">Home</Link>
              <Link to="/market" className="block transition hover:text-primary-300">Market</Link>
              <Link to="/trade" className="block transition hover:text-primary-300">Trade</Link>
              <Link to="/deposit" className="block transition hover:text-primary-300">Wallet</Link>
              <Link to="/profile" className="block transition hover:text-primary-300">Account</Link>
            </div>
          </div>

          <div>
            <h2 className="text-sm font-semibold uppercase tracking-[0.16em] text-dark-200">Learning</h2>
            <div className="mt-4 space-y-3 text-sm text-dark-400">
              <Link to="/learning" className="flex items-center gap-2 transition hover:text-primary-300">
                <GraduationCap className="h-4 w-4" />
                Learning Hub
              </Link>
              <p>University courses</p>
              <p>Student trading clubs</p>
              <p>Hackathons and portfolios</p>
              <p>Financial literacy</p>
            </div>
          </div>

          <div>
            <h2 className="text-sm font-semibold uppercase tracking-[0.16em] text-dark-200">Funding</h2>
            <div className="mt-4 space-y-3 text-sm text-dark-400">
              <p className="flex items-center gap-2">
                <Landmark className="h-4 w-4" />
                M-Pesa deposits and withdrawals
              </p>
              <p>Bank transfer support</p>
              <p>Card funding simulation</p>
              <p>Student-friendly KSh 50 entry level</p>
            </div>
          </div>
        </div>

        <div className="mt-8 flex flex-col gap-3 border-t border-dark-800 pt-6 text-sm text-dark-500 md:flex-row md:items-center md:justify-between">
          <p>© 2026 RJW FX. Built for education, training, and simulated trading practice.</p>
          <p>This platform does not connect users to live financial markets or guarantee real-world profits.</p>
        </div>
      </div>
    </footer>
  )
}
