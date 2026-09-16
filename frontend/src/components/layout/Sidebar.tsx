import { NavLink } from 'react-router-dom'
import { clsx } from 'clsx'
import {
  Activity, BarChart3, Bot, FlaskConical, Home, Layout, Mail, Megaphone, PenSquare, Plug, Search, Settings, Users,
} from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { get } from '@/lib/api'
import { useAuth } from '@/store/auth'

/**
 * Navigation is grouped by what the user is trying to DO, in their words —
 * not by the product's internal vocabulary (ICP, CRO, attribution, experiments).
 */
const GROUPS: { heading: string | null; items: { to: string; label: string; hint: string; icon: typeof Home; end?: boolean }[] }[] = [
  {
    heading: null,
    items: [{ to: '/', label: 'Dashboard', hint: 'How things are going', icon: Home, end: true }],
  },
  {
    heading: 'Do the marketing',
    items: [
      { to: '/prospects', label: 'Customers', hint: 'Who to target', icon: Users },
      { to: '/outbound', label: 'Emails', hint: 'Cold outreach and replies', icon: Mail },
      { to: '/campaigns', label: 'Ads', hint: 'Paid campaigns and creative', icon: Megaphone },
      { to: '/content', label: 'Content', hint: 'Posts, articles and SEO', icon: PenSquare },
      { to: '/conversion', label: 'Web pages', hint: 'Landing pages', icon: Layout },
    ],
  },
  {
    heading: 'See what worked',
    items: [
      { to: '/analytics', label: 'Results', hint: 'Revenue and what drove it', icon: BarChart3 },
      { to: '/intelligence', label: 'Research', hint: 'Your market and competitors', icon: Search },
      { to: '/experiments', label: 'Tests', hint: 'Experiments and lessons learned', icon: FlaskConical },
    ],
  },
  {
    heading: 'Setup',
    items: [
      { to: '/agents', label: 'AI team', hint: 'The agents doing the work', icon: Bot },
      { to: '/integrations', label: 'Connections', hint: 'Connect your tools', icon: Plug },
      { to: '/settings', label: 'Settings', hint: 'Limits and brand rules', icon: Settings },
    ],
  },
]

type Health = { ai_mode: string; provider?: string; model?: string; key_env_var?: string }

export function Sidebar() {
  const user = useAuth((s) => s.user)
  const { data: health } = useQuery({ queryKey: ['health'], queryFn: () => get<Health>('/health/'), staleTime: 60_000 })
  const { data: summary } = useQuery({
    queryKey: ['decisions', 'summary'],
    queryFn: () => get<{ pending: number }>('/agents/decisions/summary/'),
    refetchInterval: 20_000,
  })
  const isLive = health?.ai_mode === 'live'

  return (
    <aside className="hidden w-[248px] shrink-0 flex-col border-r border-line bg-ink-900/60 backdrop-blur-xl lg:flex">
      <div className="flex h-16 items-center gap-3 px-5">
        <div className="relative">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-accent to-accent-cyan shadow-glow" />
          <div className="absolute inset-0 m-auto h-3 w-3 rounded-full bg-ink-950" />
        </div>
        <div>
          <div className="text-sm font-bold tracking-tight text-white">AI GTM OS</div>
          <div className="text-[10px] uppercase tracking-[0.18em] text-[var(--text-muted)]">Revenue OS</div>
        </div>
      </div>

      <nav className="mt-1 flex-1 overflow-y-auto px-3 pb-2">
        {GROUPS.map((group) => (
          <div key={group.heading ?? 'top'} className="mb-1">
            {group.heading && (
              <div className="px-3 pb-1 pt-4 text-[10px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">
                {group.heading}
              </div>
            )}
            {group.items.map(({ to, label, hint, icon: Icon, end }) => (
              <NavLink key={to} to={to} end={end} title={hint}
                className={({ isActive }) => clsx(
                  'group relative flex items-center gap-3 rounded-xl px-3 py-2 transition',
                  isActive ? 'bg-white/[0.07]' : 'hover:bg-white/[0.04]')}>
                {({ isActive }) => (
                  <>
                    {isActive && <span className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-r-full bg-gradient-to-b from-accent to-accent-cyan" />}
                    <Icon className={clsx('h-4 w-4 shrink-0', isActive ? 'text-accent-soft' : 'text-[var(--text-muted)] group-hover:text-white')} />
                    <span className="min-w-0 flex-1">
                      <span className={clsx('block truncate text-[13px] font-medium', isActive ? 'text-white' : 'text-[var(--text-secondary)] group-hover:text-white')}>
                        {label}
                      </span>
                      <span className="block truncate text-[10.5px] leading-tight text-[var(--text-muted)]">{hint}</span>
                    </span>
                    {to === '/' && (summary?.pending ?? 0) > 0 && (
                      <span className="rounded-full bg-accent/20 px-1.5 py-0.5 font-mono text-[10px] text-accent-soft">{summary?.pending}</span>
                    )}
                  </>
                )}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="m-3 rounded-2xl border border-white/10 bg-white/[0.03] p-3">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className={clsx('absolute inline-flex h-full w-full rounded-full opacity-70 animate-pulseRing', isLive ? 'bg-emerald-400' : 'bg-violet-400')} />
            <span className={clsx('relative inline-flex h-2.5 w-2.5 rounded-full', isLive ? 'bg-emerald-400' : 'bg-violet-400')} />
          </span>
          <span className="text-xs font-semibold text-white">{isLive ? 'AI is live' : 'Demo data'}</span>
          <Activity className="ml-auto h-3.5 w-3.5 text-[var(--text-muted)]" />
        </div>
        <p className="mt-1.5 text-[11px] leading-relaxed text-[var(--text-muted)]">
          {isLive
            ? <>Agents are thinking with <span className="text-[var(--text-secondary)]">{health?.model}</span> on {health?.provider}.</>
            : <>Everything you see is realistic sample data. Add <span className="font-mono text-[10px] text-[var(--text-secondary)]">{health?.key_env_var ?? 'GROQ_API_KEY'}</span> to go live.</>}
        </p>
      </div>

      <div className="flex items-center gap-3 border-t border-line px-5 py-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-accent/60 to-accent-cyan/60 text-xs font-bold text-white">
          {(user?.full_name || user?.email || 'U').slice(0, 1).toUpperCase()}
        </div>
        <div className="min-w-0">
          <div className="truncate text-xs font-semibold text-white">{user?.full_name || user?.email}</div>
          <div className="truncate text-[11px] text-[var(--text-muted)]">{user?.current_workspace?.name}</div>
        </div>
      </div>
    </aside>
  )
}
