import { useState } from 'react'
import { motion } from 'framer-motion'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { AlertTriangle, Check, Lightbulb, MessageCircleQuestion, ShieldCheck, Sparkles, TrendingUp, X } from 'lucide-react'
import { Badge, Button, Disclosure, statusTone } from '@/components/ui'
import { post } from '@/lib/api'
import { relTime, title } from '@/lib/format'

export type Decision = {
  id: number; agent_name: string; agent_key: string; title: string; body: string; category: string; impact: string; confidence: number
  status: string; requires_approval: boolean; action: { type?: string }; metrics: Record<string, number>; conversation: { role: string; text: string }[]; created_at: string
}

const ICON: Record<string, typeof Lightbulb> = {
  insight: Lightbulb, opportunity: TrendingUp, alert: AlertTriangle, recommendation: Sparkles, approval: ShieldCheck,
}

/** Plain words for the product's own labels. */
const CATEGORY_LABEL: Record<string, string> = {
  insight: 'Something to know',
  opportunity: 'Opportunity',
  alert: 'Heads up',
  recommendation: 'Suggestion',
  approval: 'Needs your OK',
}
const CAT_TONE: Record<string, 'accent' | 'cyan' | 'warn' | 'good' | 'violet'> = {
  insight: 'cyan', opportunity: 'good', alert: 'warn', recommendation: 'accent', approval: 'violet',
}
const IMPACT_LABEL: Record<string, string> = { critical: 'Urgent', high: 'Big impact', medium: 'Worth doing', low: 'Minor' }

export function DecisionCard({ d, compact }: { d: Decision; compact?: boolean }) {
  const qc = useQueryClient()
  const [asking, setAsking] = useState(false)
  const [q, setQ] = useState('')

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ['decisions'] })
    qc.invalidateQueries({ queryKey: ['dashboard'] })
    qc.invalidateQueries({ queryKey: ['activity'] })
  }
  const act = useMutation({
    mutationFn: (verb: 'approve' | 'reject' | 'ask') => post<Decision>(`/agents/decisions/${d.id}/${verb}/`, { message: q }),
    onSuccess: () => { invalidate(); setQ(''); setAsking(false) },
  })

  const Icon = ICON[d.category] ?? Sparkles
  const pending = d.status === 'pending'
  const important = d.impact === 'high' || d.impact === 'critical'
  const hasDetails = Object.keys(d.metrics ?? {}).length > 0

  return (
    <motion.div layout initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, scale: 0.98 }}
      className={`glass group relative overflow-hidden ${compact ? 'p-4' : 'p-5'}`}>
      {important && <span className="absolute inset-y-0 left-0 w-[3px] bg-gradient-to-b from-accent to-accent-cyan" />}

      <div className="flex items-start gap-3">
        <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-white/[0.05] text-accent-soft">
          <Icon className="h-4 w-4" />
        </div>

        <div className="min-w-0 flex-1">
          {/* The headline is the thing to read. Everything else is supporting. */}
          <h4 className="text-[15px] font-semibold leading-snug text-white">{d.title}</h4>
          {!compact && <p className="mt-1.5 text-sm leading-relaxed text-[var(--text-secondary)]">{d.body}</p>}

          <div className="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-[var(--text-muted)]">
            <Badge tone={CAT_TONE[d.category] ?? 'neutral'}>{CATEGORY_LABEL[d.category] ?? title(d.category)}</Badge>
            {important && <Badge tone={statusTone(d.impact)}>{IMPACT_LABEL[d.impact] ?? d.impact}</Badge>}
            <span>From {d.agent_name} · {relTime(d.created_at)}</span>
            {!pending && <Badge tone={statusTone(d.status)} className="ml-auto">{title(d.status)}</Badge>}
          </div>

          {!compact && hasDetails && (
            <div className="mt-3">
              <Disclosure label="Show the numbers">
                <div className="flex flex-wrap gap-2">
                  {Object.entries(d.metrics).map(([k, v]) => (
                    <span key={k} className="rounded-lg border border-white/[0.06] bg-white/[0.03] px-2 py-1 font-mono text-[11px] text-[var(--text-secondary)]">
                      <span className="text-[var(--text-muted)]">{k.replace(/_/g, ' ')}</span>{' '}
                      <span className="text-white">{typeof v === 'number' ? v.toLocaleString() : String(v)}</span>
                    </span>
                  ))}
                  <span className="rounded-lg border border-white/[0.06] bg-white/[0.03] px-2 py-1 font-mono text-[11px] text-[var(--text-secondary)]">
                    <span className="text-[var(--text-muted)]">how sure</span> <span className="text-white">{Math.round(d.confidence * 100)}%</span>
                  </span>
                </div>
              </Disclosure>
            </div>
          )}

          {d.conversation?.length > 0 && (
            <div className="mt-3 space-y-2 rounded-xl border border-white/[0.06] bg-ink-900/60 p-3">
              {d.conversation.map((m, i) => (
                <div key={i} className={`text-xs leading-relaxed ${m.role === 'ai' ? 'text-white' : 'text-[var(--text-secondary)]'}`}>
                  <span className="mr-1 font-semibold text-accent-soft">{m.role === 'ai' ? 'AI' : 'You'}:</span>{m.text}
                </div>
              ))}
            </div>
          )}

          {asking && (
            <div className="mt-3 flex gap-2">
              <input autoFocus value={q} onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && q && act.mutate('ask')}
                placeholder="Ask anything about this…"
                className="flex-1 rounded-xl border border-white/10 bg-white/[0.04] px-3 py-2 text-sm text-white outline-none focus:border-accent/60" />
              <Button size="sm" variant="subtle" loading={act.isPending} onClick={() => act.mutate('ask')} disabled={!q}>Ask</Button>
            </div>
          )}

          {pending && (
            <div className="mt-3 flex flex-wrap gap-2">
              {d.requires_approval && (
                <Button size="sm" variant="success" loading={act.isPending} onClick={() => act.mutate('approve')}>
                  <Check className="h-3.5 w-3.5" /> Approve
                </Button>
              )}
              <Button size="sm" variant="danger" onClick={() => act.mutate('reject')}><X className="h-3.5 w-3.5" /> Skip</Button>
              <Button size="sm" variant="ghost" onClick={() => setAsking((a) => !a)}>
                <MessageCircleQuestion className="h-3.5 w-3.5" /> Why this?
              </Button>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}
