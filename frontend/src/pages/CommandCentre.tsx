import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { ArrowDownRight, ArrowUpRight, Sparkles, X } from 'lucide-react'
import { get, type Paginated } from '@/lib/api'
import { channelColor, channelLabel, money, num, relTime, signedPct } from '@/lib/format'
import { Button, CountUp, Disclosure, Explain, PageHeader, Panel, Ring, Skeleton, Tabs } from '@/components/ui'
import { ChannelBars, Funnel, Legend, RevenueSpendChart } from '@/components/charts'
import { DecisionCard, type Decision } from '@/components/DecisionCard'
import { SystemLoop, type LoopStage } from '@/components/SystemLoop'
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
type Activity = { id: number; agent_name: string; kind: string; message: string; created_at: string }

const STAGE_LABEL: Record<string, string> = {
  visitor: 'Visited the site', lead: 'Gave us their details', mql: 'Showed interest',
  sql: 'Sales-ready', opportunity: 'In a deal', customer: 'Bought', repeat: 'Bought again', advocate: 'Refers us',
}

/* One-time, dismissible, three sentences: the whole product. */
function HowItWorks() {
  const KEY = 'gtm.howitworks.dismissed'
  const [show, setShow] = useState(false)
  useEffect(() => { try { setShow(!localStorage.getItem(KEY)) } catch { setShow(true) } }, [])
  if (!show) return null
  const steps = [
    ['1', 'The AI finds your best-fit customers and reaches out', 'emails, ads, posts and landing pages — written, sent and measured for you'],
    ['2', 'It works out what actually made money', 'and moves budget and effort towards it, automatically'],
    ['3', 'You only step in for the big calls', 'approve or skip them below — everything else just runs'],
  ]
  return (
    <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="glass relative grid gap-3 p-4 md:grid-cols-3">
      <button onClick={() => { try { localStorage.setItem(KEY, '1') } catch { /* noop */ } setShow(false) }}
        className="absolute right-3 top-3 rounded-lg p-1 text-[var(--text-muted)] hover:bg-white/5 hover:text-white" aria-label="Dismiss">
        <X className="h-3.5 w-3.5" />
      </button>
      {steps.map(([n, h, s]) => (
        <div key={n} className="flex gap-3 pr-4">
          <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-accent to-accent-cyan text-xs font-extrabold text-ink-950">{n}</span>
          <div><div className="text-[13px] font-semibold text-white">{h}</div><div className="text-[11.5px] leading-snug text-[var(--text-muted)]">{s}</div></div>
        </div>
      ))}
    </motion.div>
  )
}

export function CommandCentre() {
  const user = useAuth((s) => s.user)
  const [days, setDays] = useState<'7' | '30' | '90'>('30')
  const [feed, setFeed] = useState<'pending' | 'all'>('pending')

  const { data: d } = useQuery({ queryKey: ['dashboard', days], queryFn: () => get<Dashboard>('/analytics/dashboard/', { days }) })
  const { data: decisions } = useQuery({
    queryKey: ['decisions', feed],
    queryFn: () => get<Paginated<Decision>>('/agents/decisions/', feed === 'pending' ? { status: 'pending', page_size: 10 } : { page_size: 10 }),
    refetchInterval: 15_000,
  })
  const { data: activity } = useQuery({ queryKey: ['activity'], queryFn: () => get<Paginated<Activity>>('/agents/activity/', { page_size: 14 }), refetchInterval: 12_000 })

  const cur = d?.currency ?? 'INR'
  const k = d?.kpis
  const c = d?.counts ?? {}
  const period = days === '7' ? 'the last 7 days' : days === '30' ? 'the last 30 days' : 'the last 90 days'
  const cheapest = d?.channels.find((x) => x.cac > 0)
  const needsYou = c.pending_decisions ?? 0
  const first = user?.full_name?.split(' ')[0] || 'there'
  const revDelta = k?.revenue.delta_pct ?? 0

  const stages: LoopStage[] = d ? [
    { key: 'find', icon: 'search', label: 'Find customers', sub: `${num(c.companies_total)} companies · best fit`, value: c.tier1_accounts ?? 0, to: '/prospects', color: 'var(--series-1)' },
    { key: 'reach', icon: 'megaphone', label: 'Reach out', sub: 'emails + ads running', value: (c.active_sequences ?? 0) + (c.active_campaigns ?? 0), to: '/outbound', color: 'var(--series-2)' },
    { key: 'meet', icon: 'handshake', label: 'Get meetings', sub: `booked in ${period}`, value: k?.meetings.value ?? 0, to: '/outbound', color: 'var(--series-3)' },
    { key: 'win', icon: 'trophy', label: 'Win deals', sub: `${money(k?.revenue.value ?? 0, cur)} made`, value: k?.customers.value ?? 0, to: '/analytics', color: 'var(--series-4)' },
    { key: 'learn', icon: 'brain', label: 'Learn', sub: `${c.running_experiments ?? 0} tests running`, value: c.memory_insights ?? 0, to: '/experiments', color: 'var(--series-6)' },
    { key: 'you', icon: 'shield', label: 'You decide', sub: 'waiting for your OK', value: needsYou, to: '/', color: 'var(--series-5)', hot: needsYou > 0 },
  ] : []

  return (
    <div className="space-y-6">
      <PageHeader
        title={<>Hi {first} — here's where you stand</>}
        description={`${user?.current_workspace?.name ?? 'Your business'} · ${period}`}
        actions={<>
          <Tabs tabs={[{ key: '7', label: '7 days' }, { key: '30', label: '30 days' }, { key: '90', label: '90 days' }]} value={days} onChange={setDays} />
          <Button onClick={openCommandBar}><Sparkles className="h-4 w-4" /> Tell the AI what you want</Button>
        </>} />

      {/* ------------------------------------------------ HERO: one number, one ring, one sentence */}
      {d && k ? (
        <motion.section initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
          className="glass-hero grid gap-8 p-7 md:grid-cols-[1.5fr_1fr] md:p-9">
          <div className="relative">
            <div className="label flex items-center gap-1.5">Money made · {period}<Explain text="Revenue from deals that actually closed in this period." /></div>
            <div className="display-num mt-3 text-[56px] text-white md:text-[76px]">
              <CountUp value={k.revenue.value} format={(n) => money(n, cur)} duration={1800} />
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-3 text-sm">
              <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-bold ${revDelta >= 0 ? 'bg-emerald-500/15 text-emerald-300' : 'bg-rose-500/15 text-rose-300'}`}>
                {revDelta >= 0 ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}{signedPct(revDelta)}
              </span>
              <span className="text-[var(--text-muted)]">vs the {days} days before</span>
            </div>
            <p className="mt-5 max-w-xl text-[15px] leading-relaxed text-[var(--text-secondary)]">
              You spent <b className="text-white">{money(k.spend.value, cur)}</b> to make it — <b className="text-white">{k.roas.value.toFixed(1)}x</b> back on every rupee.
              That's <b className="text-white">{num(k.customers.value)} new customers</b>
              {cheapest && <> at about <b className="text-white">{money(cheapest.cac, cur, 0)}</b> each, cheapest via {channelLabel(cheapest.channel)}</>}.
              {needsYou > 0
                ? <> <b className="text-accent-soft">{needsYou} decisions need you</b> — they're just below.</>
                : <> Nothing needs your approval right now.</>}
            </p>
          </div>

          <div className="flex flex-col items-center justify-center gap-5 md:items-end">
            <Ring value={d.goal.pct} size={188} stroke={13}>
              <div className="display-num text-4xl text-white"><CountUp value={d.goal.pct} format={(n) => `${Math.round(n)}%`} /></div>
              <div className="mt-1 text-[11px] uppercase tracking-wider text-[var(--text-muted)]">of your goal</div>
              <div className="text-[11px] text-[var(--text-secondary)]">{money(d.goal.revenue_goal, cur)} this year</div>
            </Ring>
            <div className="grid w-full grid-cols-3 gap-2 md:max-w-xs">
              {[
                ['Spent', k.spend.value, (n: number) => money(n, cur)],
                ['Per customer', k.cac.value, (n: number) => money(n, cur, 0)],
                ['Meetings', k.meetings.value, (n: number) => num(n)],
              ].map(([l, v, f]) => (
                <div key={l as string} className="rounded-xl border border-white/[0.08] bg-ink-950/40 px-3 py-2 text-center">
                  <div className="text-base font-bold text-white"><CountUp value={v as number} format={f as (n: number) => string} /></div>
                  <div className="text-[10px] uppercase tracking-wider text-[var(--text-muted)]">{l as string}</div>
                </div>
              ))}
            </div>
          </div>
        </motion.section>
      ) : <Skeleton className="h-[300px] rounded-3xl" />}

      <AnimatePresence><HowItWorks /></AnimatePresence>

      {/* ------------------------------------------------ THE LOOP: the whole system, live */}
      <Panel title="Your marketing, running right now" subtitle="Left to right — then it learns and goes again. Click any step to open it." padded>
        {d ? <SystemLoop stages={stages} /> : <Skeleton className="h-40" />}
      </Panel>

      {/* ------------------------------------------------ DECISIONS + MONEY */}
      <div className="grid gap-4 xl:grid-cols-[1.3fr_1fr]">
        <div className="space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h3 className="text-base font-bold text-white">What the AI wants to do next</h3>
              <p className="text-xs text-[var(--text-muted)]">Approve it, skip it, or ask why. Nothing big happens without you.</p>
            </div>
            <Tabs tabs={[{ key: 'pending', label: 'Waiting on you', count: needsYou }, { key: 'all', label: 'Everything' }]} value={feed} onChange={setFeed} />
          </div>
          <AnimatePresence mode="popLayout">
            {decisions?.results.map((dec) => <DecisionCard key={dec.id} d={dec} />)}
          </AnimatePresence>
          {decisions && decisions.results.length === 0 && (
            <div className="glass p-8 text-center text-sm text-[var(--text-muted)]">Nothing waiting. The AI will put its next suggestion here.</div>
          )}
        </div>

        <div className="space-y-4">
          <Panel title="Money in vs. money out" subtitle={`Day by day, ${period}`}
            action={<Legend items={[{ label: 'Made', color: 'var(--series-1)' }, { label: 'Spent', color: 'var(--series-2)' }]} />}>
            {d ? <RevenueSpendChart data={d.timeseries} currency={cur} height={200} /> : <Skeleton className="h-[200px]" />}
          </Panel>
          <Panel title="Where your money works hardest" subtitle="Cost to win one customer, by channel — lower is better">
            {d ? <ChannelBars data={d.channels} metric="cac" currency={cur} label="Cost per customer" height={190} /> : <Skeleton className="h-[190px]" />}
            {d && (
              <div className="mt-2 grid grid-cols-2 gap-2 text-[11px] text-[var(--text-secondary)]">
                {d.channels.slice(0, 4).map((x) => (
                  <div key={x.channel} className="flex items-center justify-between rounded-lg border border-white/[0.05] px-2 py-1.5">
                    <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full" style={{ background: channelColor(x.channel) }} />{channelLabel(x.channel)}</span>
                    <span className="num text-white">{x.roas.toFixed(1)}x back</span>
                  </div>
                ))}
              </div>
            )}
          </Panel>
        </div>
      </div>

      {/* ------------------------------------------------ everything else, one click away */}
      <Disclosure label="See everything the agents did, and your customer journey">
        <div className="grid gap-4 xl:grid-cols-[1.4fr_1fr]">
          <Panel title="Recent activity" subtitle="What the agents have been doing">
            <div className="grid gap-x-8 gap-y-1 md:grid-cols-2">
              {activity?.results.map((e, i) => (
                <motion.div key={e.id} initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.02 }} className="flex items-start gap-3 border-b border-white/[0.04] py-2 last:border-0">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-xs text-white">{e.message}</div>
                    <div className="text-[11px] text-[var(--text-muted)]">{e.agent_name} · {relTime(e.created_at)}</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </Panel>
          <Panel title="Your customer journey" subtitle="How many people are at each step">
            {d ? <Funnel data={d.funnel.map((f) => ({ ...f, stage: STAGE_LABEL[f.stage] ?? f.stage }))} /> : <Skeleton className="h-[180px]" />}
          </Panel>
        </div>
      </Disclosure>
    </div>
  )
}
