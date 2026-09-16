import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Brain, RefreshCw, Swords, TrendingUp } from 'lucide-react'
import { get, post, type Paginated } from '@/lib/api'
import { relTime, title } from '@/lib/format'
import { Badge, Button, Meter, PageHeader, Panel, Tabs, statusTone } from '@/components/ui'

type Node = { id: number; kind: string; name: string; confidence: number }
type Graph = { nodes: Node[]; edges: { source: number; target: number }[]; coverage: { kind: string; count: number }[] }
type Competitor = { id: number; name: string; positioning: string; threat_level: string; share_of_voice: number; usps: string[]; weaknesses: string[]; ad_messages: string[]; pricing: string; headcount: number; funding: string; last_seen: string }
type Signal = { id: number; kind: string; title: string; summary: string; entity: string; sentiment: string; relevance: number; opportunity: boolean; actioned: boolean; detected_at: string }

const KIND_COLOR: Record<string, string> = { product: 'var(--series-1)', customer: 'var(--series-3)', problem: 'var(--series-7)', solution: 'var(--series-6)', differentiator: 'var(--series-4)', pricing: 'var(--series-2)', objection: 'var(--series-5)', use_case: 'var(--series-3)', outcome: 'var(--series-4)', persona: 'var(--series-6)', geography: 'var(--series-1)', sales_cycle: 'var(--series-2)' }

/** Radial knowledge graph: kinds on rings, entities as nodes, related edges drawn. */
function KnowledgeGraph({ g }: { g: Graph }) {
  const layout = useMemo(() => {
    const W = 760, H = 460, cx = W / 2, cy = H / 2
    const kinds = Array.from(new Set(g.nodes.map((n) => n.kind)))
    const pos = new Map<number, { x: number; y: number }>()
    const byKind = kinds.map((k) => g.nodes.filter((n) => n.kind === k))
    const totalSlots = g.nodes.length
    let i = 0
    byKind.forEach((group, gi) => {
      group.forEach((n) => {
        const angle = (i / totalSlots) * Math.PI * 2 - Math.PI / 2
        const r = 150 + (gi % 3) * 42
        pos.set(n.id, { x: cx + Math.cos(angle) * r, y: cy + Math.sin(angle) * r * 0.78 })
        i++
      })
    })
    return { W, H, cx, cy, pos }
  }, [g])
  const [hover, setHover] = useState<number | null>(null)
  const linked = new Set<number>()
  if (hover != null) g.edges.forEach((e) => { if (e.source === hover) linked.add(e.target); if (e.target === hover) linked.add(e.source) })

  return (
    <svg viewBox={`0 0 ${layout.W} ${layout.H}`} className="h-auto w-full">
      <defs><radialGradient id="core" cx="50%" cy="50%"><stop offset="0%" stopColor="#7c6cff" stopOpacity="0.9" /><stop offset="100%" stopColor="#22d3ee" stopOpacity="0.2" /></radialGradient></defs>
      {g.edges.map((e, i) => {
        const a = layout.pos.get(e.source), b = layout.pos.get(e.target)
        if (!a || !b) return null
        const hot = hover != null && (e.source === hover || e.target === hover)
        return <line key={i} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={hot ? '#a99cff' : 'rgba(255,255,255,0.10)'} strokeWidth={hot ? 1.5 : 1} />
      })}
      {g.nodes.map((n) => {
        const p = layout.pos.get(n.id)!
        const c = layout.cx, cy = layout.cy
        return <line key={`c${n.id}`} x1={c} y1={cy} x2={p.x} y2={p.y} stroke="rgba(255,255,255,0.04)" />
      })}
      <circle cx={layout.cx} cy={layout.cy} r={30} fill="url(#core)" />
      <text x={layout.cx} y={layout.cy + 4} textAnchor="middle" fontSize="10" fill="#fff" fontWeight={700}>BUSINESS</text>
      {g.nodes.map((n) => {
        const p = layout.pos.get(n.id)!
        const dim = hover != null && hover !== n.id && !linked.has(n.id)
        return (
          <g key={n.id} onMouseEnter={() => setHover(n.id)} onMouseLeave={() => setHover(null)} style={{ cursor: 'pointer', opacity: dim ? 0.25 : 1, transition: 'opacity .2s' }}>
            <circle cx={p.x} cy={p.y} r={6 + n.confidence * 4} fill={KIND_COLOR[n.kind] ?? 'var(--series-6)'} stroke="var(--surface-1)" strokeWidth={2} />
            <text x={p.x} y={p.y - 12} textAnchor="middle" fontSize="9" fill={hover === n.id ? '#fff' : 'var(--text-secondary)'}>{n.name.length > 26 ? n.name.slice(0, 24) + '…' : n.name}</text>
          </g>
        )
      })}
    </svg>
  )
}

export function IntelligencePage() {
  const qc = useQueryClient()
  const [tab, setTab] = useState<'graph' | 'competitors' | 'signals'>('graph')
  const { data: graph } = useQuery({ queryKey: ['knowledge', 'graph'], queryFn: () => get<Graph>('/knowledge/entities/graph/') })
  const { data: comps } = useQuery({ queryKey: ['competitors'], queryFn: () => get<Competitor[]>('/knowledge/competitors/') })
  const { data: signals } = useQuery({ queryKey: ['signals'], queryFn: () => get<Paginated<Signal>>('/knowledge/signals/', { page_size: 30 }) })
  const refresh = useMutation({
    mutationFn: async () => { for (const k of ['business_intelligence', 'market_intelligence', 'competitor_intelligence']) { const agents = await get<{ id: number; key: string }[]>('/agents/agents/'); const a = agents.find((x) => x.key === k); if (a) await post(`/agents/agents/${a.id}/run/`, {}) } },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['decisions'] }); qc.invalidateQueries({ queryKey: ['activity'] }) },
  })

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Phase 1 · Intelligence" title={<>Business, market & <span className="gradient-text">competitor intelligence</span></>}
        description="A living knowledge graph every agent queries instead of re-deriving context — plus continuous external signal watching."
        actions={<><Tabs tabs={[{ key: 'graph', label: 'Knowledge graph', count: graph?.nodes.length }, { key: 'competitors', label: 'Competitor map', count: comps?.length }, { key: 'signals', label: 'Market signals', count: signals?.count }]} value={tab} onChange={setTab} />
          <Button variant="outline" onClick={() => refresh.mutate()} loading={refresh.isPending}><RefreshCw className="h-4 w-4" /> Refresh intelligence</Button></>} />

      {tab === 'graph' && graph && (
        <div className="grid gap-4 xl:grid-cols-[1.7fr_1fr]">
          <Panel title="Business Knowledge Graph" subtitle="Hover a node to see its relations" action={<Brain className="h-4 w-4 text-accent-soft" />}><KnowledgeGraph g={graph} /></Panel>
          <Panel title="Coverage by entity type" subtitle="Business Intelligence Agent · judged on coverage & freshness">
            <div className="space-y-3">
              {graph.coverage.map((c) => (
                <div key={c.kind}><div className="mb-1 flex items-center justify-between text-xs"><span className="flex items-center gap-2 text-white"><span className="h-2 w-2 rounded-full" style={{ background: KIND_COLOR[c.kind] }} />{title(c.kind)}</span><span className="num text-[var(--text-muted)]">{c.count}</span></div><Meter value={c.count} max={Math.max(...graph.coverage.map((x) => x.count))} color={KIND_COLOR[c.kind]} height={4} /></div>
              ))}
            </div>
            <div className="mt-5 rounded-xl border border-amber-400/20 bg-amber-400/5 p-3 text-xs text-amber-200"><b>Gap detected:</b> no source describes churn reasons. Connect CRM closed-lost data or answer 3 questions in Settings.</div>
          </Panel>
        </div>
      )}

      {tab === 'competitors' && (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {comps?.map((c, i) => (
            <motion.div key={c.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }} className="glass p-5">
              <div className="flex items-start justify-between gap-2">
                <div><h3 className="text-base font-bold text-white">{c.name}</h3><div className="text-[11px] text-[var(--text-muted)]">{c.headcount.toLocaleString()} staff · {c.funding} · seen {relTime(c.last_seen)}</div></div>
                <Badge tone={c.threat_level === 'high' ? 'bad' : c.threat_level === 'medium' ? 'warn' : 'neutral'}><Swords className="h-3 w-3" /> {c.threat_level}</Badge>
              </div>
              <p className="mt-3 text-sm text-[var(--text-secondary)]">{c.positioning}</p>
              <div className="mt-3"><div className="mb-1 flex justify-between text-[11px]"><span className="label">Share of voice</span><span className="num text-white">{Math.round(c.share_of_voice * 100)}%</span></div><Meter value={c.share_of_voice * 100} color="var(--series-2)" height={4} /></div>
              {c.ad_messages?.[0] && c.ad_messages[0] !== '-' && <div className="mt-3 rounded-xl border border-white/[0.06] bg-ink-900/60 p-3 text-xs"><div className="label mb-1">Observed ad message</div><span className="italic text-white">{c.ad_messages[0]}</span></div>}
              <div className="mt-3 grid grid-cols-2 gap-2 text-[11px]">
                <div><div className="label mb-1">USPs</div>{c.usps.map((u) => <div key={u} className="text-[var(--text-secondary)]">• {u}</div>)}</div>
                <div><div className="label mb-1">Weaknesses</div>{c.weaknesses.map((u) => <div key={u} className="text-emerald-300/90">• {u}</div>)}</div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {tab === 'signals' && (
        <div className="space-y-2">
          {signals?.results.map((s, i) => (
            <motion.div key={s.id} initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.03 }} className="glass flex flex-wrap items-center gap-4 px-5 py-4">
              <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${s.opportunity ? 'bg-emerald-500/10 text-emerald-300' : 'bg-white/[0.05] text-[var(--text-secondary)]'}`}><TrendingUp className="h-4 w-4" /></div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2"><Badge tone="neutral">{title(s.kind)}</Badge>{s.opportunity && <Badge tone="good">opportunity</Badge>}{s.actioned && <Badge tone="accent">actioned</Badge>}<span className="text-[11px] text-[var(--text-muted)]">{s.entity} · {relTime(s.detected_at)}</span></div>
                <div className="mt-1 text-sm font-semibold text-white">{s.title}</div>
                <div className="text-xs text-[var(--text-muted)]">{s.summary}</div>
              </div>
              <div className="w-28"><div className="label mb-1 text-right">Relevance</div><Meter value={s.relevance * 100} color={s.relevance > 0.85 ? 'var(--status-good)' : 'var(--series-1)'} height={4} /></div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
