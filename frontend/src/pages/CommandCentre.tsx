import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Bot, Sparkles } from 'lucide-react'
import { get, type Paginated } from '@/lib/api'
import { channelColor, channelLabel, explainOf, money, num, pct, relTime } from '@/lib/format'
import { Badge, Button, Callout, Disclosure, Meter, PageHeader, Panel, Skeleton, StatTile, Tabs, statusTone } from '@/components/ui'
import { ChannelBars, Funnel, Legend, RevenueSpendChart } from '@/components/charts'
import { DecisionCard, type Decision } from '@/components/DecisionCard'
import { openCommandBar } from '@/components/layout/CommandBar'
import { useAuth } from '@/store/auth'

type Kpi = { value: number; delta_pct: number }
type Dashboard = {
  window_days: number; currency: string
  goal: { revenue_goal: number; attained: number; pct: number; pipeline_coverage: number }
  kpis: Record<string, Kpi>
  timeseries: { date: string; spend: number; revenue: number; pipeline: number; leads: number; meetings: number }[]
  channels: { channel: string; spend: number; leads: number; meetings: number; customers: number; revenue: number; pipeline: number; cac: number; cpl: number; roas: number }[]
  funnel: { stage: string; count: number }[]
  counts: Record<string, number>
}
type Activity = { id: number; agent_name: string; agent_key: string; kind: string; message: string; created_at: string }
type Agent = { id: number; key: string; name: string; status: string; last_summary: string; health_score: number }

const STAGE_LABEL: Record<string, string> = {
  visitor: 'Visited the site', lead: 'Gave us their details', mql: 'Showed interest',
  sql: 'Sales-ready', opportunity: 'In a deal', customer: 'Bought', repeat: 'Bought again', advocate: 'Refers us',
}

export function CommandCentre() {
  const user = useAuth((s) => s.user)
  const [days, setDays] = useState<'7' | '30' | '90'>('30')
  const [feed, setFeed] = useState<'pending' | 'all'>('pending')

  const { data: d, isLoading } = useQuery({ queryKey: ['dashboard', days], queryFn: () => get<Dashboard>('/analytics/dashboard/', { days }) })
  const { data: decisions } = useQuery({
    queryKey: ['decisions', feed],
    queryFn: () => get<Paginated<Decision>>('/agents/decisions/', feed === 'pending' ? { status: 'pending', page_size: 12 } : { page_size: 12 }),
    refetchInterval: 15_000,
  })
  const { data: activity } = useQuery({ queryKey: ['activity'], queryFn: () => get<Paginated<Activity>>('/agents/activity/', { page_size: 12 }), refetchInterval: 12_000 })
  const { data: agents } = useQuery({ queryKey: ['agents'], queryFn: () => get<Agent[]>('/agents/agents/'), refetchInterval: 20_000 })

  const cur = d?.currency ?? 'INR'
  const k = d?.kpis
  const spark = (key: 'revenue' | 'spend' | 'leads' | 'meetings') => d?.timeseries.slice(-14).map((t) => t[key]) ?? []
  const working = agents?.filter((a) => a.status === 'running') ?? []
  const period = days === '7' ? 'the last 7 days' : days === '30' ? 'the last 30 days' : 'the last 90 days'
  const best = d?.channels.find((c) => c.cac > 0)
  const needsYou = d?.counts.pending_decisions ?? 0

  return (
    <div className="space-y-6">
      <PageHeader
        title={<>Hi {user?.full_name?.split(' ')[0] || 'there'} — here's where you stand</>}
        description={`Everything your AI marketing team did for ${user?.current_workspace?.name ?? 'your business'} in ${period}.`}
        actions={<>
          <Tabs tabs={[{ key: '7', label: '7 days' }, { key: '30', label: '30 days' }, { key: '90', label: '90 days' }]} value={days} onChange={setDays} />
          <Button onClick={openCommandBar}><Sparkles className="h-4 w-4" /> Ask the AI to do something</Button>
        </>} />

      {/* One sentence, before any number. */}
      {d && k && (
        <Callout>
          In {period} you spent <b className="text-white">{money(k.spend.value, cur)}</b> and brought in{' '}
          <b className="text-white">{money(k.revenue.value, cur)}</b> — that's{' '}
          <b className="text-white">{k.roas.value.toFixed(1)}x</b> back on every rupee.
          You booked <b className="text-white">{num(k.meetings.value)} meetings</b> and won{' '}
          <b className="text-white">{num(k.customers.value)} customers</b>
          {best && <> at about <b className="text-white">{money(best.cac, cur, 0)}</b> each, cheapest via {channelLabel(best.channel)}</>}.
          {needsYou > 0
            ? <> <b className="text-accent-soft">{needsYou} decisions are waiting for you</b> below.</>
            : <> Nothing needs your approval right now.</>}
        </Callout>
      )}

      {/* Four headline numbers. The rest are one click away. */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {isLoading || !k ? Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-[112px]" />) : (
          <>
            <StatTile big label="Money made" value={money(k.revenue.value, cur)} delta={k.revenue.delta_pct}
              accent="var(--series-1)" spark={spark('revenue')} explain={explainOf('revenue')} />
            <StatTile big label="Money spent" value={money(k.spend.value, cur)} delta={k.spend.delta_pct} upIsGood={false}
              accent="var(--series-2)" spark={spark('spend')} explain={explainOf('spend')} />
            <StatTile big label="Cost per customer" value={money(k.cac.value, cur, 0)} delta={k.cac.delta_pct} upIsGood={false}
              accent="var(--series-4)" explain={explainOf('cac')} />
            <StatTile big label="Meetings booked" value={num(k.meetings.value)} delta={k.meetings.delta_pct}
              accent="var(--series-3)" spark={spark('meetings')} explain={explainOf('meetings')} />
          </>
        )}
      </div>

      {k && (
        <Disclosure label="Show more numbers">
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <StatTile label="Deals in progress" value={money(k.pipeline.value, cur)} delta={k.pipeline.delta_pct} accent="var(--series-6)" explain={explainOf('pipeline')} />
            <StatTile label="Return on ad spend" value={`${k.roas.value.toFixed(1)}x`} delta={k.roas.delta_pct} accent="var(--series-3)" explain={explainOf('roas')} />
            <StatTile label="Ready-to-talk leads" value={num(k.qualified_leads.value)} delta={k.qualified_leads.delta_pct} accent="var(--series-5)" spark={spark('leads')} explain={explainOf('qualified_leads')} />
            <StatTile label="New customers" value={num(k.customers.value)} delta={k.customers.delta_pct} accent="var(--series-7)" explain={explainOf('customers')} />
          </div>
        </Disclosure>
      )}

      <div className="grid gap-4 xl:grid-cols-[1.6fr_1fr]">
        <Panel title="Money in vs. money out" subtitle={`Day by day over ${period}`}
          action={<Legend items={[{ label: 'Made', color: 'var(--series-1)' }, { label: 'Spent', color: 'var(--series-2)' }]} />}>
          {d ? <RevenueSpendChart data={d.timeseries} currency={cur} /> : <Skeleton className="h-[260px]" />}
        </Panel>

        <Panel className="flex flex-col" title="Progress to your goal" subtitle="Revenue target for the year">
          {d ? (
            <>
              <div className="text-4xl font-extrabold tracking-tight text-white">{pct(d.goal.pct, 0)}</div>
              <div className="mt-1 text-xs text-[var(--text-muted)]">{money(d.goal.attained, cur)} of {money(d.goal.revenue_goal, cur)}</div>
              <Meter value={d.goal.pct} className="mt-4" height={10} color="linear-gradient(90deg, var(--series-1), #22d3ee)" />
              <div className="mt-5 grid grid-cols-2 gap-3">
                {[
                  ['Deals in progress', `${d.goal.pipeline_coverage}x goal`, explainOf('pipeline')],
                  ['Best-fit accounts', String(d.counts.tier1_accounts), 'Companies that match your target customer best.'],
                  ['Emails running', String(d.counts.active_sequences), 'Outreach sequences currently sending.'],
                  ['Replies to handle', String(d.counts.unhandled_replies), 'People who replied and are waiting on an answer.'],
                ].map(([label, value]) => (
                  <div key={label} className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3">
                    <div className="label">{label}</div>
                    <div className="mt-1 text-xl font-bold text-white">{value}</div>
                  </div>
                ))}
              </div>
            </>
          ) : <Skeleton className="h-[260px]" />}
        </Panel>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.35fr_1fr]">
        <div className="space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h3 className="text-sm font-semibold text-white">What the AI wants to do next</h3>
              <p className="text-xs text-[var(--text-muted)]">Approve it, skip it, or ask why.</p>
            </div>
            <Tabs tabs={[{ key: 'pending', label: 'Waiting on you', count: needsYou }, { key: 'all', label: 'Everything' }]} value={feed} onChange={setFeed} />
          </div>
          <AnimatePresence mode="popLayout">
            {decisions?.results.map((dec) => <DecisionCard key={dec.id} d={dec} />)}
          </AnimatePresence>
          {decisions && decisions.results.length === 0 && (
            <div className="glass p-8 text-center text-sm text-[var(--text-muted)]">
              Nothing waiting. The AI will put its next suggestion here.
            </div>
          )}
        </div>

        <div className="space-y-4">
          <Panel title="Where your money works hardest" subtitle="Cost to win one customer, by channel">
            {d ? <ChannelBars data={d.channels} metric="cac" currency={cur} label="Cost per customer" height={200} /> : <Skeleton className="h-[200px]" />}
            {d && (
              <div className="mt-2 grid grid-cols-2 gap-2 text-[11px] text-[var(--text-secondary)]">
                {d.channels.slice(0, 4).map((c) => (
                  <div key={c.channel} className="flex items-center justify-between rounded-lg border border-white/[0.05] px-2 py-1.5">
                    <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full" style={{ background: channelColor(c.channel) }} />{channelLabel(c.channel)}</span>
                    <span className="num text-white">{c.roas.toFixed(1)}x back</span>
                  </div>
                ))}
              </div>
            )}
          </Panel>

          <Panel title="Your AI team right now" subtitle={`${working.length} working · ${agents?.length ?? 0} on the team`}
            action={<Bot className="h-4 w-4 text-accent-soft" />}>
            <div className="space-y-2">
              {(agents ?? []).filter((a) => a.status === 'running').concat((agents ?? []).filter((a) => a.status !== 'running').slice(0, 3)).slice(0, 5).map((a) => (
                <div key={a.id} className="flex items-start gap-3 rounded-xl border border-white/[0.05] bg-white/[0.02] p-2.5">
                  <span className="relative mt-1 flex h-2 w-2">
                    {a.status === 'running' && <span className="absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-70 animate-pulseRing" />}
                    <span className={`relative inline-flex h-2 w-2 rounded-full ${a.status === 'running' ? 'bg-cyan-400' : a.status === 'error' ? 'bg-rose-400' : 'bg-emerald-400'}`} />
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-semibold text-white">{a.name}</span>
                      <Badge tone={statusTone(a.status)}>{a.status === 'running' ? 'working' : a.status}</Badge>
                    </div>
                    <p className="mt-0.5 line-clamp-2 text-[11px] leading-relaxed text-[var(--text-muted)]">{a.last_summary}</p>
                  </div>
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Your customer journey" subtitle="How many people are at each step">
            {d ? <Funnel data={d.funnel.map((f) => ({ ...f, stage: STAGE_LABEL[f.stage] ?? f.stage }))} /> : <Skeleton className="h-[180px]" />}
          </Panel>
        </div>
      </div>

      <Panel title="Recent activity" subtitle="What the agents have been doing">
        <div className="grid gap-x-8 gap-y-1 md:grid-cols-2">
          {activity?.results.map((e, i) => (
            <motion.div key={e.id} initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.02 }}
              className="flex items-start gap-3 border-b border-white/[0.04] py-2 last:border-0">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
              <div className="min-w-0 flex-1">
                <div className="truncate text-xs text-white">{e.message}</div>
                <div className="text-[11px] text-[var(--text-muted)]">{e.agent_name} · {relTime(e.created_at)}</div>
              </div>
            </motion.div>
          ))}
        </div>
      </Panel>
    </div>
  )
}
