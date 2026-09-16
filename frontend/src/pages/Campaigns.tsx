import { useState } from 'react'
import { motion } from 'framer-motion'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowDownRight, ArrowUpRight, Image, Pause, Play, ShieldCheck, Sparkles, Trophy, Video } from 'lucide-react'
import { get, post } from '@/lib/api'
import { channelColor, channelLabel, money, num, shortDate } from '@/lib/format'
import { Badge, Button, PageHeader, Panel, Tabs, statusTone } from '@/components/ui'
import { ChannelBars } from '@/components/charts'

type Campaign = { id: number; name: string; channel: string; status: string; daily_budget: string; total_spend: string; impressions: number; clicks: number; leads: number; meetings: number; pipeline_value: string; revenue: string; ctr: number; cac: number; roas: number; creatives_count: number; landing_page_name: string; external_id: string; managed_by_ai: boolean }
type ChannelRow = { channel: string; label: string; campaigns: number; spend: number; leads: number; meetings: number; revenue: number; pipeline: number; daily_budget: number; cac: number; roas: number }
type Creative = { id: number; campaign_name: string; channel: string; kind: string; variant_label: string; hook: string; headline: string; primary_text: string; cta: string; visual_direction: string; gradient_seed: number; audience_label: string; impressions: number; clicks: number; conversions: number; ctr: number; is_winner: boolean; statistical_confidence: number; compliance_status: string; compliance_notes: string[]; active: boolean }
type Allocation = { id: number; date: string; channel: string; previous_daily: string; new_daily: string; reason: string; delta_pct: number; applied: boolean; metrics: Record<string, number> }

const GRAD = ['from-violet-600 to-cyan-500', 'from-orange-500 to-rose-500', 'from-emerald-500 to-cyan-400', 'from-amber-400 to-orange-600', 'from-pink-500 to-violet-600', 'from-sky-500 to-indigo-600', 'from-lime-400 to-emerald-600', 'from-rose-400 to-amber-400']

export function CampaignsPage() {
  const qc = useQueryClient()
  const [tab, setTab] = useState<'campaigns' | 'creatives' | 'buyer'>('campaigns')
  const { data: channels } = useQuery({ queryKey: ['campaigns', 'channels'], queryFn: () => get<ChannelRow[]>('/campaigns/campaigns/channels/') })
  const { data: camps } = useQuery({ queryKey: ['campaigns'], queryFn: () => get<Campaign[]>('/campaigns/campaigns/') })
  const { data: creatives } = useQuery({ queryKey: ['creatives'], queryFn: () => get<Creative[]>('/campaigns/creatives/') })
  const { data: allocs } = useQuery({ queryKey: ['allocations'], queryFn: () => get<Allocation[]>('/campaigns/allocations/') })
  const inval = () => { qc.invalidateQueries({ queryKey: ['campaigns'] }); qc.invalidateQueries({ queryKey: ['creatives'] }); qc.invalidateQueries({ queryKey: ['allocations'] }); qc.invalidateQueries({ queryKey: ['decisions'] }); qc.invalidateQueries({ queryKey: ['activity'] }) }
  const optimize = useMutation({ mutationFn: () => post('/campaigns/campaigns/optimize/', {}), onSuccess: inval })
  const genCreative = useMutation({ mutationFn: () => post('/campaigns/creatives/generate/', {}), onSuccess: inval })
  const setStatus = useMutation({ mutationFn: ({ id, status }: { id: number; status: string }) => post(`/campaigns/campaigns/${id}/set_status/`, { status }), onSuccess: inval })
  const compliance = useMutation({ mutationFn: ({ id, status }: { id: number; status: string }) => post(`/campaigns/creatives/${id}/compliance/`, { status }), onSuccess: inval })
  const totalSpend = channels?.reduce((a, c) => a + c.spend, 0) ?? 0

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Phases 8–9 · Paid Media → Creative → Testing → Autonomous Media Buyer" title={<>Every rupee goes where <span className="gradient-text">revenue says it should</span></>}
        description="Campaigns across Meta, Google, YouTube, LinkedIn and TikTok. Creative Director briefs → Video Agent variants → statistical winners → budget reallocated on CAC, ROAS, LTV and margin, not clicks."
        actions={<><Tabs tabs={[{ key: 'campaigns', label: 'Campaigns', count: camps?.length }, { key: 'creatives', label: 'Creative lab', count: creatives?.length }, { key: 'buyer', label: 'Media buyer log', count: allocs?.length }]} value={tab} onChange={setTab} /><Button variant="outline" onClick={() => genCreative.mutate()} loading={genCreative.isPending}><Image className="h-4 w-4" /> Generate creative</Button><Button onClick={() => optimize.mutate()} loading={optimize.isPending}><Sparkles className="h-4 w-4" /> Optimize now</Button></>} />

      <div className="grid gap-4 xl:grid-cols-[1fr_1fr]">
        <Panel title="Channel scorecard" subtitle="Sorted by CAC — the Media Buyer's decision input">
          <table className="w-full text-xs">
            <thead><tr className="text-left text-[10px] uppercase tracking-wider text-[var(--text-muted)]"><th className="py-2">Channel</th><th className="py-2 text-right">Spend</th><th className="py-2 text-right">Leads</th><th className="py-2 text-right">CAC</th><th className="py-2 text-right">ROAS</th><th className="py-2 text-right">Pipeline</th></tr></thead>
            <tbody>{channels?.map((c) => (
              <tr key={c.channel} className="border-t border-white/[0.05]">
                <td className="py-2.5"><span className="flex items-center gap-2 font-semibold text-white"><span className="h-2 w-2 rounded-full" style={{ background: channelColor(c.channel) }} />{c.label}</span></td>
                <td className="num py-2.5 text-right text-white">{money(c.spend, 'INR')}<div className="text-[10px] text-[var(--text-muted)]">{totalSpend ? Math.round((c.spend / totalSpend) * 100) : 0}%</div></td>
                <td className="num py-2.5 text-right text-white">{num(c.leads)}</td>
                <td className="num py-2.5 text-right"><span className={c.cac && c.cac < 2500 ? 'text-emerald-300' : c.cac > 4000 ? 'text-rose-300' : 'text-white'}>{c.cac ? money(c.cac, 'INR', 0) : '—'}</span></td>
                <td className="num py-2.5 text-right text-white">{c.roas ? `${c.roas.toFixed(1)}x` : '—'}</td>
                <td className="num py-2.5 text-right text-white">{money(c.pipeline, 'INR')}</td>
              </tr>))}</tbody>
          </table>
        </Panel>
        <Panel title="Cost per lead by channel" subtitle="Lower is better"><ChannelBars data={(channels ?? []).map((c) => ({ channel: c.channel, cpl: c.leads ? Math.round(c.spend / c.leads) : 0 }))} metric="cpl" currency="INR" label="CPL" height={230} /></Panel>
      </div>

      {tab === 'campaigns' && (
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {camps?.map((c, i) => (
            <motion.div key={c.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }} className="glass p-5">
              <div className="flex items-start justify-between gap-2"><div><div className="flex items-center gap-2"><span className="h-2 w-2 rounded-full" style={{ background: channelColor(c.channel) }} /><span className="label">{channelLabel(c.channel)}</span></div><h3 className="mt-1 text-sm font-bold text-white">{c.name}</h3><div className="text-[11px] text-[var(--text-muted)]">{c.external_id} · LP: {c.landing_page_name || '—'}</div></div><Badge tone={statusTone(c.status)} dot>{c.status.replace('_', ' ')}</Badge></div>
              <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                <div className="rounded-xl bg-white/[0.03] p-2"><div className="text-base font-bold text-white">{money(c.daily_budget, 'INR', 0)}</div><div className="text-[10px] text-[var(--text-muted)]">daily budget</div></div>
                <div className="rounded-xl bg-white/[0.03] p-2"><div className="text-base font-bold text-white">{c.cac ? money(c.cac, 'INR', 0) : '—'}</div><div className="text-[10px] text-[var(--text-muted)]">CAC</div></div>
                <div className="rounded-xl bg-white/[0.03] p-2"><div className="text-base font-bold text-white">{c.roas ? `${c.roas}x` : '—'}</div><div className="text-[10px] text-[var(--text-muted)]">ROAS</div></div>
              </div>
              <div className="mt-3 grid grid-cols-4 gap-1 text-center text-[11px] text-[var(--text-muted)]">
                <div><div className="num text-white">{num(c.impressions)}</div>impr</div><div><div className="num text-white">{c.ctr}%</div>CTR</div><div><div className="num text-white">{num(c.leads)}</div>leads</div><div><div className="num text-white">{num(c.meetings)}</div>meetings</div>
              </div>
              <div className="mt-4 flex items-center justify-between"><span className="text-[11px] text-[var(--text-muted)]">{c.creatives_count} creatives · {c.managed_by_ai ? 'AI-managed' : 'manual'}</span>
                {c.status === 'active' ? <Button size="sm" variant="ghost" onClick={() => setStatus.mutate({ id: c.id, status: 'paused' })}><Pause className="h-3.5 w-3.5" /> Pause</Button> : <Button size="sm" variant="success" onClick={() => setStatus.mutate({ id: c.id, status: 'active' })}><Play className="h-3.5 w-3.5" /> {c.status === 'pending_approval' ? 'Approve' : 'Resume'}</Button>}</div>
            </motion.div>
          ))}
        </div>
      )}

      {tab === 'creatives' && (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {creatives?.map((cr, i) => (
            <motion.div key={cr.id} initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.02 }} className={`glass overflow-hidden ${cr.is_winner ? 'ring-1 ring-amber-400/50' : ''}`}>
              <div className={`relative flex aspect-[4/3] items-end bg-gradient-to-br p-4 ${GRAD[(cr.gradient_seed - 1) % GRAD.length]}`}>
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(255,255,255,0.25),transparent_50%)]" />
                <div className="absolute left-3 top-3 flex gap-1.5"><Badge tone="neutral" className="!bg-black/40 !text-white">{cr.kind === 'video' ? <Video className="h-3 w-3" /> : <Image className="h-3 w-3" />} {cr.kind}</Badge><Badge tone="neutral" className="!bg-black/40 !text-white">{cr.variant_label}</Badge></div>
                {cr.is_winner && <span className="absolute right-3 top-3 rounded-full bg-amber-400 p-1.5 text-ink-950"><Trophy className="h-3 w-3" /></span>}
                <div className="relative text-base font-extrabold leading-tight text-white drop-shadow">{cr.headline}</div>
              </div>
              <div className="p-3">
                <div className="text-[11px] text-[var(--text-muted)]">{cr.campaign_name} · {cr.audience_label}</div>
                <p className="mt-1 line-clamp-2 text-xs text-[var(--text-secondary)]">{cr.primary_text}</p>
                <div className="mt-2 flex items-center justify-between text-[11px]"><span className="rounded-md bg-white/[0.06] px-1.5 py-0.5 text-white">{cr.cta}</span><span className="num text-[var(--text-muted)]">CTR <span className="text-white">{cr.ctr}%</span> · {num(cr.conversions)} conv</span></div>
                <div className="mt-2 flex items-center justify-between"><Badge tone={statusTone(cr.compliance_status)}><ShieldCheck className="h-3 w-3" /> {cr.compliance_status}</Badge>{cr.compliance_status === 'flagged' && <div className="flex gap-1"><button onClick={() => compliance.mutate({ id: cr.id, status: 'passed' })} className="text-[11px] text-emerald-300 hover:underline">Approve</button><button onClick={() => compliance.mutate({ id: cr.id, status: 'rejected' })} className="text-[11px] text-rose-300 hover:underline">Reject</button></div>}</div>
                {cr.compliance_notes?.length > 0 && <div className="mt-1 text-[10px] text-amber-300">{cr.compliance_notes[0]}</div>}
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {tab === 'buyer' && (
        <Panel title="Autonomous Media Buyer · reallocation log" subtitle="Where should the next rupee go? Based on CAC, ROAS, LTV, margin, pipeline and real revenue.">
          <div className="space-y-2">{allocs?.map((a) => (
            <div key={a.id} className="flex flex-wrap items-center gap-4 rounded-xl border border-white/[0.06] bg-white/[0.02] p-3">
              <div className="w-16 font-mono text-[11px] text-[var(--text-muted)]">{shortDate(a.date)}</div>
              <div className="flex w-32 items-center gap-2 text-sm font-semibold text-white"><span className="h-2 w-2 rounded-full" style={{ background: channelColor(a.channel) }} />{channelLabel(a.channel)}</div>
              <div className={`flex items-center gap-1 font-mono text-sm font-bold ${a.delta_pct >= 0 ? 'text-emerald-300' : 'text-rose-300'}`}>{a.delta_pct >= 0 ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}{a.delta_pct > 0 ? '+' : ''}{a.delta_pct}%</div>
              <div className="num text-xs text-[var(--text-secondary)]">{money(a.previous_daily, 'INR', 0)} → <span className="text-white">{money(a.new_daily, 'INR', 0)}</span>/day</div>
              <div className="min-w-0 flex-1 text-xs text-[var(--text-secondary)]">{a.reason}</div>
              <Badge tone={a.applied ? 'good' : 'warn'}>{a.applied ? 'applied' : 'pending'}</Badge>
            </div>))}</div>
        </Panel>
      )}
    </div>
  )
}
