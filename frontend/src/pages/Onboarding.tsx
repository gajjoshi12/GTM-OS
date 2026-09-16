import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { useMutation } from '@tanstack/react-query'
import { ArrowRight, Check, Loader2, Sparkles } from 'lucide-react'
import { Aurora } from '@/components/layout/Aurora'
import { Button, Field, inputCls } from '@/components/ui'
import { errorMessage, post } from '@/lib/api'
import { useAuth } from '@/store/auth'

const EXAMPLE = 'We sell enterprise baggage-management software to airports. We want 30 qualified airport prospects per month and ₹5 crore of pipeline.'
const DERIVES = ['Target segments', 'Target accounts', 'Decision-makers', 'Geographies', 'Messaging', 'Channels', 'Content', 'Ad creative', 'Outbound sequences', 'Offers', 'Landing pages', 'Experiment backlog', 'Budget allocation', 'Execution']

type Plan = { segments?: { name: string; why: string; priority: number }[]; decision_makers?: { title: string; pain: string; angle: string }[]; channels?: { channel: string; role: string; budget_share_pct: number; expected_cac: number }[]; monthly_targets?: Record<string, number>; messaging?: { core_promise: string } }

export function OnboardingPage() {
  const nav = useNavigate()
  const refreshUser = useAuth((s) => s.refreshUser)
  const user = useAuth((s) => s.user)
  const [form, setForm] = useState({
    company_name: user?.current_workspace?.name ?? '', website: '', industry: '', founder_brief: '', currency: 'INR',
    revenue_goal: '50000000', marketing_budget: '12000000', gross_margin_pct: '75', target_geographies: 'Europe, Middle East', average_deal_size: '4000000', sales_cycle_days: '90',
  })
  const [step, setStep] = useState(0)
  const [plan, setPlan] = useState<Plan | null>(null)

  const submit = useMutation({
    mutationFn: () => post<{ business: { derived_plan: Plan } }>('/core/onboarding/', {
      ...form, revenue_goal: Number(form.revenue_goal), marketing_budget: Number(form.marketing_budget), gross_margin_pct: Number(form.gross_margin_pct),
      average_deal_size: Number(form.average_deal_size), sales_cycle_days: Number(form.sales_cycle_days),
      target_geographies: form.target_geographies.split(',').map((s) => s.trim()).filter(Boolean), description: form.founder_brief,
    }),
    onSuccess: async (d) => { setPlan(d.business.derived_plan); await refreshUser() },
  })

  return (
    <div className="relative min-h-full overflow-hidden">
      <Aurora intensity={0.8} />
      <div className="relative mx-auto max-w-4xl px-6 py-12">
        <div className="mb-8 flex items-center gap-3"><div className="h-9 w-9 rounded-xl bg-gradient-to-br from-accent to-accent-cyan shadow-glow" /><span className="font-bold text-white">AI GTM OS</span><span className="ml-auto label">Onboarding</span></div>

        <AnimatePresence mode="wait">
          {!plan && !submit.isPending && (
            <motion.div key="form" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }} className="glass-strong p-8">
              <div className="label mb-2 !text-accent-soft">Step {step + 1} of 2</div>
              {step === 0 ? (
                <>
                  <h1 className="text-3xl font-bold tracking-tight text-white">Describe your business in one sentence.</h1>
                  <p className="mt-2 text-sm text-[var(--text-secondary)]">The AI CMO derives everything else — segments, personas, channels, messaging, budget split and the experiment backlog.</p>
                  <textarea value={form.founder_brief} onChange={(e) => setForm({ ...form, founder_brief: e.target.value })} rows={4} placeholder={EXAMPLE}
                    className={inputCls + ' mt-6 text-base leading-relaxed'} />
                  <button type="button" onClick={() => setForm({ ...form, founder_brief: EXAMPLE, company_name: form.company_name || 'SkyBag Systems', industry: 'Airport baggage-management software' })} className="mt-2 text-xs text-accent-soft hover:underline">Use the example</button>
                  <div className="mt-6 flex flex-wrap gap-2">{DERIVES.map((d, i) => <motion.span key={d} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.04 }} className="rounded-full border border-white/10 bg-white/[0.03] px-2.5 py-1 text-[11px] text-[var(--text-secondary)]">{d}</motion.span>)}</div>
                  <div className="mt-8 flex justify-end"><Button size="lg" disabled={form.founder_brief.trim().length < 20} onClick={() => setStep(1)}>Continue <ArrowRight className="h-4 w-4" /></Button></div>
                </>
              ) : (
                <>
                  <h1 className="text-3xl font-bold tracking-tight text-white">Goal, budget, margin.</h1>
                  <p className="mt-2 text-sm text-[var(--text-secondary)]">These bound every autonomous decision — spend caps, CAC targets and payback.</p>
                  <div className="mt-6 grid gap-4 md:grid-cols-2">
                    <Field label="Company"><input className={inputCls} value={form.company_name} onChange={(e) => setForm({ ...form, company_name: e.target.value })} /></Field>
                    <Field label="Website"><input className={inputCls} placeholder="https://" value={form.website} onChange={(e) => setForm({ ...form, website: e.target.value })} /></Field>
                    <Field label="Industry"><input className={inputCls} value={form.industry} onChange={(e) => setForm({ ...form, industry: e.target.value })} /></Field>
                    <Field label="Currency"><select className={inputCls} value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value })}>{['INR', 'USD', 'EUR', 'GBP', 'AED', 'SGD'].map((c) => <option key={c}>{c}</option>)}</select></Field>
                    <Field label="Revenue goal (annual)"><input className={inputCls} type="number" value={form.revenue_goal} onChange={(e) => setForm({ ...form, revenue_goal: e.target.value })} /></Field>
                    <Field label="Marketing budget (annual)"><input className={inputCls} type="number" value={form.marketing_budget} onChange={(e) => setForm({ ...form, marketing_budget: e.target.value })} /></Field>
                    <Field label="Gross margin %"><input className={inputCls} type="number" value={form.gross_margin_pct} onChange={(e) => setForm({ ...form, gross_margin_pct: e.target.value })} /></Field>
                    <Field label="Average deal size"><input className={inputCls} type="number" value={form.average_deal_size} onChange={(e) => setForm({ ...form, average_deal_size: e.target.value })} /></Field>
                    <Field label="Target geographies" hint="Comma separated"><input className={inputCls} value={form.target_geographies} onChange={(e) => setForm({ ...form, target_geographies: e.target.value })} /></Field>
                    <Field label="Sales cycle (days)"><input className={inputCls} type="number" value={form.sales_cycle_days} onChange={(e) => setForm({ ...form, sales_cycle_days: e.target.value })} /></Field>
                  </div>
                  {submit.isError && <div className="mt-4 rounded-xl border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-xs text-rose-300">{errorMessage(submit.error)}</div>}
                  <div className="mt-8 flex justify-between"><Button variant="ghost" onClick={() => setStep(0)}>Back</Button><Button size="lg" onClick={() => submit.mutate()}><Sparkles className="h-4 w-4" /> Build my GTM system</Button></div>
                </>
              )}
            </motion.div>
          )}

          {submit.isPending && (
            <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="glass-strong p-10 text-center">
              <div className="relative mx-auto h-24 w-24">
                <div className="absolute inset-0 rounded-full border border-accent/30 animate-orbit [animation-duration:8s]"><span className="absolute -top-1.5 left-1/2 h-3 w-3 -translate-x-1/2 rounded-full bg-accent" /></div>
                <div className="absolute inset-3 rounded-full border border-cyan-400/30 animate-orbit [animation-duration:5s] [animation-direction:reverse]"><span className="absolute -top-1 left-1/2 h-2 w-2 -translate-x-1/2 rounded-full bg-accent-cyan" /></div>
                <Loader2 className="absolute inset-0 m-auto h-6 w-6 animate-spin text-white" />
              </div>
              <h2 className="mt-6 text-xl font-bold text-white">The AI CMO is building your operating plan</h2>
              <div className="mx-auto mt-4 max-w-md space-y-2 text-left">
                {['Business Intelligence → knowledge graph', 'Market Intelligence → opportunity map', 'Competitor Intelligence → competitor map', 'ICP Agent → ranked segments', 'AI CMO → channels, budget, experiments'].map((s, i) => (
                  <motion.div key={s} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.5 }} className="flex items-center gap-2 text-sm text-[var(--text-secondary)]"><Check className="h-4 w-4 text-emerald-400" />{s}</motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {plan && (
            <motion.div key="plan" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
              <div className="glass-strong p-8">
                <div className="label !text-accent-soft">Derived plan</div>
                <h2 className="mt-1 text-2xl font-bold text-white">{plan.messaging?.core_promise ?? 'Your GTM system is ready.'}</h2>
                <div className="mt-6 grid gap-6 md:grid-cols-3">
                  <div><div className="label mb-2">Segments</div>{plan.segments?.map((s) => <div key={s.name} className="mb-2 rounded-xl border border-white/[0.06] bg-white/[0.02] p-3"><div className="text-sm font-semibold text-white">#{s.priority} {s.name}</div><div className="text-xs text-[var(--text-muted)]">{s.why}</div></div>)}</div>
                  <div><div className="label mb-2">Decision-makers</div>{plan.decision_makers?.map((d) => <div key={d.title} className="mb-2 rounded-xl border border-white/[0.06] bg-white/[0.02] p-3"><div className="text-sm font-semibold text-white">{d.title}</div><div className="text-xs text-[var(--text-muted)]">{d.angle}</div></div>)}</div>
                  <div><div className="label mb-2">Channel mix</div>{plan.channels?.map((c) => <div key={c.channel} className="mb-2 flex items-center justify-between rounded-xl border border-white/[0.06] bg-white/[0.02] p-3"><div><div className="text-sm font-semibold text-white">{c.channel.replace('_', ' ')}</div><div className="text-xs text-[var(--text-muted)]">{c.role}</div></div><div className="font-mono text-sm text-accent-soft">{c.budget_share_pct}%</div></div>)}</div>
                </div>
                <div className="mt-8 flex justify-end"><Button size="lg" onClick={() => nav('/')}>Open Command Centre <ArrowRight className="h-4 w-4" /></Button></div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
