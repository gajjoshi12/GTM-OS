import { motion } from 'framer-motion'
import { clsx } from 'clsx'
import { PixelAvatar, type AvatarState } from './PixelAvatar'
import { Badge, statusTone, useSpot } from '@/components/ui'
import { relTime } from '@/lib/format'

export type TeamAgent = {
  id: number; key: string; name: string; group: string; group_label?: string
  description?: string; status: string; last_summary: string; health_score: number
  last_run_at?: string | null; pending_decisions?: number
}

export const avatarState = (status: string, busy: boolean): AvatarState =>
  busy || status === 'running' ? 'working' : status === 'error' ? 'error' : status === 'paused' ? 'paused' : 'idle'

/** Three dots that march while an agent is thinking. */
function Typing() {
  return (
    <span className="inline-flex items-center gap-[3px]" aria-label="working">
      {[0, 1, 2].map((i) => (
        <motion.span key={i} className="h-1 w-1 rounded-full bg-cyan-300"
          animate={{ opacity: [0.25, 1, 0.25], y: [0, -2, 0] }}
          transition={{ duration: 0.9, repeat: Infinity, delay: i * 0.15 }} />
      ))}
    </span>
  )
}

function Desk({ a, busy, onSelect }: { a: TeamAgent; busy: boolean; onSelect?: (a: TeamAgent) => void }) {
  const state = avatarState(a.status, busy)
  const working = state === 'working'
  const spot = useSpot<HTMLButtonElement>()

  return (
    <motion.button ref={spot.ref} onMouseMove={spot.onMouseMove} onClick={() => onSelect?.(a)}
      layout initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} whileHover={{ y: -3 }}
      title={a.description}
      className={clsx('glass spot group relative flex flex-col items-center gap-2 p-3 text-center', working && 'ring-1 ring-cyan-400/40')}>

      {/* status corner */}
      <span className="absolute right-2 top-2 flex items-center gap-1">
        {(a.pending_decisions ?? 0) > 0 && (
          <span className="rounded-full bg-accent/25 px-1.5 font-mono text-[9px] font-bold text-accent-soft">{a.pending_decisions}</span>
        )}
        <span className={clsx('h-1.5 w-1.5 rounded-full',
          working ? 'bg-cyan-400' : a.status === 'error' ? 'bg-rose-400' : a.status === 'paused' ? 'bg-amber-400' : 'bg-emerald-400/70')} />
      </span>

      {/* the little person, sitting on a desk shadow */}
      <div className={clsx('relative rounded-2xl px-2 pt-1 transition',
        working ? 'bg-cyan-400/[0.07]' : 'bg-white/[0.02] group-hover:bg-white/[0.04]')}>
        <PixelAvatar seed={a.key} state={state} size={72} desk />
      </div>

      <div className="min-w-0 w-full">
        <div className="truncate text-[12px] font-bold leading-tight text-white">{a.name.replace(/ Agent$/, '')}</div>
        <div className="mt-1 flex items-center justify-center gap-1.5">
          {working ? <Typing /> : <span className="text-[10px] text-[var(--text-muted)]">{a.last_run_at ? relTime(a.last_run_at) : 'not run yet'}</span>}
        </div>
      </div>

      {/* what it last did — revealed on hover so the grid stays calm */}
      <div className="pointer-events-none absolute inset-x-0 bottom-0 translate-y-1 rounded-b-2xl bg-ink-950/95 p-2.5 text-left text-[10.5px] leading-snug text-[var(--text-secondary)] opacity-0 backdrop-blur transition group-hover:translate-y-0 group-hover:opacity-100">
        {a.last_summary || 'Has not run yet.'}
      </div>
    </motion.button>
  )
}

export function TeamRoom({ groups, cmo, busy, onSelect }: {
  groups: { key: string; label: string; agents: TeamAgent[] }[]
  cmo?: TeamAgent | null
  busy: Set<number>
  onSelect?: (a: TeamAgent) => void
}) {
  const all = groups.flatMap((g) => g.agents)
  const working = all.filter((a) => avatarState(a.status, busy.has(a.id)) === 'working').length

  return (
    <div className="space-y-5">
      {/* the manager, front and centre */}
      {cmo && (
        <motion.button onClick={() => onSelect?.(cmo)} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
          className="glass-hero flex w-full flex-wrap items-center gap-5 p-5 text-left ring-1 ring-accent/25 transition hover:ring-accent/50">
          <PixelAvatar seed={cmo.key} state={avatarState(cmo.status, busy.has(cmo.id))} size={104} desk />
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="text-lg font-bold text-white">{cmo.name}</h3>
              <Badge tone="accent">the manager</Badge>
              <Badge tone={statusTone(cmo.status)} dot>{cmo.status === 'running' ? 'working' : cmo.status}</Badge>
            </div>
            <p className="mt-1 max-w-2xl text-[13px] leading-relaxed text-[var(--text-secondary)]">{cmo.last_summary || cmo.description}</p>
          </div>
          <div className="text-right">
            <div className="display-num text-3xl text-white">{working}</div>
            <div className="text-[10px] uppercase tracking-wider text-[var(--text-muted)]">working now</div>
          </div>
        </motion.button>
      )}

      {groups.map((g) => (
        <div key={g.key}>
          <div className="mb-2 flex items-baseline gap-2">
            <h4 className="text-[13px] font-bold text-white">{g.label}</h4>
            <span className="text-[11px] text-[var(--text-muted)]">{g.agents.length} {g.agents.length === 1 ? 'person' : 'people'}</span>
          </div>
          <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-6">
            {g.agents.map((a) => <Desk key={a.id} a={a} busy={busy.has(a.id)} onSelect={onSelect} />)}
          </div>
        </div>
      ))}
    </div>
  )
}
