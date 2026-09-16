import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Check, Shield, ShieldAlert, ShieldCheck, Sparkles } from 'lucide-react'
import { get, patch, post } from '@/lib/api'
import { money } from '@/lib/format'
import { Badge, Button, Field, PageHeader, Panel, Tabs, inputCls } from '@/components/ui'

type Controls = { mode: string; daily_spend_cap: string; monthly_spend_cap: string; max_daily_outbound: number; can_change_pricing: boolean; can_email_unapproved_icps: boolean; can_launch_paid_without_approval: boolean; can_publish_social_without_approval: boolean; compliance_gate_required: boolean; regulated_vertical: boolean; agent_mode_overrides: Record<string, string> }
type Brand = { tone: string; voice_rules: string[]; vocabulary_preferred: string[]; vocabulary_banned: string[]; primary_color: string; secondary_color: string; font_family: string; approved_claims: string[]; forbidden_claims: string[]; legal_disclaimer: string }
type Business = { company_name: string; website: string; industry: string; founder_brief: string; currency: string; revenue_goal: string; marketing_budget: string; gross_margin_pct: string; target_geographies: string[]; average_deal_size: string; sales_cycle_days: number; derived_plan: Record<string, unknown> }

const MODES = [
  { key: 'copilot', label: 'Copilot', icon: Shield, desc: 'AI recommends; a human executes every action.' },
  { key: 'autonomous_with_approval', label: 'Autonomous with approval', icon: ShieldCheck, desc: 'AI prepares copy, creative, targeting and budget; you approve before it goes live.' },
  { key: 'full_autonomy', label: 'Full autonomy within limits', icon: ShieldAlert, desc: 'AI executes inside your guardrails — spend caps, approved ICPs, no pricing changes.' },
]
const OVERRIDABLE = ['paid_media', 'media_buyer', 'sequence', 'sdr', 'social', 'seo', 'landing_page', 'email_marketing']

export function SettingsPage() {
  const qc = useQueryClient()
  const [tab, setTab] = useState<'control' | 'brand' | 'business'>('control')
  const { data: controls } = useQuery({ queryKey: ['controls'], queryFn: () => get<Controls>('/core/controls/') })
  const { data: brand } = useQuery({ queryKey: ['brand'], queryFn: () => get<Brand>('/core/brand/') })
  const { data: business } = useQuery({ queryKey: ['business'], queryFn: () => get<Business>('/core/business/') })
  const [c, setC] = useState<Controls | null>(null)
  const [b, setB] = useState<Brand | null>(null)
  const [biz, setBiz] = useState<Business | null>(null)
  useEffect(() => { if (controls) setC(controls) }, [controls])
  useEffect(() => { if (brand) setB(brand) }, [brand])
  useEffect(() => { if (business) setBiz(business) }, [business])
  const saveC = useMutation({ mutationFn: () => patch('/core/controls/', c), onSuccess: () => qc.invalidateQueries({ queryKey: ['controls'] }) })
  const saveB = useMutation({ mutationFn: () => patch('/core/brand/', b), onSuccess: () => qc.invalidateQueries({ queryKey: ['brand'] }) })
  const saveBiz = useMutation({ mutationFn: () => patch('/core/business/', biz), onSuccess: () => qc.invalidateQueries({ queryKey: ['business'] }) })
  const regen = useMutation({ mutationFn: () => post('/core/business/regenerate-plan/', {}), onSuccess: () => qc.invalidateQueries({ queryKey: ['business'] }) })
  const listField = (v: string[]) => v.join('\n')
  const parseList = (s: string) => s.split('\n').map((x) => x.trim()).filter(Boolean)

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Human control model · Brand · Business" title={<>You set the limits. <span className="gradient-text">The AI works inside them.</span></>}
        description="Three operating modes, selectable per workspace or per agent. Every guardrail here bounds what the AI may do without you."
        actions={<Tabs tabs={[{ key: 'control', label: 'Control & guardrails' }, { key: 'brand', label: 'Brand guidelines' }, { key: 'business', label: 'Business profile' }]} value={tab} onChange={setTab} />} />

      {tab === 'control' && c && (
        <div className="space-y-4">
          <div className="grid gap-3 md:grid-cols-3">
            {MODES.map((m) => { const Icon = m.icon; const on = c.mode === m.key; return (
              <motion.button key={m.key} whileHover={{ y: -2 }} onClick={() => setC({ ...c, mode: m.key })} className={`glass p-5 text-left transition ${on ? 'ring-1 ring-accent/60' : ''}`}>
                <div className="flex items-center justify-between"><Icon className={`h-5 w-5 ${on ? 'text-accent-soft' : 'text-[var(--text-muted)]'}`} />{on && <Badge tone="accent"><Check className="h-3 w-3" /> active</Badge>}</div>
                <div className="mt-3 text-sm font-bold text-white">{m.label}</div><div className="mt-1 text-xs text-[var(--text-secondary)]">{m.desc}</div>
              </motion.button>) })}
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <Panel title="Spend & volume limits" subtitle="e.g. “AI can spend up to ₹2L/day”">
              <div className="grid gap-3 sm:grid-cols-2">
                <Field label="Daily spend cap" hint={money(c.daily_spend_cap, 'INR')}><input className={inputCls} type="number" value={c.daily_spend_cap} onChange={(e) => setC({ ...c, daily_spend_cap: e.target.value })} /></Field>
                <Field label="Monthly spend cap" hint={money(c.monthly_spend_cap, 'INR')}><input className={inputCls} type="number" value={c.monthly_spend_cap} onChange={(e) => setC({ ...c, monthly_spend_cap: e.target.value })} /></Field>
                <Field label="Max outbound / day"><input className={inputCls} type="number" value={c.max_daily_outbound} onChange={(e) => setC({ ...c, max_daily_outbound: Number(e.target.value) })} /></Field>
              </div>
            </Panel>
            <Panel title="Permissions" subtitle="What the AI may do without a human">
              <div className="space-y-2">
                {([['can_change_pricing', 'AI can change pricing'], ['can_email_unapproved_icps', 'AI can email unapproved ICPs'], ['can_launch_paid_without_approval', 'AI can launch paid campaigns without approval'], ['can_publish_social_without_approval', 'AI can publish social posts without approval'], ['compliance_gate_required', 'Compliance gate required before publish'], ['regulated_vertical', 'Regulated vertical (finance / healthcare / legal)']] as [keyof Controls, string][]).map(([k, l]) => (
                  <label key={k} className="flex cursor-pointer items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.02] px-3 py-2.5 text-sm text-white">
                    <span>{l}</span>
                    <button type="button" onClick={() => setC({ ...c, [k]: !c[k] })} className={`relative h-6 w-11 rounded-full transition ${c[k] ? 'bg-gradient-to-r from-accent to-accent-cyan' : 'bg-white/10'}`}><span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition ${c[k] ? 'left-[22px]' : 'left-0.5'}`} /></button>
                  </label>))}
              </div>
            </Panel>
          </div>
          <Panel title="Per-agent mode overrides" subtitle="Give the AI SDR full autonomy while keeping paid media on approval, for instance.">
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
              {OVERRIDABLE.map((k) => (
                <div key={k} className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-3"><div className="mb-1.5 text-xs font-semibold capitalize text-white">{k.replace('_', ' ')}</div>
                  <select className={inputCls + ' !py-1.5 !text-xs'} value={c.agent_mode_overrides[k] ?? ''} onChange={(e) => { const o = { ...c.agent_mode_overrides }; if (e.target.value) o[k] = e.target.value; else delete o[k]; setC({ ...c, agent_mode_overrides: o }) }}>
                    <option value="">Inherit workspace</option>{MODES.map((m) => <option key={m.key} value={m.key}>{m.label}</option>)}</select></div>))}
            </div>
          </Panel>
          <div className="flex justify-end"><Button onClick={() => saveC.mutate()} loading={saveC.isPending}>{saveC.isSuccess ? <><Check className="h-4 w-4" /> Saved</> : 'Save guardrails'}</Button></div>
        </div>
      )}

      {tab === 'brand' && b && (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Panel title="Voice & tone" subtitle="Enforced by the AI Brand Manager on every asset">
              <div className="space-y-3">
                <Field label="Tone"><input className={inputCls} value={b.tone} onChange={(e) => setB({ ...b, tone: e.target.value })} /></Field>
                <Field label="Voice rules (one per line)"><textarea rows={4} className={inputCls} value={listField(b.voice_rules)} onChange={(e) => setB({ ...b, voice_rules: parseList(e.target.value) })} /></Field>
                <div className="grid grid-cols-2 gap-3"><Field label="Preferred vocabulary"><textarea rows={4} className={inputCls} value={listField(b.vocabulary_preferred)} onChange={(e) => setB({ ...b, vocabulary_preferred: parseList(e.target.value) })} /></Field><Field label="Banned vocabulary"><textarea rows={4} className={inputCls} value={listField(b.vocabulary_banned)} onChange={(e) => setB({ ...b, vocabulary_banned: parseList(e.target.value) })} /></Field></div>
              </div>
            </Panel>
            <Panel title="Claims & compliance" subtitle="Gated by the Guardrail Agent before anything goes live">
              <div className="space-y-3">
                <Field label="Approved claims"><textarea rows={3} className={inputCls} value={listField(b.approved_claims)} onChange={(e) => setB({ ...b, approved_claims: parseList(e.target.value) })} /></Field>
                <Field label="Forbidden claims"><textarea rows={3} className={inputCls} value={listField(b.forbidden_claims)} onChange={(e) => setB({ ...b, forbidden_claims: parseList(e.target.value) })} /></Field>
                <Field label="Legal disclaimer"><textarea rows={2} className={inputCls} value={b.legal_disclaimer} onChange={(e) => setB({ ...b, legal_disclaimer: e.target.value })} /></Field>
                <div className="grid grid-cols-3 gap-3"><Field label="Primary"><input type="color" className="h-10 w-full rounded-xl border border-white/10 bg-transparent" value={b.primary_color} onChange={(e) => setB({ ...b, primary_color: e.target.value })} /></Field><Field label="Secondary"><input type="color" className="h-10 w-full rounded-xl border border-white/10 bg-transparent" value={b.secondary_color} onChange={(e) => setB({ ...b, secondary_color: e.target.value })} /></Field><Field label="Font"><input className={inputCls} value={b.font_family} onChange={(e) => setB({ ...b, font_family: e.target.value })} /></Field></div>
              </div>
            </Panel>
          </div>
          <div className="flex justify-end"><Button onClick={() => saveB.mutate()} loading={saveB.isPending}>{saveB.isSuccess ? <><Check className="h-4 w-4" /> Saved</> : 'Save brand'}</Button></div>
        </div>
      )}

      {tab === 'business' && biz && (
        <div className="space-y-4">
          <Panel title="Founder brief" subtitle="The sentence the whole system derives from">
            <textarea rows={3} className={inputCls + ' text-base'} value={biz.founder_brief} onChange={(e) => setBiz({ ...biz, founder_brief: e.target.value })} />
            <div className="mt-4 grid gap-3 md:grid-cols-3">
              <Field label="Company"><input className={inputCls} value={biz.company_name} onChange={(e) => setBiz({ ...biz, company_name: e.target.value })} /></Field>
              <Field label="Website"><input className={inputCls} value={biz.website} onChange={(e) => setBiz({ ...biz, website: e.target.value })} /></Field>
              <Field label="Industry"><input className={inputCls} value={biz.industry} onChange={(e) => setBiz({ ...biz, industry: e.target.value })} /></Field>
              <Field label="Revenue goal"><input className={inputCls} type="number" value={biz.revenue_goal} onChange={(e) => setBiz({ ...biz, revenue_goal: e.target.value })} /></Field>
              <Field label="Marketing budget"><input className={inputCls} type="number" value={biz.marketing_budget} onChange={(e) => setBiz({ ...biz, marketing_budget: e.target.value })} /></Field>
              <Field label="Gross margin %"><input className={inputCls} type="number" value={biz.gross_margin_pct} onChange={(e) => setBiz({ ...biz, gross_margin_pct: e.target.value })} /></Field>
              <Field label="Average deal size"><input className={inputCls} type="number" value={biz.average_deal_size} onChange={(e) => setBiz({ ...biz, average_deal_size: e.target.value })} /></Field>
              <Field label="Sales cycle (days)"><input className={inputCls} type="number" value={biz.sales_cycle_days} onChange={(e) => setBiz({ ...biz, sales_cycle_days: Number(e.target.value) })} /></Field>
              <Field label="Geographies (comma separated)"><input className={inputCls} value={biz.target_geographies.join(', ')} onChange={(e) => setBiz({ ...biz, target_geographies: e.target.value.split(',').map((s) => s.trim()).filter(Boolean) })} /></Field>
            </div>
            <div className="mt-4 flex justify-end gap-2"><Button variant="outline" onClick={() => regen.mutate()} loading={regen.isPending}><Sparkles className="h-4 w-4" /> Regenerate plan</Button><Button onClick={() => saveBiz.mutate()} loading={saveBiz.isPending}>{saveBiz.isSuccess ? <><Check className="h-4 w-4" /> Saved</> : 'Save profile'}</Button></div>
          </Panel>
          <Panel title="Derived plan (AI CMO)" subtitle="Regenerate after changing the brief"><pre className="max-h-96 overflow-auto rounded-xl bg-ink-950/70 p-4 font-mono text-[11px] leading-relaxed text-[var(--text-secondary)]">{JSON.stringify(biz.derived_plan, null, 2)}</pre></Panel>
        </div>
      )}
    </div>
  )
}
