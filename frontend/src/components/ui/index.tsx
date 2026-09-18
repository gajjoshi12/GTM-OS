import { clsx } from 'clsx'
import { motion } from 'framer-motion'
import { useEffect, useRef, useState } from 'react'
import type { ButtonHTMLAttributes, HTMLAttributes, ReactNode } from 'react'
import { ArrowDownRight, ArrowUpRight, ChevronDown, HelpCircle, Info, Loader2 } from 'lucide-react'
import { signedPct } from '@/lib/format'

/* ---------------------------------------------------------------- Panel */
export function Panel({ className, children, title, subtitle, action, padded = true, ...rest }: Omit<HTMLAttributes<HTMLDivElement>, 'title'> & {
  title?: ReactNode; subtitle?: ReactNode; action?: ReactNode; padded?: boolean
}) {
  const spot = useSpot()
  return (
    <div ref={spot.ref} onMouseMove={spot.onMouseMove} className={clsx('glass spot', padded && 'p-5', className)} {...rest}>
      {(title || action) && (
        <div className={clsx('mb-4 flex items-start justify-between gap-3', !padded && 'px-5 pt-5')}>
          <div>
            {title && <h3 className="text-sm font-semibold text-white">{title}</h3>}
            {subtitle && <p className="mt-0.5 text-xs text-[var(--text-muted)]">{subtitle}</p>}
          </div>
          {action}
        </div>
      )}
      {children}
    </div>
  )
}

/* ---------------------------------------------------------------- Button */
type BtnVariant = 'primary' | 'ghost' | 'outline' | 'danger' | 'success' | 'subtle'
export function Button({ variant = 'primary', size = 'md', loading, className, children, ...rest }: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: BtnVariant; size?: 'sm' | 'md' | 'lg'; loading?: boolean
}) {
  const base = 'inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/60'
  const sizes = { sm: 'h-8 px-3 text-xs', md: 'h-10 px-4 text-sm', lg: 'h-12 px-6 text-base' }
  const variants: Record<BtnVariant, string> = {
    primary: 'bg-gradient-to-r from-accent to-accent-cyan text-ink-950 shadow-glow hover:brightness-110 active:scale-[0.98]',
    ghost: 'text-[var(--text-secondary)] hover:bg-white/5 hover:text-white',
    outline: 'border border-white/10 bg-white/[0.03] text-white hover:bg-white/[0.07]',
    subtle: 'bg-white/[0.06] text-white hover:bg-white/[0.1]',
    danger: 'border border-rose-500/30 bg-rose-500/10 text-rose-300 hover:bg-rose-500/20',
    success: 'border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20',
  }
  return (
    <button className={clsx(base, sizes[size], variants[variant], className)} disabled={loading || rest.disabled} {...rest}>
      {loading && <Loader2 className="h-4 w-4 animate-spin" />}
      {children}
    </button>
  )
}

/* ---------------------------------------------------------------- Badge */
export type Tone = 'neutral' | 'accent' | 'cyan' | 'good' | 'warn' | 'bad' | 'violet' | 'amber'
const tones: Record<Tone, string> = {
  neutral: 'bg-white/[0.06] text-[var(--text-secondary)] border-white/10',
  accent: 'bg-accent/15 text-accent-soft border-accent/30',
  cyan: 'bg-cyan-400/10 text-cyan-300 border-cyan-400/30',
  good: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
  warn: 'bg-amber-400/10 text-amber-300 border-amber-400/30',
  bad: 'bg-rose-500/10 text-rose-300 border-rose-500/30',
  violet: 'bg-violet-500/10 text-violet-300 border-violet-500/30',
  amber: 'bg-orange-400/10 text-orange-300 border-orange-400/30',
}
export function Badge({ tone = 'neutral', className, children, dot }: { tone?: Tone; className?: string; children: ReactNode; dot?: boolean }) {
  return (
    <span className={clsx('inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[11px] font-medium', tones[tone], className)}>
      {dot && <span className="h-1.5 w-1.5 rounded-full bg-current" />}
      {children}
    </span>
  )
}

export const statusTone = (s: string): Tone => {
  const map: Record<string, Tone> = {
    active: 'good', live: 'good', running: 'cyan', succeeded: 'good', approved: 'good', executed: 'good', connected: 'good', valid: 'good', passed: 'good', published: 'good', concluded: 'good',
    pending: 'warn', pending_approval: 'warn', queued: 'warn', proposed: 'neutral', scheduled: 'cyan', drafted: 'neutral', draft: 'neutral', idle: 'neutral', risky: 'warn', flagged: 'warn', env_configured: 'cyan',
    paused: 'amber', rejected: 'bad', failed: 'bad', error: 'bad', invalid: 'bad', not_connected: 'neutral', simulated: 'violet', unverified: 'neutral', ended: 'neutral', completed: 'neutral',
    high: 'amber', critical: 'bad', medium: 'warn', low: 'neutral',
  }
  return map[s] ?? 'neutral'
}

/* ---------------------------------------------------------------- StatTile */
export function StatTile({ label, value, delta, hint, upIsGood = true, accent, spark, className, explain, big, count, fmt }: {
  label: string; value?: ReactNode; delta?: number | null; hint?: string; upIsGood?: boolean; accent?: string
  spark?: number[]; className?: string; explain?: string; big?: boolean
  /** Give a raw number + formatter and the tile counts up instead of rendering `value`. */
  count?: number; fmt?: (n: number) => string
}) {
  const d = delta ?? null
  const good = d == null ? null : upIsGood ? d >= 0 : d <= 0
  const spot = useSpot()
  const shown = count != null ? <CountUp value={count} format={fmt} /> : value
  return (
    <motion.div ref={spot.ref} onMouseMove={spot.onMouseMove} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={clsx('glass spot p-4', className)}>
      <div className="flex items-start justify-between">
        <span className="label flex items-center gap-1.5">{label}<Explain text={explain} /></span>
        {accent && <span className="h-2 w-2 rounded-full" style={{ background: accent }} />}
      </div>
      <div className="mt-2 flex items-end justify-between gap-3">
        <div>
          <div className={clsx('whitespace-nowrap font-bold tracking-tight text-white', big ? 'text-[26px] xl:text-3xl' : 'text-xl xl:text-[22px]')}>{shown}</div>
          {(d != null || hint) && (
            <div className="mt-1 flex items-center gap-2 text-xs">
              {d != null && (
                <span className={clsx('inline-flex items-center gap-0.5 font-semibold', good ? 'text-emerald-300' : 'text-rose-300')}>
                  {d >= 0 ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}{signedPct(d)}
                </span>
              )}
              {hint && <span className="text-[var(--text-muted)]">{hint}</span>}
            </div>
          )}
        </div>
        {spark && spark.length > 1 && <Sparkline data={spark} color={accent ?? 'var(--series-1)'} w={56} h={24} />}
      </div>
    </motion.div>
  )
}

/* ---------------------------------------------------------------- Sparkline */
export function Sparkline({ data, color = 'var(--series-1)', w = 84, h = 28 }: { data: number[]; color?: string; w?: number; h?: number }) {
  const max = Math.max(...data), min = Math.min(...data)
  const pts = data.map((v, i) => [ (i / (data.length - 1)) * w, h - ((v - min) / (max - min || 1)) * (h - 4) - 2 ])
  const path = pts.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ')
  const last = pts[pts.length - 1]
  return (
    <svg width={w} height={h} className="overflow-visible">
      <path d={path} fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" opacity={0.9} />
      <circle cx={last[0]} cy={last[1]} r={3.5} fill={color} stroke="var(--surface-1)" strokeWidth={2} />
    </svg>
  )
}

/* ---------------------------------------------------------------- Progress / Meter */
export function Meter({ value, max = 100, color = 'var(--series-1)', className, height = 6 }: { value: number; max?: number; color?: string; className?: string; height?: number }) {
  const p = Math.max(0, Math.min(100, (value / max) * 100))
  return (
    <div className={clsx('w-full overflow-hidden rounded-full bg-white/[0.07]', className)} style={{ height }}>
      <motion.div initial={{ width: 0 }} animate={{ width: `${p}%` }} transition={{ duration: 0.8, ease: 'easeOut' }} className="h-full rounded-full" style={{ background: color }} />
    </div>
  )
}

/* ---------------------------------------------------------------- PageHeader */
export function PageHeader({ title, description, actions }: { title: ReactNode; description?: ReactNode; actions?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white md:text-[28px]">{title}</h1>
        {description && <p className="mt-1.5 max-w-2xl text-[13px] leading-relaxed text-[var(--text-secondary)]">{description}</p>}
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </div>
  )
}

/* ---------------------------------------------------------------- Skeleton / Empty */
export function Skeleton({ className }: { className?: string }) {
  return <div className={clsx('shimmer rounded-xl', className)} />
}

export function Empty({ title, hint, action }: { title: string; hint?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-white/10 py-14 text-center">
      <div className="text-sm font-semibold text-white">{title}</div>
      {hint && <div className="mt-1 max-w-sm text-xs text-[var(--text-muted)]">{hint}</div>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}

/* ---------------------------------------------------------------- Tabs */
export function Tabs<T extends string>({ tabs, value, onChange }: { tabs: { key: T; label: string; count?: number }[]; value: T; onChange: (t: T) => void }) {
  return (
    <div className="inline-flex rounded-xl border border-white/10 bg-white/[0.03] p-1">
      {tabs.map((t) => (
        <button key={t.key} onClick={() => onChange(t.key)}
          className={clsx('relative rounded-lg px-3 py-1.5 text-xs font-semibold transition', value === t.key ? 'text-white' : 'text-[var(--text-muted)] hover:text-white')}>
          {value === t.key && <motion.span layoutId="tab-pill" className="absolute inset-0 rounded-lg bg-white/[0.08]" transition={{ type: 'spring', stiffness: 400, damping: 30 }} />}
          <span className="relative">{t.label}{t.count != null && <span className="ml-1.5 text-[var(--text-muted)]">{t.count}</span>}</span>
        </button>
      ))}
    </div>
  )
}

/* ---------------------------------------------------------------- Avatar / Logo mark */
export function Mark({ seed, size = 32, className }: { seed: string; size?: number; className?: string }) {
  let h = 0
  for (const ch of seed) h = (h * 31 + ch.charCodeAt(0)) >>> 0
  const hue = h % 360
  const initials = seed.split(/[\s.-]+/).slice(0, 2).map((s) => s[0]?.toUpperCase() ?? '').join('')
  return (
    <div className={clsx('flex shrink-0 items-center justify-center rounded-xl font-bold text-white', className)}
      style={{ width: size, height: size, fontSize: size * 0.36, background: `linear-gradient(135deg, hsl(${hue} 70% 45%), hsl(${(hue + 40) % 360} 70% 35%))` }}>
      {initials}
    </div>
  )
}

/* ---------------------------------------------------------------- Modal */
export function Modal({ open, onClose, title, children, width = 'max-w-lg' }: { open: boolean; onClose: () => void; title?: ReactNode; children: ReactNode; width?: string }) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-ink-950/70 backdrop-blur-sm" />
      <motion.div initial={{ opacity: 0, scale: 0.96, y: 8 }} animate={{ opacity: 1, scale: 1, y: 0 }} onClick={(e) => e.stopPropagation()}
        className={clsx('glass-strong relative w-full p-6', width)}>
        {title && <h3 className="mb-4 text-base font-semibold text-white">{title}</h3>}
        {children}
      </motion.div>
    </div>
  )
}

/* ---------------------------------------------------------------- Field */
export function Field({ label, children, hint }: { label: string; children: ReactNode; hint?: string }) {
  return (
    <label className="block">
      <span className="label mb-1.5 block">{label}</span>
      {children}
      {hint && <span className="mt-1 block text-[11px] text-[var(--text-muted)]">{hint}</span>}
    </label>
  )
}
export const inputCls = 'w-full rounded-xl border border-white/10 bg-white/[0.04] px-3 py-2.5 text-sm text-white placeholder:text-[var(--text-muted)] outline-none transition focus:border-accent/60 focus:bg-white/[0.06] focus:ring-2 focus:ring-accent/20'

/* ---------------------------------------------------------------- Explain
 * A small ⓘ that turns jargon into a plain sentence on hover/tap. Used wherever
 * the product's own vocabulary (CAC, ROAS, ICP, pipeline) leaks into the UI.
 */
export function Explain({ text, className }: { text?: string; className?: string }) {
  if (!text) return null
  return (
    <span className={clsx('group/ex relative inline-flex items-center', className)}>
      <HelpCircle className="h-3 w-3 cursor-help text-[var(--text-muted)] transition hover:text-white" />
      <span role="tooltip"
        className="pointer-events-none absolute bottom-full left-1/2 z-50 mb-2 w-56 -translate-x-1/2 rounded-xl border border-white/10 bg-ink-850 p-2.5 text-[11px] font-normal leading-relaxed text-[var(--text-secondary)] opacity-0 shadow-glass transition-opacity duration-150 group-hover/ex:opacity-100">
        {text}
      </span>
    </span>
  )
}

/* ---------------------------------------------------------------- Callout
 * One plain-English sentence explaining what a screen is for, in the user's words.
 */
export function Callout({ children, tone = 'info' }: { children: ReactNode; tone?: 'info' | 'warn' }) {
  return (
    <div className={clsx('flex items-start gap-2.5 rounded-xl border px-3.5 py-2.5 text-[13px] leading-relaxed',
      tone === 'warn' ? 'border-amber-400/25 bg-amber-400/[0.07] text-amber-100' : 'border-white/[0.08] bg-white/[0.03] text-[var(--text-secondary)]')}>
      <Info className="mt-0.5 h-4 w-4 shrink-0 text-[var(--text-muted)]" />
      <div>{children}</div>
    </div>
  )
}

/* ---------------------------------------------------------------- Disclosure
 * Hides secondary detail behind one click so the default view stays scannable.
 */
export function Disclosure({ label, children, count }: { label: string; children: ReactNode; count?: number }) {
  const [open, setOpen] = useState(false)
  return (
    <div>
      <button onClick={() => setOpen((o) => !o)}
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-[var(--text-muted)] transition hover:text-white">
        <ChevronDown className={clsx('h-3.5 w-3.5 transition-transform', open && 'rotate-180')} />
        {open ? 'Hide' : label}{count != null && !open && <span className="text-[var(--text-muted)]">({count})</span>}
      </button>
      {open && <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="mt-3 overflow-hidden">{children}</motion.div>}
    </div>
  )
}

/* ---------------------------------------------------------------- CountUp
 * Animates a number from its previous value to the new one. Honors
 * prefers-reduced-motion by jumping straight to the target.
 */
export function CountUp({ value, format = (n) => Math.round(n).toLocaleString(), duration = 1400, className }: {
  value: number; format?: (n: number) => string; duration?: number; className?: string
}) {
  const [shown, setShown] = useState(0)
  const prev = useRef(0)
  useEffect(() => {
    const reduce = typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    const from = prev.current, to = Number(value) || 0
    if (reduce || from === to) { setShown(to); prev.current = to; return }
    const start = performance.now()
    let raf = 0
    const tick = (t: number) => {
      const p = Math.min(1, (t - start) / duration)
      const eased = 1 - Math.pow(1 - p, 3)
      setShown(from + (to - from) * eased)
      if (p < 1) raf = requestAnimationFrame(tick)
      else prev.current = to
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [value, duration])
  return <span className={className}>{format(shown)}</span>
}

/* ---------------------------------------------------------------- Spotlight
 * Cursor-following glow. Attach the returned props to any element with the
 * `spot` class; the CSS does the rest.
 */
export function useSpot<T extends HTMLElement = HTMLDivElement>() {
  const ref = useRef<T>(null)
  const onMouseMove = (e: React.MouseEvent<T>) => {
    const el = ref.current
    if (!el) return
    const r = el.getBoundingClientRect()
    el.style.setProperty('--mx', `${e.clientX - r.left}px`)
    el.style.setProperty('--my', `${e.clientY - r.top}px`)
  }
  return { ref, onMouseMove }
}

/* ---------------------------------------------------------------- Ring
 * Circular progress with a gradient stroke, animated on mount / change.
 */
export function Ring({ value, max = 100, size = 168, stroke = 12, children, className }: {
  value: number; max?: number; size?: number; stroke?: number; children?: ReactNode; className?: string
}) {
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  const p = Math.max(0, Math.min(1, value / (max || 1)))
  const id = useRef(`ring-${Math.random().toString(36).slice(2, 8)}`).current
  return (
    <div className={clsx('relative shrink-0', className)} style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <defs>
          <linearGradient id={id} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#7c6cff" /><stop offset="100%" stopColor="#22d3ee" />
          </linearGradient>
        </defs>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={stroke} />
        <motion.circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={`url(#${id})`} strokeWidth={stroke} strokeLinecap="round"
          strokeDasharray={c} initial={{ strokeDashoffset: c }} animate={{ strokeDashoffset: c * (1 - p) }}
          transition={{ duration: 1.6, ease: [0.2, 0.8, 0.2, 1] }}
          style={{ filter: 'drop-shadow(0 0 10px rgba(124,108,255,0.55))' }} />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">{children}</div>
    </div>
  )
}
