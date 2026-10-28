import React from 'react'
import { Link } from 'react-router-dom'
import {
  BookOpen,
  Briefcase,
  Code2,
  GraduationCap,
  Lightbulb,
  Rocket,
  Trophy,
  WalletCards,
} from 'lucide-react'

const tracks = [
  {
    title: 'University Course',
    subtitle: 'Finance, Economics, Computer Science',
    icon: GraduationCap,
    accent: 'text-primary-300 border-primary-500/30 bg-primary-500/10',
    points: [
      'Use trading simulation examples in finance, economics, and CS coursework.',
      'Follow structured modules on risk, data analysis, and market systems.',
      'Turn market activity into class-friendly case studies and reports.',
    ],
  },
  {
    title: 'Student Trading Club',
    subtitle: 'Weekly competitions',
    icon: Trophy,
    accent: 'text-warning-300 border-warning-500/30 bg-warning-500/10',
    points: [
      'Host weekly leaderboard challenges around simulated performance.',
      'Create pair-of-the-week competitions for club members.',
      'Use the dashboard and market screen during live club sessions.',
    ],
  },
  {
    title: 'Self-Learning',
    subtitle: 'Follow 4-week plan',
    icon: BookOpen,
    accent: 'text-success-300 border-success-500/30 bg-success-500/10',
    points: [
      'Week 1: market basics, terminology, and account setup.',
      'Week 2: chart reading, order flow, and risk control.',
      'Week 3: strategy testing with journal-style review.',
      'Week 4: simulated execution, performance review, and reflection.',
    ],
  },
  {
    title: 'Hackathons',
    subtitle: 'Full-stack project template',
    icon: Rocket,
    accent: 'text-fuchsia-300 border-fuchsia-500/30 bg-fuchsia-500/10',
    points: [
      'Use this platform as a base for fintech and trading hackathon demos.',
      'Show live market streaming, wallet funding, and analytics in one project.',
      'Extend the simulator with alerts, AI insights, or social competition features.',
    ],
  },
  {
    title: 'Portfolio Projects',
    subtitle: 'Demonstrate full-stack skills',
    icon: Briefcase,
    accent: 'text-sky-300 border-sky-500/30 bg-sky-500/10',
    points: [
      'Showcase React UI, FastAPI services, auth, payments, and real-time streaming.',
      'Document architecture, API design, and simulation logic for recruiters.',
      'Use the market, dashboard, and profile features as portfolio proof points.',
    ],
  },
  {
    title: 'Financial Literacy',
    subtitle: 'Teach trading basics',
    icon: WalletCards,
    accent: 'text-emerald-300 border-emerald-500/30 bg-emerald-500/10',
    points: [
      'Explain leverage, P&L, balance, equity, and margin using the simulator.',
      'Teach safe practice habits before students ever see real-money platforms.',
      'Use deposits and profile settings to discuss digital finance workflows.',
    ],
  },
]

const weeklyPlan = [
  {
    week: 'Week 1',
    title: 'Foundations',
    description: 'Create an account, fund the simulator wallet, and learn the meaning of pairs, spread, and leverage.',
  },
  {
    week: 'Week 2',
    title: 'Market Reading',
    description: 'Use the live market page to study candles, recent trades, and order-book style movement.',
  },
  {
    week: 'Week 3',
    title: 'Execution',
    description: 'Place controlled long and short trades, then review unrealized and realized P&L.',
  },
  {
    week: 'Week 4',
    title: 'Build & Present',
    description: 'Turn what you learned into a club presentation, course assignment, or portfolio case study.',
  },
]

export const LearningHub = () => {
  return (
    <div className="min-h-screen bg-dark-950 pt-8 pb-12">
      <div className="mx-auto max-w-7xl px-4">
        <section className="mb-10 overflow-hidden rounded-[28px] border border-dark-700 bg-[radial-gradient(circle_at_top_left,rgba(34,197,94,0.15),transparent_30%),radial-gradient(circle_at_top_right,rgba(59,130,246,0.15),transparent_26%),linear-gradient(145deg,#101726_0%,#0b1120_55%,#090d17_100%)] p-8">
          <div className="max-w-3xl">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-dark-300">
              <Lightbulb className="h-4 w-4 text-warning-300" />
              Growth Paths
            </div>
            <h1 className="text-4xl font-display font-bold text-white md:text-5xl">
              Learn Trading, Build Projects, and Grow Through the Platform
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-dark-300">
              This system can support coursework, club competitions, self-learning, hackathons, portfolio building, and financial-literacy programs. The hub below turns those goals into visible paths inside the product.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/market" className="btn-primary inline-flex items-center gap-2">
                <Code2 className="h-4 w-4" />
                Open Live Market
              </Link>
              <Link to="/dashboard" className="btn-secondary inline-flex items-center gap-2">
                <BookOpen className="h-4 w-4" />
                View Dashboard
              </Link>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <div className="mb-5">
            <h2 className="text-2xl font-semibold text-dark-100">Programs Inside the System</h2>
            <p className="mt-2 text-dark-400">Each path below shows how the simulator can be used beyond simple trade entry.</p>
          </div>

          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {tracks.map((track) => {
              const Icon = track.icon
              return (
                <article key={track.title} className="rounded-2xl border border-dark-700 bg-dark-800 p-6">
                  <div className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] ${track.accent}`}>
                    <Icon className="h-4 w-4" />
                    {track.title}
                  </div>
                  <h3 className="mt-4 text-xl font-semibold text-dark-100">{track.subtitle}</h3>
                  <div className="mt-4 space-y-3">
                    {track.points.map((point) => (
                      <div key={point} className="rounded-xl border border-dark-700 bg-dark-900 px-4 py-3 text-sm leading-6 text-dark-300">
                        {point}
                      </div>
                    ))}
                  </div>
                </article>
              )
            })}
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.3fr_0.9fr]">
          <div className="rounded-2xl border border-dark-700 bg-dark-800 p-6">
            <h2 className="text-2xl font-semibold text-dark-100">4-Week Self-Learning Plan</h2>
            <p className="mt-2 text-dark-400">A built-in path students can follow on their own using the current app screens.</p>

            <div className="mt-6 grid gap-4 md:grid-cols-2">
              {weeklyPlan.map((item) => (
                <div key={item.week} className="rounded-2xl border border-dark-700 bg-dark-900 p-5">
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-primary-300">{item.week}</p>
                  <h3 className="mt-2 text-lg font-semibold text-dark-100">{item.title}</h3>
                  <p className="mt-3 text-sm leading-6 text-dark-400">{item.description}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-6">
            <section className="rounded-2xl border border-dark-700 bg-dark-800 p-6">
              <h2 className="text-xl font-semibold text-dark-100">Suggested In-App Flow</h2>
              <div className="mt-4 space-y-3">
                {[
                  'Register and update your account settings.',
                  'Deposit simulated funds through the wallet page.',
                  'Study candles and live pricing on the market page.',
                  'Place controlled trades with leverage and live P&L.',
                  'Review performance and learning progress on the dashboard.',
                ].map((step, index) => (
                  <div key={step} className="flex items-start gap-3 rounded-xl border border-dark-700 bg-dark-900 px-4 py-3">
                    <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary-600 text-xs font-bold text-white">
                      {index + 1}
                    </div>
                    <p className="text-sm leading-6 text-dark-300">{step}</p>
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-2xl border border-dark-700 bg-dark-800 p-6">
              <h2 className="text-xl font-semibold text-dark-100">Best Use Cases</h2>
              <div className="mt-4 space-y-3">
                {[
                  'Course labs for finance, economics, and computer science students.',
                  'Weekly trading-club competitions and leaderboard sessions.',
                  'Hackathon demos with real-time full-stack features.',
                  'Portfolio storytelling for internships and graduate roles.',
                  'Financial-literacy workshops for beginners.',
                ].map((item) => (
                  <div key={item} className="rounded-xl border border-dark-700 bg-dark-900 px-4 py-3 text-sm leading-6 text-dark-300">
                    {item}
                  </div>
                ))}
              </div>
            </section>
          </div>
        </section>
      </div>
    </div>
  )
}
