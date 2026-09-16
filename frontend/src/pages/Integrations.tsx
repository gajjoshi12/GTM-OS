import { useState } from 'react'
import { motion } from 'framer-motion'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Check, ExternalLink, KeyRound, Plug, RefreshCw, Trash2, X } from 'lucide-react'
import { del, errorMessage, get, post } from '@/lib/api'
import { relTime, title } from '@/lib/format'
import { Badge, Button, Field, Modal, PageHeader, Tabs, inputCls, statusTone } from '@/components/ui'

type Provider = { key: string; name: string; category: string; category_label: string; env_vars: string[]; fields: string[]; docs: string; capabilities: string[]; used_by: string[]; state: string; env_configured: boolean; has_credentials: boolean; account_label: string; health: { ok?: boolean; message?: string; checked_at?: string }; last_synced_at: string | null; error_message: string }
type Resp = { categories: { key: string; label: string }[]; providers: Provider[]; summary: { total: number; connected: number; simulated: number } }

const STATE_LABEL: Record<string, string> = { connected: 'Connected', env_configured: 'Configured via .env', error: 'Error', not_connected: 'Simulated' }

export function IntegrationsPage() {
  const qc = useQueryClient()
  const [cat, setCat] = useState<string>('all')
  const [open, setOpen] = useState<Provider | null>(null)
  const [creds, setCreds] = useState<Record<string, string>>({})
  const [label, setLabel] = useState('')
  const { data } = useQuery({ queryKey: ['integrations'], queryFn: () => get<Resp>('/integrations/') })
  const inval = () => qc.invalidateQueries({ queryKey: ['integrations'] })
  const connect = useMutation({ mutationFn: () => post<Provider>(`/integrations/${open!.key}/`, { credentials: creds, account_label: label }), onSuccess: (p) => { inval(); setOpen(p) } })
  const test = useMutation({ mutationFn: (key: string) => post<{ ok: boolean; message: string; simulated: boolean }>(`/integrations/${key}/test/`, {}), onSuccess: inval })
  const disconnect = useMutation({ mutationFn: (key: string) => del(`/integrations/${key}/`), onSuccess: () => { inval(); setOpen(null) } })
  const list = data?.providers.filter((p) => cat === 'all' || p.category === cat) ?? []
  const openProvider = (p: Provider) => { setOpen(p); setCreds({}); setLabel(p.account_label) }

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Connector framework · provider-agnostic by design" title={<>{data?.summary.connected ?? 0} of {data?.summary.total ?? 0} providers <span className="gradient-text">connected</span></>}
        description="No single vendor is load-bearing. Each capability sits behind an internal interface with multiple adapters and waterfall fallback. Blank keys run in simulation; paste keys here (encrypted at rest) or set them in .env." />

      <div className="flex flex-wrap gap-2">
        <Tabs tabs={[{ key: 'all', label: 'All', count: data?.providers.length }, ...(data?.categories.map((c) => ({ key: c.key, label: c.label, count: data.providers.filter((p) => p.category === c.key).length })) ?? [])]} value={cat} onChange={setCat} />
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {list.map((p, i) => (
          <motion.button key={p.key} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.015 }} onClick={() => openProvider(p)}
            className={`glass p-4 text-left transition hover:bg-white/[0.05] ${p.state === 'connected' ? 'ring-1 ring-emerald-500/30' : p.state === 'env_configured' ? 'ring-1 ring-cyan-500/30' : ''}`}>
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-3"><div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/[0.05] font-bold text-white">{p.name.slice(0, 1)}</div><div><div className="text-sm font-semibold text-white">{p.name}</div><div className="text-[11px] text-[var(--text-muted)]">{p.category_label}</div></div></div>
              <span className={`mt-1 h-2 w-2 rounded-full ${p.state === 'connected' ? 'bg-emerald-400' : p.state === 'env_configured' ? 'bg-cyan-400' : p.state === 'error' ? 'bg-rose-400' : 'bg-violet-400/70'}`} />
            </div>
            <div className="mt-3 flex flex-wrap gap-1">{p.capabilities.slice(0, 3).map((c) => <span key={c} className="rounded bg-white/[0.05] px-1.5 py-0.5 font-mono text-[9px] text-[var(--text-secondary)]">{c}</span>)}</div>
            <div className="mt-3 flex items-center justify-between text-[11px]"><Badge tone={statusTone(p.state)}>{STATE_LABEL[p.state] ?? title(p.state)}</Badge><span className="truncate text-[var(--text-muted)]">{p.account_label}</span></div>
          </motion.button>
        ))}
      </div>

      <Modal open={!!open} onClose={() => setOpen(null)} width="max-w-xl">
        {open && (
          <div className="space-y-4">
            <div className="flex items-start gap-3"><div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-accent/50 to-accent-cyan/50 text-lg font-bold text-white">{open.name.slice(0, 1)}</div><div className="flex-1"><h3 className="text-lg font-bold text-white">{open.name}</h3><div className="text-xs text-[var(--text-muted)]">{open.category_label} · used by {open.used_by.map(title).join(', ')}</div></div><Badge tone={statusTone(open.state)}>{STATE_LABEL[open.state] ?? open.state}</Badge></div>
            {open.health?.message && <div className={`rounded-xl border p-3 text-xs ${open.health.ok ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-200' : 'border-white/10 bg-white/[0.03] text-[var(--text-secondary)]'}`}>{open.health.ok ? <Check className="mr-1 inline h-3.5 w-3.5" /> : <Plug className="mr-1 inline h-3.5 w-3.5" />}{open.health.message}{open.health.checked_at && <span className="ml-2 text-[var(--text-muted)]">· {relTime(open.health.checked_at)}</span>}</div>}
            <div className="rounded-xl border border-white/[0.06] bg-ink-900/60 p-3"><div className="label mb-1.5"><KeyRound className="mr-1 inline h-3 w-3" />.env keys</div><div className="font-mono text-[11px] leading-relaxed text-[var(--text-secondary)]">{open.env_vars.map((v) => <div key={v}>{v}=<span className={open.env_configured ? 'text-emerald-300' : 'text-[var(--text-muted)]'}>{open.env_configured ? '••••••••' : ''}</span></div>)}</div></div>
            <div className="space-y-3"><div className="label">Or paste credentials (encrypted at rest)</div>
              <Field label="Account label"><input className={inputCls} value={label} onChange={(e) => setLabel(e.target.value)} placeholder="e.g. Main ad account" /></Field>
              {open.fields.map((f) => <Field key={f} label={title(f)}><input className={inputCls} type={/secret|token|key|password/i.test(f) ? 'password' : 'text'} value={creds[f] ?? ''} onChange={(e) => setCreds({ ...creds, [f]: e.target.value })} placeholder={open.has_credentials ? 'stored — leave blank to keep' : ''} /></Field>)}
            </div>
            {connect.isError && <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-xs text-rose-300">{errorMessage(connect.error)}</div>}
            {test.data && <div className={`rounded-xl border px-3 py-2 text-xs ${test.data.ok ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-200' : 'border-amber-400/30 bg-amber-400/10 text-amber-200'}`}>{test.data.message}</div>}
            <div className="flex flex-wrap gap-2">
              <Button onClick={() => connect.mutate()} loading={connect.isPending}><Plug className="h-4 w-4" /> Save & test</Button>
              <Button variant="outline" onClick={() => test.mutate(open.key)} loading={test.isPending}><RefreshCw className="h-4 w-4" /> Test connection</Button>
              <a href={open.docs} target="_blank" rel="noreferrer" className="inline-flex h-10 items-center gap-1 rounded-xl px-3 text-sm text-[var(--text-secondary)] hover:text-white"><ExternalLink className="h-4 w-4" /> Docs</a>
              {(open.has_credentials || open.state === 'connected') && <Button variant="danger" className="ml-auto" onClick={() => disconnect.mutate(open.key)}><Trash2 className="h-4 w-4" /> Disconnect</Button>}
              <button onClick={() => setOpen(null)} className="ml-auto text-[var(--text-muted)] hover:text-white"><X className="h-4 w-4" /></button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
