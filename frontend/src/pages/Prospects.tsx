import { useState } from 'react'
import { motion } from 'framer-motion'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Check, Database, Search, ShieldCheck, Sparkles } from 'lucide-react'
import { get, post, type Paginated } from '@/lib/api'
import { money, num, title } from '@/lib/format'
import { Badge, Button, Mark, Meter, Modal, PageHeader, Panel, Tabs, inputCls, statusTone } from '@/components/ui'

type ICP = { id: number; name: string; rank: number; status: string; description: string; criteria: Record<string, string | string[]>; personas: { title: string; pain: string; angle: string }[]; expected_acv: string; estimated_tam: number; prospects_count: number; reply_rate: number; meeting_rate: number; buying_signals: string[] }
type Company = { id: number; name: string; domain: string; country: string; city: string; headcount: number; revenue: string; tech_stack: string[]; signals: string[]; icp_name: string; fit_score: number; score_breakdown: Record<string, number>; tier: number; source: string; enriched: boolean; contacts_count: number; contacts?: Contact[] }
type Contact = { id: number; full_name: string; title: string; persona: string; email: string; email_status: string; stage: string; lead_score: number; intelligence_card: Record<string, string>; enrichment_log: { provider: string; fields: string[]; ok: boolean }[]; verification: Record<string, unknown> }
type Stats = { total: number; by_tier: Record<string, number>; avg_fit: number; enriched: number; by_country: { country: string; c: number }[] }

export function ProspectsPage() {
  const qc = useQueryClient()
  const [tab, setTab] = useState<'icps' | 'accounts' | 'contacts'>('accounts')
  const [tier, setTier] = useState<'' | '1' | '2' | '3'>('')
  const [q, setQ] = useState('')
  const [open, setOpen] = useState<Company | null>(null)
  const { data: icps } = useQuery({ queryKey: ['icps'], queryFn: () => get<ICP[]>('/leads/icps/') })
  const { data: stats } = useQuery({ queryKey: ['companies', 'stats'], queryFn: () => get<Stats>('/leads/companies/stats/') })
  const { data: companies } = useQuery({ queryKey: ['companies', tier, q], queryFn: () => get<Paginated<Company>>('/leads/companies/', { tier: tier || undefined, search: q || undefined, page_size: 40 }) })
  const { data: contacts } = useQuery({ queryKey: ['contacts', q], queryFn: () => get<Paginated<Contact & { company_name: string; company_tier: number }>>('/leads/contacts/', { search: q || undefined, page_size: 40, ordering: '-lead_score' }), enabled: tab === 'contacts' })
  const { data: detail } = useQuery({ queryKey: ['company', open?.id], queryFn: () => get<Company>(`/leads/companies/${open!.id}/`), enabled: !!open })
  const inval = () => { qc.invalidateQueries({ queryKey: ['companies'] }); qc.invalidateQueries({ queryKey: ['contacts'] }); qc.invalidateQueries({ queryKey: ['decisions'] }); qc.invalidateQueries({ queryKey: ['activity'] }) }
  const discover = useMutation({ mutationFn: () => post('/leads/companies/discover/', { count: 5000 }), onSuccess: inval })
  const enrich = useMutation({ mutationFn: () => post('/leads/contacts/enrich/', {}), onSuccess: inval })
  const approve = useMutation({ mutationFn: (id: number) => post(`/leads/icps/${id}/approve/`, {}), onSuccess: () => qc.invalidateQueries({ queryKey: ['icps'] }) })

  return (
    <div className="space-y-6">
      <PageHeader title={<>Who to <span className="gradient-text">target</span></>}
        description="The AI works out which companies are most likely to buy from you, finds them, fills in the missing contact details, and throws away anything that looks wrong before you email it."
        actions={<><Button variant="outline" onClick={() => enrich.mutate()} loading={enrich.isPending}><ShieldCheck className="h-4 w-4" /> Fill in missing details</Button><Button onClick={() => discover.mutate()} loading={discover.isPending}><Sparkles className="h-4 w-4" /> Find more companies</Button></>} />

      <div className="grid grid-cols-2 gap-3 md:grid-cols-5">
        {[['Companies found', num(stats?.total)], ['Best fit', num(stats?.by_tier?.['1'])], ['Good fit', num(stats?.by_tier?.['2'])], ['Avg match score', String(stats?.avg_fit ?? '—')], ['Details filled in', `${stats && stats.total ? Math.round((stats.enriched / stats.total) * 100) : 0}%`]].map(([l, v]) => (
          <div key={l} className="glass p-4"><div className="label">{l}</div><div className="mt-1 text-2xl font-bold text-white">{v}</div></div>
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Tabs tabs={[{ key: 'icps', label: 'Customer types', count: icps?.length }, { key: 'accounts', label: 'Companies', count: stats?.total }, { key: 'contacts', label: 'People' }]} value={tab} onChange={setTab} />
        {tab !== 'icps' && <>
          <div className="relative"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-muted)]" /><input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search…" className={inputCls + ' !w-64 !pl-9'} /></div>
          {tab === 'accounts' && <Tabs tabs={[{ key: '', label: 'All' }, { key: '1', label: 'Best fit' }, { key: '2', label: 'Good fit' }, { key: '3', label: 'Weak fit' }]} value={tier} onChange={setTier} />}
        </>}
      </div>

      {tab === 'icps' && (
        <div className="grid gap-4 xl:grid-cols-3">
          {icps?.map((icp, i) => (
            <motion.div key={icp.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} className={`glass p-5 ${icp.rank === 1 ? 'ring-1 ring-accent/40' : ''}`}>
              <div className="flex items-start justify-between gap-2"><div><div className="label">Customer type #{icp.rank}</div><h3 className="mt-1 text-base font-bold leading-snug text-white">{icp.name}</h3></div><Badge tone={statusTone(icp.status)}>{icp.status}</Badge></div>
              <p className="mt-2 text-xs text-[var(--text-secondary)]">{icp.description}</p>
              <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                <div className="rounded-xl bg-white/[0.03] p-2"><div className="text-lg font-bold text-white">{money(icp.expected_acv, 'INR')}</div><div className="text-[10px] text-[var(--text-muted)]">Typical deal size</div></div>
                <div className="rounded-xl bg-white/[0.03] p-2"><div className="text-lg font-bold text-white">{num(icp.estimated_tam)}</div><div className="text-[10px] text-[var(--text-muted)]">Companies like this</div></div>
                <div className="rounded-xl bg-white/[0.03] p-2"><div className="text-lg font-bold text-white">{(icp.reply_rate * 100).toFixed(1)}%</div><div className="text-[10px] text-[var(--text-muted)]">Reply rate</div></div>
              </div>
              <div className="mt-4 space-y-1.5 text-xs">{Object.entries(icp.criteria).map(([k, v]) => <div key={k} className="flex gap-2"><span className="w-20 shrink-0 text-[var(--text-muted)]">{title(k)}</span><span className="text-white">{Array.isArray(v) ? v.join(', ') : v}</span></div>)}</div>
              <div className="mt-4"><div className="label mb-1.5">Who to talk to</div>{icp.personas.map((p) => <div key={p.title} className="mb-1 rounded-lg border border-white/[0.06] px-2.5 py-1.5 text-xs"><span className="font-semibold text-white">{p.title}</span><span className="text-[var(--text-muted)]"> — {p.angle}</span></div>)}</div>
              {icp.status !== 'approved' && <Button size="sm" variant="success" className="mt-4 w-full" onClick={() => approve.mutate(icp.id)}><Check className="h-3.5 w-3.5" /> Use this for outreach</Button>}
            </motion.div>
          ))}
        </div>
      )}

      {tab === 'accounts' && (
        <Panel padded={false}>
          <table className="w-full text-sm">
            <thead><tr className="text-left text-[11px] uppercase tracking-wider text-[var(--text-muted)]"><th className="px-5 py-3">Account</th><th className="px-3 py-3">Customer type</th><th className="px-3 py-3">Fit</th><th className="px-3 py-3 w-44">Match score</th><th className="px-3 py-3">Why now</th><th className="px-3 py-3">Source</th><th className="px-3 py-3 text-right">Contacts</th></tr></thead>
            <tbody>
              {companies?.results.map((c) => (
                <tr key={c.id} onClick={() => setOpen(c)} className="cursor-pointer border-t border-white/[0.05] transition hover:bg-white/[0.03]">
                  <td className="px-5 py-3"><div className="flex items-center gap-3"><Mark seed={c.name} /><div><div className="font-semibold text-white">{c.name}</div><div className="text-[11px] text-[var(--text-muted)]">{c.city}, {c.country} · {num(c.headcount)} staff</div></div></div></td>
                  <td className="px-3 py-3 text-xs text-[var(--text-secondary)]">{c.icp_name?.split(' ').slice(0, 4).join(' ')}</td>
                  <td className="px-3 py-3"><Badge tone={c.tier === 1 ? 'accent' : c.tier === 2 ? 'cyan' : 'neutral'}>{c.tier === 1 ? 'Best fit' : c.tier === 2 ? 'Good fit' : 'Weak fit'}</Badge></td>
                  <td className="px-3 py-3"><div className="flex items-center gap-2"><Meter value={c.fit_score} height={5} color={c.fit_score >= 80 ? 'var(--status-good)' : c.fit_score >= 60 ? 'var(--series-1)' : 'var(--text-muted)'} /><span className="num w-7 text-xs font-semibold text-white">{c.fit_score}</span></div></td>
                  <td className="px-3 py-3"><div className="flex flex-wrap gap-1">{c.signals.slice(0, 2).map((s) => <span key={s} className="rounded-md bg-white/[0.05] px-1.5 py-0.5 text-[10px] text-[var(--text-secondary)]">{s}</span>)}</div></td>
                  <td className="px-3 py-3 text-xs text-[var(--text-muted)]">{c.source}{c.enriched && <Check className="ml-1 inline h-3 w-3 text-emerald-400" />}</td>
                  <td className="px-3 py-3 text-right text-xs text-white">{c.contacts_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>
      )}

      {tab === 'contacts' && (
        <Panel padded={false}>
          <table className="w-full text-sm">
            <thead><tr className="text-left text-[11px] uppercase tracking-wider text-[var(--text-muted)]"><th className="px-5 py-3">Contact</th><th className="px-3 py-3">Company</th><th className="px-3 py-3">Role</th><th className="px-3 py-3">Email</th><th className="px-3 py-3">Where they are</th><th className="px-3 py-3 text-right">Score</th></tr></thead>
            <tbody>{contacts?.results.map((c) => (
              <tr key={c.id} className="border-t border-white/[0.05] hover:bg-white/[0.03]">
                <td className="px-5 py-3"><div className="font-semibold text-white">{c.full_name}</div><div className="text-[11px] text-[var(--text-muted)]">{c.title}</div></td>
                <td className="px-3 py-3 text-xs text-[var(--text-secondary)]">{c.company_name} <Badge tone={c.company_tier === 1 ? 'accent' : 'neutral'} className="ml-1">T{c.company_tier}</Badge></td>
                <td className="px-3 py-3 text-xs text-[var(--text-secondary)]">{c.persona}</td>
                <td className="px-3 py-3"><Badge tone={statusTone(c.email_status)} dot>{c.email_status}</Badge></td>
                <td className="px-3 py-3 text-xs capitalize text-white">{c.stage}</td>
                <td className="num px-3 py-3 text-right text-xs font-semibold text-white">{c.lead_score}</td>
              </tr>))}</tbody>
          </table>
        </Panel>
      )}

      <Modal open={!!open} onClose={() => setOpen(null)} width="max-w-3xl">
        {detail && (
          <div className="space-y-5">
            <div className="flex items-start gap-4"><Mark seed={detail.name} size={48} /><div className="flex-1"><h3 className="text-xl font-bold text-white">{detail.name}</h3><div className="text-xs text-[var(--text-muted)]">{detail.domain} · {detail.city}, {detail.country} · {num(detail.headcount)} staff · revenue {money(detail.revenue, 'INR')}</div><div className="mt-2 flex flex-wrap gap-1.5">{detail.tech_stack.map((t) => <Badge key={t}>{t}</Badge>)}</div></div><div className="text-right"><div className="label">Match</div><div className="text-3xl font-bold text-white">{detail.fit_score}</div><Badge tone="accent">{detail.tier === 1 ? 'Best fit' : detail.tier === 2 ? 'Good fit' : 'Weak fit'}</Badge></div></div>
            <div className="grid gap-4 md:grid-cols-2">
              <div><div className="label mb-2">Why this score</div>{Object.entries(detail.score_breakdown).map(([k, v]) => <div key={k} className="mb-1.5"><div className="flex justify-between text-[11px]"><span className="text-[var(--text-secondary)]">{title(k)}</span><span className="num text-white">{v}</span></div><Meter value={v} height={4} /></div>)}</div>
              <div><div className="label mb-2">Signs they might buy</div>{detail.signals.map((s) => <div key={s} className="mb-1 rounded-lg border border-emerald-500/20 bg-emerald-500/5 px-2.5 py-1.5 text-xs text-emerald-200">{s}</div>)}</div>
            </div>
            <div><div className="label mb-2">People to contact, and what we know about them</div>
              <div className="space-y-2">{detail.contacts?.map((ct) => (
                <details key={ct.id} className="rounded-xl border border-white/[0.06] bg-white/[0.02]"><summary className="flex cursor-pointer items-center gap-3 px-3 py-2.5 text-sm"><span className="font-semibold text-white">{ct.full_name}</span><span className="text-xs text-[var(--text-muted)]">{ct.title}</span><Badge tone={statusTone(ct.email_status)} className="ml-auto">{ct.email_status}</Badge><span className="num text-xs text-white">{ct.lead_score}</span></summary>
                  <div className="grid gap-3 border-t border-white/[0.05] px-3 py-3 text-xs md:grid-cols-2">
                    <div><div className="label mb-1">What we know</div>{Object.entries(ct.intelligence_card).map(([k, v]) => <div key={k} className="flex gap-2 py-0.5"><span className="w-24 shrink-0 text-[var(--text-muted)]">{title(k)}</span><span className="text-white">{v}</span></div>)}</div>
                    <div><div className="label mb-1"><Database className="mr-1 inline h-3 w-3" />Where the details came from</div>{ct.enrichment_log.map((e, i) => <div key={i} className="flex items-center gap-2 py-0.5"><span className={e.ok ? 'text-emerald-400' : 'text-rose-400'}>{e.ok ? '✓' : '✗'}</span><span className="text-white">{e.provider}</span><span className="text-[var(--text-muted)]">{e.fields.join(', ')}</span></div>)}
                      <div className="label mb-1 mt-3">Safety checks</div>{Object.entries(ct.verification).filter(([k]) => k !== 'checked_at').map(([k, v]) => <div key={k} className="flex gap-2 py-0.5"><span className="w-24 text-[var(--text-muted)]">{title(k)}</span><span className={v === true ? 'text-emerald-300' : v === false ? 'text-[var(--text-secondary)]' : 'text-white'}>{String(v)}</span></div>)}</div>
                  </div></details>))}</div></div>
          </div>
        )}
      </Modal>
    </div>
  )
}
