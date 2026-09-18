import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { Bot } from 'lucide-react'
import { Badge, statusTone } from '@/components/ui'
import { relTime } from '@/lib/format'

/**
 * The AI team as a living constellation. The manager (CMO) sits at the core;
 * every specialist orbits on a ring by its department. Working agents pulse.
 * Hover any node to see who it is and what it last did.
 */
export type OrbitAgent = {
  id: number; key: string; name: string; group: string; group_label?: string
  status: string; last_summary: string; health_score: number; last_run_at?: string | null; pending_decisions?: number
}

// Fixed slot per department so colours never change between visits.
const GROUP_COLOR: Record<string, string> = {
  intelligence: 'var(--series-1)', targeting: 'var(--series-3)', prospecting: 'var(--series-4)',
  outbound: 'var(--series-2)', lifecycle: 'var(--series-5)', content: 'var(--series-6)', creative: 'var(--series-7)',
  paid: 'var(--series-2)', conversion: 'var(--series-3)', revenue: 'var(--series-1)', optimization: 'var(--series-6)', governance: 'var(--series-4)',
}
const RINGS = [
  { r: 118, dur: 70, dir: 'orbitCW' }, { r: 182, dur: 105, dir: 'orbitCCW' }, { r: 246, dur: 140, dir: 'orbitCW' },
]
const RING_FOR_GROUP: Record<string, number> = {
  intelligence: 0, targeting: 0, governance: 0, optimization: 0,
  prospecting: 1, outbound: 1, revenue: 1, conversion: 1,
  lifecycle: 2, content: 2, creative: 2, paid: 2,
}

export function AgentOrbit({ cmo, agents, onSelect, size = 560 }: {
  cmo?: OrbitAgent | null; agents: OrbitAgent[]; onSelect?: (a: OrbitAgent) => void; size?: number
}) {
  const [hover, setHover] = useState<OrbitAgent | null>(null)
  const cx = size / 2, cy = size / 2
  const scale = size / 560

  const placed = useMemo(() => {
    const byRing: OrbitAgent[][] = [[], [], []]
    agents.forEach((a) => byRing[RING_FOR_GROUP[a.group] ?? 2].push(a))
    return byRing.map((list, ri) => list.map((a, i) => {
      const angle = (i / Math.max(list.length, 1)) * Math.PI * 2 - Math.PI / 2
      const r = RINGS[ri].r * scale
      return { a, x: cx + Math.cos(angle) * r, y: cy + Math.sin(angle) * r }
    }))
  }, [agents, cx, cy, scale])

  const working = agents.filter((a) => a.status === 'running').length
  const shown = hover ?? cmo ?? null

  return (
    <div className="flex flex-col items-center gap-4 xl:flex-row xl:items-center xl:gap-8">
      <div className={`relative ${hover ? 'orbit-paused' : ''}`} style={{ width: size, height: size, maxWidth: '100%' }}>
        <svg viewBox={`0 0 ${size} ${size}`} className="h-auto w-full overflow-visible">
          <defs>
            <radialGradient id="coreGrad" cx="50%" cy="50%"><stop offset="0%" stopColor="#a99cff" /><stop offset="60%" stopColor="#7c6cff" /><stop offset="100%" stopColor="#22d3ee" stopOpacity="0.2" /></radialGradient>
          </defs>
          {RINGS.map((ring, i) => (
            <circle key={i} cx={cx} cy={cy} r={ring.r * scale} fill="none" stroke="rgba(255,255,255,0.07)" strokeDasharray={i === 1 ? '2 6' : undefined} />
          ))}
          {/* faint spokes */}
          {placed.flat().map(({ a, x, y }) => <line key={`s${a.id}`} x1={cx} y1={cy} x2={x} y2={y} stroke="rgba(255,255,255,0.035)" />)}

          {/* core */}
          <g className="breathe">
            <circle cx={cx} cy={cy} r={46 * scale} fill="url(#coreGrad)" />
            <circle cx={cx} cy={cy} r={54 * scale} fill="none" stroke="rgba(124,108,255,0.35)" className="animate-pulseRing" style={{ transformOrigin: `${cx}px ${cy}px` }} />
            <text x={cx} y={cy - 4 * scale} textAnchor="middle" fontSize={11 * scale} fontWeight={800} fill="#0b0d13">AI</text>
            <text x={cx} y={cy + 9 * scale} textAnchor="middle" fontSize={9 * scale} fontWeight={700} fill="#0b0d13">MANAGER</text>
          </g>

          {/* rings of agents, slowly rotating */}
          {placed.map((list, ri) => (
            <g key={ri} className="orbit-ring" style={{ animation: `${RINGS[ri].dir} ${RINGS[ri].dur}s linear infinite`, transformOrigin: `${cx}px ${cy}px` }}>
              {list.map(({ a, x, y }) => {
                const color = GROUP_COLOR[a.group] ?? 'var(--series-6)'
                const running = a.status === 'running'
                const err = a.status === 'error'
                const isHover = hover?.id === a.id
                return (
                  <g key={a.id} onMouseEnter={() => setHover(a)} onMouseLeave={() => setHover(null)} onClick={() => onSelect?.(a)} style={{ cursor: 'pointer' }}>
                    {running && <circle cx={x} cy={y} r={11 * scale} fill={color} opacity={0.35} className="animate-pulseRing" style={{ transformOrigin: `${x}px ${y}px` }} />}
                    <circle cx={x} cy={y} r={(isHover ? 9 : 6.5) * scale} fill={err ? 'var(--status-critical)' : color} stroke="var(--surface-1)" strokeWidth={2}
                      style={{ filter: isHover || running ? `drop-shadow(0 0 8px ${color})` : undefined, transition: 'r .2s' }} />
                    {(a.pending_decisions ?? 0) > 0 && <circle cx={x + 6 * scale} cy={y - 6 * scale} r={3 * scale} fill="#a99cff" stroke="var(--surface-1)" strokeWidth={1.5} />}
                  </g>
                )
              })}
            </g>
          ))}
        </svg>
      </div>

      {/* info card: who is this, what did they just do */}
      <motion.div key={shown?.id ?? 'none'} initial={{ opacity: 0, x: 8 }} animate={{ opacity: 1, x: 0 }} className="glass w-full max-w-sm p-5">
        {shown ? (
          <>
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl" style={{ background: `color-mix(in oklab, ${GROUP_COLOR[shown.group] ?? '#7c6cff'} 22%, transparent)` }}>
                <Bot className="h-5 w-5 text-white" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="truncate text-sm font-bold text-white">{shown.name}</div>
                <div className="text-[11px] text-[var(--text-muted)]">{shown.group_label ?? shown.group}{shown.last_run_at ? ` · last worked ${relTime(shown.last_run_at)}` : ''}</div>
              </div>
              <Badge tone={statusTone(shown.status)} dot>{shown.status === 'running' ? 'working' : shown.status}</Badge>
            </div>
            <p className="mt-3 text-[13px] leading-relaxed text-[var(--text-secondary)]">{shown.last_summary || 'Has not run yet.'}</p>
            {onSelect && <button onClick={() => onSelect(shown)} className="mt-3 text-xs font-semibold text-accent-soft hover:underline">See everything it did →</button>}
          </>
        ) : <div className="text-sm text-[var(--text-muted)]">Hover a dot.</div>}
        <div className="mt-4 border-t border-white/[0.06] pt-3 text-[11px] text-[var(--text-muted)]">
          <span className="text-white">{working}</span> working right now · <span className="text-white">{agents.length}</span> specialists · hover pauses the orbit
        </div>
      </motion.div>
    </div>
  )
}
