import { useState } from 'react'
import { motion } from 'framer-motion'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Inbox, Link2, Mail, Pause, Play, Sparkles } from 'lucide-react'
import { get, post, type Paginated } from '@/lib/api'
import { num, relTime, title } from '@/lib/format'
import { Badge, Button, Meter, PageHeader, Panel, Tabs, statusTone } from '@/components/ui'

type Step = { day: number; channel: string; type: string; subject: string; body: string }
type Sequence = { id: number; name: string; icp_name: string; persona: string; channel: string; status: string; steps: Step[]; enrolled: number; sent: number; opened: number; replied: number; positive_replies: number; meetings: number; bounced: number; reply_rate: number; compliance_status: string; daily_cap: number }
type Stats = { enrolled: number; sent: number; opened: number; replied: number; positive: number; meetings: number; bounced: number; active: number; reply_rate: number; positive_rate: number; bounce_rate: number }
type Reply = { id: number; contact_name: string; contact_title: string; company_name: string; company_tier: number; sequence_name: string; body: string; classification: string; confidence: number; next_action: string; sdr_response: string; handled: boolean; meeting_booked_at: string | null; received_at: string }
type Breakdown = { total: number; unhandled: number; by_class: { classification: string; count: number }[]; meetings: number }

const CLASS_TONE: Record<string, 'good' | 'cyan' | 'warn' | 'bad' | 'neutral' | 'accent'> = { interested: 'good', meeting_request: 'good', pricing_request: 'cyan', send_info: 'cyan', not_now: 'warn', wrong_person: 'accent', objection: 'warn', unsubscribe: 'bad', negative: 'bad', out_of_office: 'neutral' }

export function OutboundPage() {
  const qc = useQueryClient()
  const [tab, setTab] = useState<'sequences' | 'inbox'>('sequences')
  const [sel, setSel] = useState<number | null>(null)
  const [filter, setFilter] = useState<'unhandled' | 'all'>('unhandled')
  const { data: stats } = useQuery({ queryKey: ['sequences', 'stats'], queryFn: () => get<Stats>('/outbound/sequences/stats/') })
  const { data: seqs } = useQuery({ queryKey: ['sequences'], queryFn: () => get<Sequence[]>('/outbound/sequences/') })
  const { data: replies } = useQuery({ queryKey: ['replies', filter], queryFn: () => get<Paginated<Reply>>('/outbound/replies/', { handled: filter === 'unhandled' ? 'false' : undefined, page_size: 40 }) })
  const { data: breakdown } = useQuery({ queryKey: ['replies', 'breakdown'], queryFn: () => get<Breakdown>('/outbound/replies/breakdown/') })
  const inval = () => { qc.invalidateQueries({ queryKey: ['sequences'] }); qc.invalidateQueries({ queryKey: ['replies'] }); qc.invalidateQueries({ queryKey: ['decisions'] }); qc.invalidateQueries({ queryKey: ['activity'] }) }
  const setStatus = useMutation({ mutationFn: ({ id, status }: { id: number; status: string }) => post(`/outbound/sequences/${id}/set_status/`, { status }), onSuccess: inval })
  const generate = useMutation({ mutationFn: () => post('/outbound/sequences/generate/', {}), onSuccess: inval })
  const handle = useMutation({ mutationFn: (id: number) => post(`/outbound/replies/${id}/handle/`, {}), onSuccess: inval })
  const active = seqs?.find((s) => s.id === sel) ?? seqs?.[0]

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Phases 5–6 · Personalization → Outbound → Reply Intelligence → AI SDR" title={<>Outbound that reads like <span className="gradient-text">a human who did the research</span></>}
        description="Prospects → intelligence cards → hyper-personalized copy → AI QA → verification → adaptive cadences → throttled sends → classified replies → AI SDR books the meeting."
        actions={<><Tabs tabs={[{ key: 'sequences', label: 'Sequences', count: seqs?.length }, { key: 'inbox', label: 'Reply inbox', count: breakdown?.unhandled }]} value={tab} onChange={setTab} /><Button onClick={() => generate.mutate()} loading={generate.isPending}><Sparkles className="h-4 w-4" /> Generate sequence</Button></>} />

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-7">
        {[['Enrolled', num(stats?.enrolled)], ['Sent', num(stats?.sent)], ['Open rate', stats && stats.sent ? `${Math.round((stats.opened / stats.sent) * 100)}%` : '—'], ['Reply rate', `${stats?.reply_rate ?? 0}%`], ['Positive rate', `${stats?.positive_rate ?? 0}%`], ['Meetings', num(stats?.meetings)], ['Bounce rate', `${stats?.bounce_rate ?? 0}%`]].map(([l, v]) => (
          <div key={l} className="glass p-4"><div className="label">{l}</div><div className="mt-1 text-2xl font-bold text-white">{v}</div></div>
        ))}
      </div>

      {tab === 'sequences' && (
        <div className="grid gap-4 xl:grid-cols-[1fr_1.4fr]">
          <div className="space-y-2">
            {seqs?.map((s) => (
              <button key={s.id} onClick={() => setSel(s.id)} className={`glass w-full p-4 text-left transition hover:bg-white/[0.05] ${active?.id === s.id ? 'ring-1 ring-accent/50' : ''}`}>
                <div className="flex items-start justify-between gap-2"><div className="min-w-0"><div className="truncate text-sm font-semibold text-white">{s.name}</div><div className="text-[11px] text-[var(--text-muted)]">{s.persona} · {s.channel === 'multi' ? 'Email + LinkedIn' : title(s.channel)} · cap {s.daily_cap}/day</div></div><Badge tone={statusTone(s.status)} dot>{title(s.status)}</Badge></div>
                <div className="mt-3 grid grid-cols-4 gap-2 text-center text-[11px]">
                  {[['Sent', s.sent], ['Replies', s.replied], ['Positive', s.positive_replies], ['Meetings', s.meetings]].map(([l, v]) => <div key={String(l)}><div className="num text-sm font-bold text-white">{num(Number(v))}</div><div className="text-[var(--text-muted)]">{l}</div></div>)}
                </div>
                <div className="mt-2 flex items-center gap-2"><Meter value={s.reply_rate} max={15} height={4} color="var(--series-3)" /><span className="num text-[11px] text-white">{s.reply_rate}%</span></div>
              </button>
            ))}
          </div>

          {active && (
            <Panel title={active.name} subtitle={`ICP: ${active.icp_name || '—'} · compliance ${active.compliance_status}`} action={
              <div className="flex gap-2">
                {active.status === 'active' ? <Button size="sm" variant="outline" onClick={() => setStatus.mutate({ id: active.id, status: 'paused' })}><Pause className="h-3.5 w-3.5" /> Pause</Button>
                  : <Button size="sm" variant="success" onClick={() => setStatus.mutate({ id: active.id, status: 'active' })}><Play className="h-3.5 w-3.5" /> {active.status === 'pending_approval' ? 'Approve & launch' : 'Activate'}</Button>}
              </div>}>
              <div className="relative ml-3 border-l border-white/10 pl-6">
                {active.steps.map((st, i) => (
                  <motion.div key={i} initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className="relative mb-4">
                    <span className="absolute -left-[31px] top-1 flex h-5 w-5 items-center justify-center rounded-full border border-white/10 bg-ink-850">{st.channel === 'linkedin' ? <Link2 className="h-3 w-3 text-cyan-300" /> : <Mail className="h-3 w-3 text-accent-soft" />}</span>
                    <div className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3">
                      <div className="flex items-center gap-2 text-[11px]"><span className="font-mono font-semibold text-accent-soft">Day {st.day}</span><Badge>{title(st.type)}</Badge><span className="text-[var(--text-muted)]">{st.channel}</span></div>
                      {st.subject && <div className="mt-1.5 text-sm font-semibold text-white">{st.subject}</div>}
                      <p className="mt-1 text-xs leading-relaxed text-[var(--text-secondary)]">{st.body}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </Panel>
          )}
        </div>
      )}

      {tab === 'inbox' && (
        <div className="grid gap-4 xl:grid-cols-[1fr_300px]">
          <div className="space-y-2">
            <div className="flex items-center justify-between"><Tabs tabs={[{ key: 'unhandled', label: 'Needs action', count: breakdown?.unhandled }, { key: 'all', label: 'All', count: breakdown?.total }]} value={filter} onChange={setFilter} /><span className="text-xs text-[var(--text-muted)]">{breakdown?.meetings} meetings booked by AI SDR</span></div>
            {replies?.results.map((r, i) => (
              <motion.div key={r.id} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }} className="glass p-4">
                <div className="flex flex-wrap items-center gap-2"><span className="text-sm font-semibold text-white">{r.contact_name}</span><span className="text-xs text-[var(--text-muted)]">{r.contact_title} · {r.company_name}</span>{r.company_tier === 1 && <Badge tone="accent">Tier 1</Badge>}<span className="ml-auto text-[11px] text-[var(--text-muted)]">{relTime(r.received_at)}</span></div>
                <p className="mt-2 rounded-xl bg-ink-900/60 p-3 text-sm italic text-[var(--text-secondary)]">“{r.body}”</p>
                <div className="mt-3 flex flex-wrap items-center gap-2"><Badge tone={CLASS_TONE[r.classification] ?? 'neutral'} dot>{title(r.classification)}</Badge><span className="text-[11px] text-[var(--text-muted)]">{Math.round(r.confidence * 100)}% · Reply Intelligence</span><span className="text-xs text-white">→ {r.next_action}</span>{r.meeting_booked_at && <Badge tone="good">Meeting booked</Badge>}</div>
                {r.sdr_response && <div className="mt-3 rounded-xl border border-accent/20 bg-accent/5 p-3 text-xs"><div className="label mb-1 !text-accent-soft">AI SDR drafted</div><span className="text-white">{r.sdr_response}</span></div>}
                {!r.handled && <div className="mt-3 flex gap-2"><Button size="sm" variant="success" onClick={() => handle.mutate(r.id)}>Approve & send</Button><Button size="sm" variant="ghost">Edit</Button></div>}
              </motion.div>
            ))}
            {replies && replies.results.length === 0 && <div className="glass p-10 text-center text-sm text-[var(--text-muted)]"><Inbox className="mx-auto mb-2 h-6 w-6" />Inbox zero.</div>}
          </div>
          <Panel title="Classification mix" subtitle="Every reply, routed">
            <div className="space-y-2">{breakdown?.by_class.map((b) => <div key={b.classification}><div className="mb-1 flex justify-between text-xs"><span className="text-white">{title(b.classification)}</span><span className="num text-[var(--text-muted)]">{b.count}</span></div><Meter value={b.count} max={Math.max(...breakdown.by_class.map((x) => x.count))} height={4} color={`var(--status-${CLASS_TONE[b.classification] === 'good' ? 'good' : CLASS_TONE[b.classification] === 'bad' ? 'critical' : 'warning'})`} /></div>)}</div>
          </Panel>
        </div>
      )}
    </div>
  )
}
