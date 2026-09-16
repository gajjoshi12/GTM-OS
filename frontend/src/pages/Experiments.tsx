import { useState } from 'react'
import { motion } from 'framer-motion'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Brain, FlaskConical, Play, Sparkles, Trophy } from 'lucide-react'
import { get, post } from '@/lib/api'
import { channelColor, channelLabel, relTime, title } from '@/lib/format'
import { Badge, Button, Meter, PageHeader, Panel, Tabs, statusTone } from '@/components/ui'

type Variant = { label: string; exposures: number; conversions: number }
type Experiment = { id: number; name: string; hypothesis: string; channel: string; variable: string; variants: Variant[]; status: string; confidence: number; winner: string; lift_pct: number; learning: string; started_at: string | null; concluded_at: string | null; owner_agent: string }
type Insight = { id: number; statement: string; category: string; confidence: number; applies_to: string[]; source_experiment_name: string; times_applied: number; impact_score: number }
type Stats = { running: number; proposed: number; concluded: number; winners: number; avg_lift: number }

const CAT_COLOR: Record<string, string> = { messaging: 'var(--series-1)', conversion: 'var(--series-3)', creative: 'var(--series-5)', timing: 'var(--series-4)', channel: 'var(--series-2)', content: 'var(--series-6)', governance: 'var(--series-7)' }

export function ExperimentsPage() {
  const qc = useQueryClient()
  const [tab, setTab] = useState<'experiments' | 'memory'>('experiments')
  const [status, setStatus] = useState<'' | 'running' | 'concluded' | 'proposed'>('')
  const { data: stats } = useQuery({ queryKey: ['experiments', 'stats'], queryFn: () => get<Stats>('/analytics/experiments/stats/') })
  const { data: exps } = useQuery({ queryKey: ['experiments', status], queryFn: () => get<Experiment[]>('/analytics/experiments/', { status: status || undefined }) })
  const { data: memory } = useQuery({ queryKey: ['memory'], queryFn: () => get<Insight[]>('/analytics/memory/') })
  const inval = () => { qc.invalidateQueries({ queryKey: ['experiments'] }); qc.invalidateQueries({ queryKey: ['decisions'] }) }
  const propose = useMutation({ mutationFn: () => post('/analytics/experiments/propose/', {}), onSuccess: inval })
  const setSt = useMutation({ mutationFn: ({ id, s }: { id: number; s: string }) => post(`/analytics/experiments/${id}/set_status/`, { status: s }), onSuccess: inval })

  return (
    <div className="space-y-6">
      <PageHeader title={<>Tests and <span className="gradient-text">lessons learned</span></>}
        description="Every change is run as a proper test. When one clearly wins, the lesson is saved and applied everywhere else automatically — so the system keeps getting better on its own."
        actions={<><Tabs tabs={[{ key: 'experiments', label: 'Tests' }, { key: 'memory', label: 'What we have learned', count: memory?.length }]} value={tab} onChange={setTab} /><Button onClick={() => propose.mutate()} loading={propose.isPending}><Sparkles className="h-4 w-4" /> Suggest new tests</Button></>} />

      <div className="grid grid-cols-2 gap-3 md:grid-cols-5">
        {[['Running now', stats?.running], ['Queued up', stats?.proposed], ['Finished', stats?.concluded], ['Clear winners', stats?.winners], ['Avg improvement', `${stats?.avg_lift ?? 0}%`]].map(([l, v]) => <div key={String(l)} className="glass p-4"><div className="label">{l}</div><div className="mt-1 text-2xl font-bold text-white">{v ?? '—'}</div></div>)}
      </div>

      {tab === 'experiments' && (
        <>
          <Tabs tabs={[{ key: '', label: 'All' }, { key: 'running', label: 'Running now' }, { key: 'concluded', label: 'Finished' }, { key: 'proposed', label: 'Ideas' }]} value={status} onChange={setStatus} />
          <div className="grid gap-3 md:grid-cols-2">
            {exps?.map((e, i) => {
              const total = e.variants.reduce((a, v) => a + v.exposures, 0)
              return (
                <motion.div key={e.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }} className="glass p-5">
                  <div className="flex items-start justify-between gap-2"><div><div className="flex items-center gap-2"><span className="h-2 w-2 rounded-full" style={{ background: channelColor(e.channel) }} /><span className="label">{channelLabel(e.channel)} · {title(e.variable)}</span></div><h3 className="mt-1 text-sm font-bold text-white">{e.name}</h3></div><Badge tone={statusTone(e.status)} dot>{e.status}</Badge></div>
                  <p className="mt-2 text-xs italic text-[var(--text-secondary)]">Testing whether: {e.hypothesis}</p>
                  {e.variants.length > 0 && total > 0 && (
                    <div className="mt-3 space-y-2">{e.variants.map((v) => { const cr = v.exposures ? (v.conversions / v.exposures) * 100 : 0; const best = Math.max(...e.variants.map((x) => x.exposures ? x.conversions / x.exposures : 0)) * 100; return (
                      <div key={v.label}><div className="flex justify-between text-[11px]"><span className="flex items-center gap-1.5 text-white">{v.label}{e.winner === v.label && <Trophy className="h-3 w-3 text-amber-300" />}</span><span className="num text-[var(--text-secondary)]">{v.conversions}/{v.exposures} · <b className="text-white">{cr.toFixed(1)}%</b></span></div><Meter value={cr} max={best * 1.15} height={5} color={e.winner === v.label ? 'var(--status-good)' : 'var(--series-1)'} /></div>) })}</div>
                  )}
                  <div className="mt-3 flex flex-wrap items-center gap-3 text-[11px] text-[var(--text-muted)]">
                    <span>How sure <b className="num text-white">{Math.round(e.confidence * 100)}%</b></span>
                    {e.lift_pct > 0 && <span>Better by <b className="num text-emerald-300">{e.lift_pct}%</b></span>}
                    <span>Owner: {title(e.owner_agent)}</span>
                    {e.started_at && <span>started {relTime(e.started_at)}</span>}
                    <span className="ml-auto flex gap-2">{e.status === 'proposed' && <Button size="sm" variant="subtle" onClick={() => setSt.mutate({ id: e.id, s: 'running' })}><Play className="h-3 w-3" /> Start</Button>}{e.status === 'running' && e.confidence >= 0.95 && <Button size="sm" variant="success" onClick={() => setSt.mutate({ id: e.id, s: 'concluded' })}>Conclude</Button>}</span>
                  </div>
                  {e.learning && <div className="mt-3 rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3 text-xs text-emerald-100"><Brain className="mr-1 inline h-3.5 w-3.5" />{e.learning}</div>}
                </motion.div>
              )
            })}
          </div>
        </>
      )}

      {tab === 'memory' && (
        <div className="grid gap-3 md:grid-cols-2">
          {memory?.map((m, i) => (
            <motion.div key={m.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }} className="glass relative overflow-hidden p-5">
              <span className="absolute inset-y-0 left-0 w-[3px]" style={{ background: CAT_COLOR[m.category] ?? 'var(--series-6)' }} />
              <div className="flex items-center gap-2"><Badge tone="neutral">{title(m.category)}</Badge><span className="text-[11px] text-[var(--text-muted)]">{Math.round(m.confidence * 100)}% sure · used {m.times_applied} times</span><span className="ml-auto num text-xs font-bold text-white">impact {m.impact_score}</span></div>
              <p className="mt-2 text-[15px] font-semibold leading-snug text-white">“{m.statement}”</p>
              <div className="mt-3 flex flex-wrap gap-1.5">{m.applies_to.map((a) => <span key={a} className="rounded-md bg-white/[0.05] px-1.5 py-0.5 font-mono text-[10px] text-[var(--text-secondary)]">→ {a}</span>)}</div>
              {m.source_experiment_name && <div className="mt-2 flex items-center gap-1 text-[11px] text-[var(--text-muted)]"><FlaskConical className="h-3 w-3" /> from: {m.source_experiment_name}</div>}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
