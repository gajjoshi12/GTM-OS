import { Outlet, useNavigate } from 'react-router-dom'
import { Bell, LogOut, Search, Sparkles } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { Sidebar } from './Sidebar'
import { CommandBar, useCommandBar } from './CommandBar'
import { useAuth } from '@/store/auth'
import { get } from '@/lib/api'
import { Button } from '@/components/ui'

export function AppShell() {
  const { open, setOpen } = useCommandBar()
  const logout = useAuth((s) => s.logout)
  const nav = useNavigate()
  const { data: summary } = useQuery({ queryKey: ['decisions', 'summary'], queryFn: () => get<{ pending: number; high_impact_pending: number }>('/agents/decisions/summary/'), refetchInterval: 20_000 })

  return (
    <div className="flex h-full">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-line bg-ink-950/70 px-4 backdrop-blur-xl md:px-6">
          <button onClick={() => setOpen(true)}
            className="group flex h-10 flex-1 max-w-xl items-center gap-3 rounded-xl border border-white/10 bg-white/[0.03] px-3 text-left text-sm text-[var(--text-muted)] transition hover:border-accent/40 hover:bg-white/[0.05]">
            <Search className="h-4 w-4" />
            <span className="flex-1 truncate">Ask the AI CMO anything… “Why did revenue fall this week?”</span>
            <span className="hidden items-center gap-1 md:flex"><span className="kbd">⌘</span><span className="kbd">K</span></span>
          </button>
          <div className="ml-auto flex items-center gap-2">
            <Button size="sm" variant="primary" onClick={() => setOpen(true)} className="hidden sm:inline-flex"><Sparkles className="h-3.5 w-3.5" /> Command</Button>
            <button onClick={() => nav('/')} className="relative rounded-xl border border-white/10 bg-white/[0.03] p-2.5 text-[var(--text-secondary)] hover:text-white">
              <Bell className="h-4 w-4" />
              {(summary?.pending ?? 0) > 0 && <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-accent px-1 font-mono text-[10px] font-bold text-ink-950">{summary?.pending}</span>}
            </button>
            <button onClick={() => { logout(); nav('/login') }} className="rounded-xl border border-white/10 bg-white/[0.03] p-2.5 text-[var(--text-secondary)] hover:text-white" title="Sign out">
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto px-4 py-6 md:px-8">
          <div className="mx-auto max-w-[1440px]"><Outlet /></div>
        </main>
      </div>
      <CommandBar open={open} onClose={() => setOpen(false)} />
    </div>
  )
}
