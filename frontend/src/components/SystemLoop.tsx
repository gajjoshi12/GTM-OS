import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Brain, Handshake, Megaphone, RotateCcw, Search, ShieldCheck, Trophy } from 'lucide-react'
import { CountUp, useSpot } from '@/components/ui'

/**
 * The whole product in one line: the closed loop from the spec, with live
 * numbers. Left to right, then it repeats. Each stage is a door into the
 * screen that runs it.
 */
export type LoopStage = {
  key: string
  label: string
  sub: string
  value: number
  fmt?: (n: number) => string
  to: string
  color: string
  icon: 'search' | 'megaphone' | 'handshake' | 'trophy' | 'brain' | 'shield'
  hot?: boolean
}

const ICONS = { search: Search, megaphone: Megaphone, handshake: Handshake, trophy: Trophy, brain: Brain, shield: ShieldCheck }

function Connector({ delay }: { delay: number }) {
  return (
    <div className="hidden h-full min-w-[34px] flex-1 items-center lg:flex" aria-hidden>
      <svg viewBox="0 0 60 12" className="h-3 w-full overflow-visible" preserveAspectRatio="none">
        <line x1="0" y1="6" x2="60" y2="6" stroke="rgba(255,255,255,0.10)" strokeWidth="2" />
        <line x1="0" y1="6" x2="60" y2="6" stroke="url(#loopGrad)" strokeWidth="2" className="flow-line" style={{ animationDelay: `${delay}s` }} />
      </svg>
    </div>
  )
}

function Stage({ s, i }: { s: LoopStage; i: number }) {
  const nav = useNavigate()
  const Icon = ICONS[s.icon]
  const spot = useSpot<HTMLButtonElement>()
  return (
    <motion.button ref={spot.ref} onMouseMove={spot.onMouseMove} onClick={() => nav(s.to)}
      initial={{ opacity: 0, y: 14, scale: 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }} transition={{ delay: 0.08 * i, type: 'spring', stiffness: 260, damping: 24 }}
      whileHover={{ y: -4 }}
      className={`glass spot group relative flex min-w-[150px] flex-1 flex-col items-start gap-2 p-4 text-left ${s.hot ? 'ring-live' : ''}`}>
      <span className="absolute inset-x-4 top-0 h-px" style={{ background: `linear-gradient(90deg, transparent, ${s.color}, transparent)` }} />
      <span className="flex h-9 w-9 items-center justify-center rounded-xl" style={{ background: `color-mix(in oklab, ${s.color} 18%, transparent)`, color: s.color }}>
        <Icon className="h-4 w-4" />
      </span>
      <span className="display-num text-3xl text-white"><CountUp value={s.value} format={s.fmt} /></span>
      <span>
        <span className="block text-[13px] font-semibold text-white">{s.label}</span>
        <span className="block text-[11px] text-[var(--text-muted)]">{s.sub}</span>
      </span>
      <span className="absolute right-3 top-3 text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)] opacity-0 transition group-hover:opacity-100">open →</span>
    </motion.button>
  )
}

export function SystemLoop({ stages }: { stages: LoopStage[] }) {
  return (
    <div className="relative">
      <svg width="0" height="0" className="absolute"><defs>
        <linearGradient id="loopGrad" x1="0" x2="1"><stop offset="0" stopColor="#7c6cff" /><stop offset="1" stopColor="#22d3ee" /></linearGradient>
      </defs></svg>
      <div className="flex flex-col gap-3 lg:flex-row lg:items-stretch lg:gap-0">
        {stages.map((s, i) => (
          <div key={s.key} className="contents">
            <Stage s={s} i={i} />
            {i < stages.length - 1 && <Connector delay={i * 0.18} />}
          </div>
        ))}
      </div>
      <div className="mt-3 flex items-center justify-end gap-2 text-[11px] text-[var(--text-muted)]">
        <RotateCcw className="h-3 w-3 text-accent-soft" />
        then it learns from what happened and starts again — automatically
      </div>
    </div>
  )
}
