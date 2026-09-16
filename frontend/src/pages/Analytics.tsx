import { useState } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Route } from 'lucide-react'
import { get } from '@/lib/api'
import { channelColor, channelLabel, dayLabel, money, num, pct, shortDate } from '@/lib/format'
import { Meter, PageHeader, Panel, Skeleton, StatTile, Tabs } from '@/components/ui'
import { ChannelBars, Legend, MultiLine } from '@/components/charts'

type Attribution = { total_revenue: number; table: { channel: string; first_touch: number; last_touch: number; multi_touch: number; share: number }[]; journeys: { company: string; amount: number; closed_at: string; days_to_close: number; path: { channel: string; type: string }[] }[]; avg_days_to_close: number; attributed_share: number }
type RevInt = { revenue: number; pipeline: number; spend: number; cac: number; roas: number; customers: number; leads: number; meetings: number; gross_margin_pct: number; ltv: number; ltv_to_cac: number; payback_months: number; roi_pct: number; window_days: number }
type Dash = { currency: string; timeseries: { date: string; leads: number; meetings: number; pipeline: number }[]; channels: { channel: string; revenue: number; spend: number; roas: number; pipeline: number }[] }

export function AnalyticsPage() {
  const [model, setModel] = useState<'multi_touch' | 'first_touch' | 'last_touch'>('multi_touch')
  const { data: attr } = useQuery({ queryKey: ['attribution'], queryFn: () => get<Attribution>('/analytics/attribution/') })
  const { data: ri } = useQuery({ queryKey: ['revenue-intelligence'], queryFn: () => get<RevInt>('/analytics/revenue-intelligence/', { days: 90 }) })
  const { data: dash } = useQuery({ queryKey: ['dashboard', '90'], queryFn: () => get<Dash>('/analytics/dashboard/', { days: 90 }) })
  const cur = dash?.currency ?? 'INR'
  const series = dash?.timeseries.map((t) => ({ label: dayLabel(t.date), leads: t.leads, meetings: t.meetings })) ?? []

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Phase 12 · Analytics → Attribution → Revenue Intelligence" title={<>Not “how many clicks?” — <span className="gradient-text">how much revenue?</span></>}
        description="Ad → Landing page → Lead → Sales call → Opportunity → Customer → revenue, traced back to the originating activity. One identity graph, no per-channel silos." />

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-8">
        {ri ? <>
          <StatTile label="Revenue (90d)" value={money(ri.revenue, cur)} accent="var(--series-1)" />
          <StatTile label="Pipeline" value={money(ri.pipeline, cur)} accent="var(--series-6)" />
          <StatTile label="CAC" value={money(ri.cac, cur, 0)} accent="var(--series-4)" />
          <StatTile label="LTV" value={money(ri.ltv, cur)} accent="var(--series-3)" />
          <StatTile label="LTV : CAC" value={`${ri.ltv_to_cac}x`} hint={ri.ltv_to_cac >= 3 ? 'healthy (>3x)' : 'below 3x'} accent="var(--series-3)" />
          <StatTile label="Payback" value={`${ri.payback_months} mo`} accent="var(--series-2)" />
          <StatTile label="Gross margin" value={pct(ri.gross_margin_pct, 0)} accent="var(--series-5)" />
          <StatTile label="Marketing ROI" value={pct(ri.roi_pct, 0)} accent="var(--series-7)" />
        </> : Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-24" />)}
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.3fr_1fr]">
        <Panel title="Revenue attribution by channel" subtitle={`${Math.round((attr?.attributed_share ?? 0) * 100)}% of closed revenue attributed with confidence · avg ${attr?.avg_days_to_close ?? 0} days to close`}
          action={<Tabs tabs={[{ key: 'multi_touch', label: 'Multi-touch' }, { key: 'first_touch', label: 'First' }, { key: 'last_touch', label: 'Last' }]} value={model} onChange={setModel} />}>
          {attr ? <ChannelBars data={attr.table.map((r) => ({ channel: r.channel, value: r[model] }))} metric="value" currency={cur} label="Revenue" height={240} /> : <Skeleton className="h-60" />}
          {attr && <div className="mt-3 grid grid-cols-2 gap-2 md:grid-cols-3">{attr.table.map((r) => <div key={r.channel} className="rounded-lg border border-white/[0.05] px-2.5 py-2 text-[11px]"><div className="flex items-center justify-between"><span className="flex items-center gap-1.5 text-white"><span className="h-2 w-2 rounded-full" style={{ background: channelColor(r.channel) }} />{channelLabel(r.channel)}</span><span className="num text-[var(--text-muted)]">{r.share}%</span></div><Meter value={r.share} height={3} color={channelColor(r.channel)} className="mt-1.5" /></div>)}</div>}
        </Panel>
        <Panel title="Leads & meetings" subtitle="Daily, last 90 days" action={<Legend items={[{ label: 'Leads', color: 'var(--series-1)' }, { label: 'Meetings', color: 'var(--series-3)' }]} />}>
          {dash ? <MultiLine data={series} keys={[{ key: 'leads', label: 'Leads', color: 'var(--series-1)' }, { key: 'meetings', label: 'Meetings', color: 'var(--series-3)' }]} height={240} /> : <Skeleton className="h-60" />}
        </Panel>
      </div>

      <Panel title="Won journeys" subtitle="Every touch from first click to closed revenue" action={<Route className="h-4 w-4 text-accent-soft" />}>
        <div className="space-y-2">
          {attr?.journeys.map((j, i) => (
            <motion.div key={i} initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.04 }} className="flex flex-wrap items-center gap-3 rounded-xl border border-white/[0.06] bg-white/[0.02] p-3">
              <div className="w-48 min-w-0"><div className="truncate text-sm font-semibold text-white">{j.company}</div><div className="text-[11px] text-[var(--text-muted)]">closed {shortDate(j.closed_at)} · {j.days_to_close}d cycle</div></div>
              <div className="flex flex-1 flex-wrap items-center gap-1">
                {j.path.map((t, k) => <span key={k} className="flex items-center gap-1"><span className="flex items-center gap-1.5 rounded-lg border border-white/[0.06] bg-ink-900/60 px-2 py-1 text-[11px]"><span className="h-1.5 w-1.5 rounded-full" style={{ background: channelColor(t.channel) }} /><span className="text-white">{channelLabel(t.channel)}</span><span className="text-[var(--text-muted)]">{t.type.replace('_', ' ')}</span></span>{k < j.path.length - 1 && <span className="text-[var(--text-muted)]">→</span>}</span>)}
                <span className="text-[var(--text-muted)]">→</span><span className="rounded-lg bg-emerald-500/15 px-2 py-1 text-[11px] font-semibold text-emerald-300">Won</span>
              </div>
              <div className="num text-sm font-bold text-white">{money(j.amount, cur)}</div>
            </motion.div>
          ))}
        </div>
      </Panel>

      <Panel title="Channel ROAS" subtitle="Revenue ÷ spend, last 90 days">
        {dash ? <ChannelBars data={dash.channels.map((c) => ({ channel: c.channel, roas: c.roas }))} metric="roas" label="ROAS" height={200} /> : <Skeleton className="h-48" />}
        <div className="mt-2 text-[11px] text-[var(--text-muted)]">{num(ri?.customers)} customers · {num(ri?.meetings)} meetings · {num(ri?.leads)} leads in window</div>
      </Panel>
    </div>
  )
}
