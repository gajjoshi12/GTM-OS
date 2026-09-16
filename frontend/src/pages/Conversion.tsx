import { motion } from 'framer-motion'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ExternalLink, FlaskConical, Layers } from 'lucide-react'
import { get, patch } from '@/lib/api'
import { channelColor, channelLabel, num } from '@/lib/format'
import { Badge, Button, Meter, PageHeader, statusTone } from '@/components/ui'

type LP = { id: number; name: string; slug: string; channel: string; audience: string; headline: string; subheadline: string; cta: string; offer: string; sections: string[]; status: string; visitors: number; conversions: number; conversion_rate: number; active_experiment: string; variants: { label: string; headline: string; cr: number }[] }

export function ConversionPage() {
  const qc = useQueryClient()
  const { data: pages } = useQuery({ queryKey: ['landing-pages'], queryFn: () => get<LP[]>('/campaigns/landing-pages/') })
  const publish = useMutation({ mutationFn: (id: number) => patch(`/campaigns/landing-pages/${id}/`, { status: 'live' }), onSuccess: () => qc.invalidateQueries({ queryKey: ['landing-pages'] }) })

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Phase 10 · Landing Page Agent → CRO Agent" title={<>Ad → Page → Offer → CTA, <span className="gradient-text">kept coherent</span></>}
        description="A channel-matched page for every campaign: LinkedIn → enterprise, Google → high intent, Meta → education. The CRO Agent experiments on headline, CTA, form, proof and structure continuously." />
      <div className="grid gap-4 md:grid-cols-2">
        {pages?.map((p, i) => (
          <motion.div key={p.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} className="glass overflow-hidden">
            {/* page preview */}
            <div className="relative border-b border-white/[0.06] bg-ink-900/70 p-5">
              <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent" />
              <div className="mb-3 flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-rose-400/70" /><span className="h-2 w-2 rounded-full bg-amber-400/70" /><span className="h-2 w-2 rounded-full bg-emerald-400/70" /><span className="ml-2 rounded-md bg-white/[0.05] px-2 py-0.5 font-mono text-[10px] text-[var(--text-muted)]">go.skybag.example.com/{p.slug}</span></div>
              <div className="rounded-xl border border-white/[0.06] bg-gradient-to-br from-white/[0.04] to-transparent p-5">
                <div className="mb-2 flex items-center gap-2"><span className="h-2 w-2 rounded-full" style={{ background: channelColor(p.channel) }} /><span className="label">{channelLabel(p.channel)} · {p.audience}</span></div>
                <div className="text-lg font-extrabold leading-tight text-white">{p.headline}</div>
                <div className="mt-1 text-xs text-[var(--text-secondary)]">{p.subheadline}</div>
                <div className="mt-3 flex items-center gap-2"><span className="rounded-lg bg-gradient-to-r from-accent to-accent-cyan px-3 py-1.5 text-[11px] font-bold text-ink-950">{p.cta}</span><span className="text-[10px] text-[var(--text-muted)]">offer: {p.offer}</span></div>
                <div className="mt-3 flex flex-wrap gap-1">{p.sections.map((s) => <span key={s} className="rounded bg-white/[0.05] px-1.5 py-0.5 font-mono text-[9px] text-[var(--text-muted)]">{s}</span>)}</div>
              </div>
            </div>
            <div className="p-5">
              <div className="flex items-center justify-between"><h3 className="text-sm font-bold text-white">{p.name}</h3><Badge tone={statusTone(p.status)} dot>{p.status.replace('_', ' ')}</Badge></div>
              <div className="mt-3 grid grid-cols-3 gap-2 text-center">
                <div className="rounded-xl bg-white/[0.03] p-2"><div className="text-lg font-bold text-white">{num(p.visitors)}</div><div className="text-[10px] text-[var(--text-muted)]">visitors</div></div>
                <div className="rounded-xl bg-white/[0.03] p-2"><div className="text-lg font-bold text-white">{num(p.conversions)}</div><div className="text-[10px] text-[var(--text-muted)]">conversions</div></div>
                <div className="rounded-xl bg-white/[0.03] p-2"><div className="text-lg font-bold text-emerald-300">{p.conversion_rate}%</div><div className="text-[10px] text-[var(--text-muted)]">CVR</div></div>
              </div>
              {p.active_experiment && (
                <div className="mt-3 rounded-xl border border-white/[0.06] bg-white/[0.02] p-3">
                  <div className="flex items-center gap-2 text-[11px]"><FlaskConical className="h-3.5 w-3.5 text-accent-soft" /><span className="font-semibold text-white">CRO experiment:</span><span className="text-[var(--text-secondary)]">{p.active_experiment}</span></div>
                  {p.variants.length > 0 && <div className="mt-2 space-y-1.5">{p.variants.map((v) => <div key={v.label}><div className="flex justify-between text-[11px]"><span className="text-[var(--text-secondary)]"><b className="text-white">{v.label}</b> · {v.headline}</span><span className="num text-white">{v.cr}%</span></div><Meter value={v.cr} max={Math.max(...p.variants.map((x) => x.cr)) * 1.2} height={4} color={v.cr === Math.max(...p.variants.map((x) => x.cr)) ? 'var(--status-good)' : 'var(--series-1)'} /></div>)}</div>}
                </div>
              )}
              <div className="mt-3 flex gap-2">{p.status === 'pending_approval' && <Button size="sm" variant="success" onClick={() => publish.mutate(p.id)}><Layers className="h-3.5 w-3.5" /> Approve & publish</Button>}<Button size="sm" variant="ghost"><ExternalLink className="h-3.5 w-3.5" /> Preview</Button></div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
