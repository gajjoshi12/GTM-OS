import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, Sparkles } from 'lucide-react'
import { Aurora } from '@/components/layout/Aurora'
import { Button, Field, inputCls } from '@/components/ui'
import { useAuth } from '@/store/auth'
import { errorMessage } from '@/lib/api'

const LOOP = ['Understand', 'Strategize', 'Find customers', 'Create', 'Launch', 'Sell', 'Measure', 'Learn', 'Optimize', 'Scale']

export function LoginPage() {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [form, setForm] = useState({ email: import.meta.env.VITE_DEMO_EMAIL ?? '', password: import.meta.env.VITE_DEMO_PASSWORD ?? '', full_name: '', company_name: '' })
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const { login, register } = useAuth()
  const nav = useNavigate()

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErr(''); setBusy(true)
    try {
      if (mode === 'login') await login(form.email, form.password)
      else await register(form)
      nav(mode === 'login' ? '/' : '/onboarding')
    } catch (ex) { setErr(errorMessage(ex)) } finally { setBusy(false) }
  }

  return (
    <div className="relative grid min-h-full lg:grid-cols-[1.1fr_1fr]">
      <Aurora />
      <section className="relative hidden flex-col justify-between p-12 lg:flex">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-accent to-accent-cyan shadow-glow" />
          <span className="text-lg font-bold tracking-tight text-white">AI GTM OS</span>
        </div>
        <div className="max-w-xl">
          <motion.h1 initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="text-5xl font-extrabold leading-[1.05] tracking-tight text-white">
            Give it a revenue goal.<br /><span className="gradient-text">It runs the whole growth department.</span>
          </motion.h1>
          <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="mt-5 text-base leading-relaxed text-[var(--text-secondary)]">
            Research, ICP, prospecting, outbound, content, ads, landing pages, CRM, attribution — one AI CMO orchestrating 37 specialist agents in a closed loop that keeps learning.
          </motion.p>
          <div className="mt-8 flex flex-wrap gap-2">
            {LOOP.map((s, i) => (
              <motion.span key={s} initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.4 + i * 0.06 }}
                className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-medium text-white">
                {s}{i < LOOP.length - 1 && <span className="ml-2 text-[var(--text-muted)]">→</span>}
              </motion.span>
            ))}
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4 text-sm">
          {[['37', 'specialist agents'], ['60+', 'provider connectors'], ['1', 'revenue graph']].map(([n, l]) => (
            <div key={l} className="glass p-4"><div className="text-2xl font-bold text-white">{n}</div><div className="text-xs text-[var(--text-muted)]">{l}</div></div>
          ))}
        </div>
      </section>

      <section className="relative flex items-center justify-center p-6">
        <motion.form onSubmit={submit} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="glass-strong w-full max-w-md p-8">
          <div className="mb-6 flex items-center gap-2 text-accent-soft"><Sparkles className="h-4 w-4" /><span className="label !text-accent-soft">{mode === 'login' ? 'Welcome back' : 'Create your workspace'}</span></div>
          <h2 className="text-2xl font-bold text-white">{mode === 'login' ? 'Sign in to the Command Centre' : 'Start your Revenue OS'}</h2>
          <p className="mt-1 text-sm text-[var(--text-muted)]">{mode === 'login' ? 'Demo credentials are pre-filled.' : 'Your AI CMO will onboard you in one sentence.'}</p>
          <div className="mt-6 space-y-4">
            {mode === 'register' && (
              <>
                <Field label="Your name"><input className={inputCls} value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required /></Field>
                <Field label="Company"><input className={inputCls} value={form.company_name} onChange={(e) => setForm({ ...form, company_name: e.target.value })} required /></Field>
              </>
            )}
            <Field label="Email"><input className={inputCls} type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required /></Field>
            <Field label="Password"><input className={inputCls} type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required minLength={8} /></Field>
            {err && <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-xs text-rose-300">{err}</div>}
            <Button type="submit" size="lg" className="w-full" loading={busy}>{mode === 'login' ? 'Enter Command Centre' : 'Create workspace'} <ArrowRight className="h-4 w-4" /></Button>
          </div>
          <button type="button" onClick={() => setMode(mode === 'login' ? 'register' : 'login')} className="mt-5 w-full text-center text-xs text-[var(--text-muted)] hover:text-white">
            {mode === 'login' ? 'New here? Create a workspace' : 'Already have an account? Sign in'}
          </button>
        </motion.form>
      </section>
    </div>
  )
}
