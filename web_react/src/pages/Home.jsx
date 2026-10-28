import React from 'react'
import { Link } from 'react-router-dom'
import { TrendingUp, Zap, Shield, Users, GraduationCap, Trophy, Rocket } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export const Home = () => {
  const { isAuthenticated } = useAuth()

  return (
    <div className="min-h-screen bg-dark-950 pt-8 pb-12">
      {/* Hero */}
      <div className="max-w-7xl mx-auto px-4 mb-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-display font-bold text-dark-100 mb-4">
            Master Forex Trading
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-green-400">
              {' '}the Smart Way
            </span>
          </h1>
          <p className="text-base sm:text-lg md:text-xl text-dark-400 mb-8 max-w-2xl mx-auto">
            Learn, practice, and compete in simulated forex trading. Perfect for Kenyan university students 
            to develop real trading skills without risking real money.
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-4">
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" className="btn-primary text-lg px-8 py-3">
                  🎯 Go to Dashboard
                </Link>
                <Link to="/trade" className="btn-secondary text-lg px-8 py-3">
                  📈 Start Trading
                </Link>
              </>
            ) : (
              <>
                <Link to="/register" className="btn-primary text-lg px-8 py-3">
                  🚀 Get Started Free
                </Link>
                <Link to="/login" className="btn-secondary text-lg px-8 py-3">
                  Sign In
                </Link>
              </>
            )}
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          <div className="card">
            <Zap className="w-8 h-8 text-primary-400 mb-4" />
            <h3 className="text-lg font-bold text-dark-100 mb-2">Live Trading</h3>
            <p className="text-dark-400 text-sm">
              Execute trades with simulated market prices updated in real-time
            </p>
          </div>

          <div className="card">
            <Shield className="w-8 h-8 text-success-400 mb-4" />
            <h3 className="text-lg font-bold text-dark-100 mb-2">Zero Risk</h3>
            <p className="text-dark-400 text-sm">
              Learn trading without risking real money. Safe for students
            </p>
          </div>

          <div className="card">
            <TrendingUp className="w-8 h-8 text-warning-400 mb-4" />
            <h3 className="text-lg font-bold text-dark-100 mb-2">Real Analytics</h3>
            <p className="text-dark-400 text-sm">
              Track your P&L, win rate, and trading performance metrics
            </p>
          </div>

          <div className="card">
            <Users className="w-8 h-8 text-primary-400 mb-4" />
            <h3 className="text-lg font-bold text-dark-100 mb-2">Community</h3>
            <p className="text-dark-400 text-sm">
              Compete with classmates and learn from other traders
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="card mb-16">
          <h2 className="text-3xl font-display font-bold text-dark-100 mb-8 text-center">
            How It Works
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              { num: '1', title: 'Register', desc: 'Create your account in minutes' },
              { num: '2', title: 'Learn', desc: 'Study our trading guides & tutorials' },
              { num: '3', title: 'Trade', desc: 'Execute simulated forex trades' },
              { num: '4', title: 'Track', desc: 'Monitor your P&L and performance' },
            ].map((step) => (
              <div key={step.num} className="text-center">
                <div className="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center text-xl font-bold text-white mx-auto mb-4">
                  {step.num}
                </div>
                <h4 className="font-bold text-dark-100 mb-2">{step.title}</h4>
                <p className="text-sm text-dark-400">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="mb-16">
          <div className="mb-8 text-center">
            <h2 className="text-3xl font-display font-bold text-dark-100">Built for Learning and Career Growth</h2>
            <p className="mt-3 text-dark-400 max-w-3xl mx-auto">
              Use the system for coursework, student clubs, self-learning, hackathons, portfolio projects, and financial-literacy programs.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            {[
              {
                icon: GraduationCap,
                title: 'University Course',
                text: 'Support finance, economics, and computer science learning with practical simulated trading workflows.',
              },
              {
                icon: Trophy,
                title: 'Student Trading Club',
                text: 'Run weekly competitions and peer-learning sessions with a shared trading platform.',
              },
              {
                icon: Rocket,
                title: 'Hackathons & Portfolios',
                text: 'Turn the simulator into a full-stack fintech project for demos, internships, and showcases.',
              },
            ].map((item) => {
              const Icon = item.icon
              return (
                <div key={item.title} className="card">
                  <Icon className="w-8 h-8 text-primary-400 mb-4" />
                  <h3 className="text-lg font-bold text-dark-100 mb-2">{item.title}</h3>
                  <p className="text-dark-400 text-sm">{item.text}</p>
                </div>
              )
            })}
          </div>

          <div className="mt-8 text-center">
            <Link to="/learning" className="btn-secondary text-lg px-8 py-3 inline-block">
              Explore Learning Hub
            </Link>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-16">
          <div className="card text-center">
            <p className="text-4xl font-display font-bold text-primary-400 mb-2">500+</p>
            <p className="text-dark-400">Active Traders</p>
          </div>
          <div className="card text-center">
            <p className="text-4xl font-display font-bold text-success-400 mb-2">10K+</p>
            <p className="text-dark-400">Trades Executed</p>
          </div>
          <div className="card text-center">
            <p className="text-4xl font-display font-bold text-warning-400 mb-2">8 Pairs</p>
            <p className="text-dark-400">Available to Trade</p>
          </div>
        </div>

        {/* CTA */}
        <div className="card bg-gradient-to-r from-primary-900/30 to-green-900/30 border-primary-500/50 text-center">
          <h3 className="text-2xl font-bold text-dark-100 mb-4">Ready to Start Learning?</h3>
          <p className="text-dark-400 mb-6">Join thousands of Kenyan students mastering forex trading</p>
          {!isAuthenticated && (
            <Link to="/register" className="btn-primary text-lg px-8 py-3 inline-block">
              Create Free Account
            </Link>
          )}
        </div>
      </div>
    </div>
  )
}
