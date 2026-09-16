import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowDown, ArrowUp, CalendarDays, Sparkles } from 'lucide-react'
import { get, post } from '@/lib/api'
import { num, title } from '@/lib/format'
import { Badge, Button, PageHeader, Panel, Tabs, statusTone } from '@/components/ui'

type Item = { id: number; title: string; kind: string; theme: string; platform: string; scheduled_for: string; status: string; body: string; hashtags: string[]; engagement: Record<string, number>; seo_keyword: string }
type Keyword = { id: number; keyword: string; cluster: string; intent: string; volume: number; difficulty: number; current_rank: number | null; previous_rank: number | null }

const THEME_COLOR: Record<string, string> = { 'Industry insight': 'var(--series-1)', 'Customer problem': 'var(--series-2)', 'Case study': 'var(--series-3)', 'Founder POV': 'var(--series-6)', 'Product insight': 'var(--series-4)' }
const KIND_ICON: Record<string, string> = { linkedin_post: 'in', blog: 'B', video: '▶', instagram: 'IG', x_post: 'X', newsletter: '✉', case_study: 'CS', youtube: 'YT' }

export function ContentPage() {
  const qc = useQueryClient()
  const [tab, setTab] = useState<'calendar' | 'seo'>('calendar')
  const { data: items } = useQuery({ queryKey: ['content'], queryFn: () => get<Item[]>('/campaigns/content/') })
  const { data: kws } = useQuery({ queryKey: ['seo'], queryFn: () => get<Keyword[]>('/campaigns/seo-keywords/') })
  const plan = useMutation({ mutationFn: () => post('/campaigns/content/plan_week/', {}), onSuccess: () => { qc.invalidateQueries({ queryKey: ['content'] }); qc.invalidateQueries({ queryKey: ['decisions'] }); qc.invalidateQueries({ queryKey: ['activity'] }) } })
  const setStatus = useMutation({ mutationFn: ({ id, status }: { id: number; status: string }) => post(`/campaigns/content/${id}/set_status/`, { status }), onSuccess: () => qc.invalidateQueries({ queryKey: ['content'] }) })

  const weeks = useMemo(() => {
    if (!items) return []
    const byDay = new Map<string, Item[]>()
    items.forEach((it) => { const k = it.scheduled_for?.slice(0, 10); if (k) byDay.set(k, [...(byDay.get(k) ?? []), it]) })
    const days = Array.from(byDay.keys()).sort()
    const out: { key: string; days: { date: string; items: Item[] }[] }[] = []
    days.forEach((d) => { const dt = new Date(d); const monday = new Date(dt); monday.setDate(dt.getDate() - ((dt.getDay() + 6) % 7)); const wk = monday.toISOString().slice(0, 10); let w = out.find((x) => x.key === wk); if (!w) { w = { key: wk, days: [] }; out.push(w) } w.days.push({ date: d, items: byDay.get(d)! }) })
    return out
  }, [items])
  const published = items?.filter((i) => i.status === 'published') ?? []
  const totals = published.reduce((a, i) => ({ impressions: a.impressions + (i.engagement.impressions ?? 0), leads: a.leads + (i.engagement.leads ?? 0), clicks: a.clicks + (i.engagement.clicks ?? 0) }), { impressions: 0, leads: 0, clicks: 0 })
  const today = new Date().toISOString().slice(0, 10)

  return (
    <div className="space-y-6">
      <PageHeader title={<>Posts and <span className="gradient-text">articles</span></>}
        description="A weekly plan of social posts and blog articles, written and scheduled for you. The AI reshuffles the plan based on what people actually read."
        actions={<><Tabs tabs={[{ key: 'calendar', label: 'Plan', count: items?.length }, { key: 'seo', label: 'Search rankings', count: kws?.length }]} value={tab} onChange={setTab} /><Button onClick={() => plan.mutate()} loading={plan.isPending}><Sparkles className="h-4 w-4" /> Plan next week</Button></>} />

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {[['Published', num(published.length)], ['Times seen', num(totals.impressions)], ['Clicks', num(totals.clicks)], ['Leads from content', num(totals.leads)]].map(([l, v]) => <div key={l} className="glass p-4"><div className="label">{l}</div><div className="mt-1 text-2xl font-bold text-white">{v}</div></div>)}
      </div>

      {tab === 'calendar' && (
        <div className="space-y-4">
          <div className="flex flex-wrap gap-3 text-[11px] text-[var(--text-secondary)]">{Object.entries(THEME_COLOR).map(([t, c]) => <span key={t} className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full" style={{ background: c }} />{t}</span>)}</div>
          {weeks.map((w) => (
            <Panel key={w.key} title={<span className="flex items-center gap-2"><CalendarDays className="h-4 w-4 text-accent-soft" /> Week of {new Date(w.key).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}</span>} padded={false}>
              <div className="grid grid-cols-1 gap-px bg-white/[0.04] md:grid-cols-5">
                {w.days.map((d) => (
                  <div key={d.date} className={`bg-ink-900/40 p-3 ${d.date === today ? 'ring-1 ring-inset ring-accent/40' : ''}`}>
                    <div className="mb-2 text-[11px] font-semibold text-[var(--text-muted)]">{new Date(d.date).toLocaleDateString(undefined, { weekday: 'short', day: 'numeric' })}</div>
                    <div className="space-y-2">{d.items.map((it) => (
                      <motion.div key={it.id} whileHover={{ y: -2 }} className="rounded-xl border border-white/[0.06] bg-white/[0.03] p-2.5">
                        <div className="flex items-center gap-2"><span className="flex h-5 w-6 items-center justify-center rounded bg-white/[0.06] font-mono text-[9px] font-bold text-white">{KIND_ICON[it.kind] ?? '•'}</span><span className="h-1.5 w-1.5 rounded-full" style={{ background: THEME_COLOR[it.theme] }} /><Badge tone={statusTone(it.status)} className="ml-auto">{it.status.replace('_', ' ')}</Badge></div>
                        <div className="mt-1.5 text-xs font-semibold leading-snug text-white">{it.title}</div>
                        {it.status === 'published' ? <div className="mt-1.5 text-[10px] text-[var(--text-muted)]">{num(it.engagement.impressions)} impr · {it.engagement.likes} likes · {it.engagement.leads} leads</div>
                          : it.status === 'pending_approval' ? <button onClick={() => setStatus.mutate({ id: it.id, status: 'scheduled' })} className="mt-1.5 text-[11px] font-semibold text-emerald-300 hover:underline">Approve</button>
                          : <div className="mt-1.5 text-[10px] text-[var(--text-muted)]">{title(it.kind)}</div>}
                      </motion.div>))}</div>
                  </div>
                ))}
              </div>
            </Panel>
          ))}
        </div>
      )}

      {tab === 'seo' && (
        <Panel title="What you rank for on Google" subtitle="Green means you moved up since the last check" padded={false}>
          <table className="w-full text-sm">
            <thead><tr className="text-left text-[11px] uppercase tracking-wider text-[var(--text-muted)]"><th className="px-5 py-3">Keyword</th><th className="px-3 py-3">Cluster</th><th className="px-3 py-3">Intent</th><th className="px-3 py-3 text-right">Searches/mo</th><th className="px-3 py-3 text-right">How hard</th><th className="px-3 py-3 text-right">Your position</th><th className="px-3 py-3 text-right">Δ</th></tr></thead>
            <tbody>{kws?.map((k) => { const d = k.previous_rank != null && k.current_rank != null ? k.previous_rank - k.current_rank : null; return (
              <tr key={k.id} className="border-t border-white/[0.05] hover:bg-white/[0.03]">
                <td className="px-5 py-3 font-semibold text-white">{k.keyword}</td><td className="px-3 py-3 text-xs text-[var(--text-secondary)]">{k.cluster}</td><td className="px-3 py-3"><Badge tone={k.intent === 'commercial' ? 'accent' : 'neutral'}>{k.intent}</Badge></td>
                <td className="num px-3 py-3 text-right text-white">{num(k.volume)}</td><td className="num px-3 py-3 text-right text-[var(--text-secondary)]">{k.difficulty}</td>
                <td className="num px-3 py-3 text-right text-white">{k.current_rank ?? '—'}</td>
                <td className="px-3 py-3 text-right">{d == null ? <span className="text-[var(--text-muted)]">new</span> : d > 0 ? <span className="inline-flex items-center gap-0.5 text-emerald-300"><ArrowUp className="h-3 w-3" />{d}</span> : d < 0 ? <span className="inline-flex items-center gap-0.5 text-rose-300"><ArrowDown className="h-3 w-3" />{-d}</span> : <span className="text-[var(--text-muted)]">0</span>}</td>
              </tr>) })}</tbody>
          </table>
        </Panel>
      )}
    </div>
  )
}
