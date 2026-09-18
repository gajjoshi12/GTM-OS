import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowRight, ArrowUpRight, Check, Globe, Lock, Menu, Minus, Plus,
  ShieldCheck, Sparkles, Terminal, X,
} from 'lucide-react'
import '@/styles/landing.css'

/* =========================================================================
   Content
   ========================================================================= */

const NAV_LINKS = [
  { label: 'Platform', href: '#platform' },
  { label: 'Agents', href: '#agents' },
  { label: 'Security', href: '#security' },
  { label: 'FAQ', href: '#faq' },
]

const PIXEL_GLYPHS = ['◆', '✦', '▲', '●', '✚', '◗']

const STACK = [
  'Salesforce', 'HubSpot', 'Apollo', 'Clay', 'LinkedIn', 'Gmail', 'Outreach', 'Slack',
  'Stripe', 'Segment', 'GA4', 'Google Ads', 'Meta Ads', 'Webflow', 'Notion', 'Snowflake',
]

const PERSONAS = [
  {
    role: 'Early-stage founder',
    short: 'Founder',
    need: 'Taking your idea beyond the drawing board',
    workflow: ['Validate', 'Launch', 'Source'],
    tagline: 'From "what if" to a real pipeline',
    features: [
      { title: 'Market research', subtitle: 'Validate demand and size your market before you build.' },
      { title: 'ICP & segmentation', subtitle: 'Find the accounts and buyers that actually convert.' },
      { title: 'Positioning & messaging', subtitle: 'Shape raw concepts into a story buyers repeat back.' },
      { title: 'Landing page builder', subtitle: 'Ship a branded site without writing a line of code.' },
    ],
  },
  {
    role: 'PLG growth team',
    short: 'Growth',
    need: 'Turning signups into self-serve revenue.',
    workflow: ['Acquire', 'Activate', 'Expand'],
    tagline: 'Compound every experiment, not just the wins',
    features: [
      { title: 'Lifecycle orchestration', subtitle: 'Trigger the right nudge at the right moment, automatically.' },
      { title: 'SEO & content engine', subtitle: 'Automate SEO for more traffic and more conversions.' },
      { title: 'Experiment factory', subtitle: 'Run, measure and promote winning variants continuously.' },
      { title: 'Activation analytics', subtitle: 'See which moment turns a trial into a customer.' },
    ],
  },
  {
    role: 'Outbound sales team',
    short: 'Outbound',
    need: 'Running every channel without the chaos.',
    workflow: ['Monitor', 'Convert', 'Scale'],
    tagline: 'Scale your sequences, not your headcount',
    features: [
      { title: 'Prospect sourcing', subtitle: 'Build verified lists from 60+ providers in one pass.' },
      { title: 'Personalised sequences', subtitle: 'Generate research-backed outreach for every account.' },
      { title: 'Competitive monitoring', subtitle: 'Track rival pricing and product moves in real time.' },
      { title: 'Inbox & reply triage', subtitle: 'Draft, route and follow up on every reply automatically.' },
    ],
  },
  {
    role: 'Agency & consultancy',
    short: 'Agency',
    need: 'Serving more clients without drowning in admin.',
    workflow: ['Acquire', 'Deliver', 'Retain'],
    tagline: 'Automate admin to take on more clients',
    features: [
      { title: 'Content marketing', subtitle: 'Produce a steady stream of work that wins new clients.' },
      { title: 'Client reporting', subtitle: 'Attribution decks generated the moment the month closes.' },
      { title: 'Operations intelligence', subtitle: 'Stay on top of tasks, deadlines and performance.' },
      { title: 'Relationship management', subtitle: 'Nurture every account without dropping a ball.' },
    ],
  },
]

const CHANNELS = [
  {
    title: 'Command Centre',
    tagline: 'Where the heavy lifting happens',
    desc: 'The full console taps into your CRM, ad accounts and warehouse, runs multi-agent campaigns, and handles the work that needs real compute.',
  },
  {
    title: 'Web Portal',
    tagline: 'Open a tab, get to work',
    desc: 'No install. Just log in and go — built for approvals and quick launches when you are on a shared device, travelling, or between meetings.',
  },
  {
    title: 'Mobile',
    tagline: 'Your agents in your pocket',
    desc: 'Stay in control on the go. Get a push the moment an agent hits a decision point, and keep the loop moving from anywhere.',
  },
]

const CHAPTERS = [
  { title: 'Set the revenue goal', desc: 'Set your North Star' },
  { title: 'Build the growth plan', desc: 'Map the path forward' },
  { title: 'Automate execution', desc: 'Hands-off across channels' },
  { title: 'Track daily progress', desc: 'Track every step' },
]

const WHY_TOOLS = [
  'Web research', 'Firmographic enrich', 'Email send', 'LinkedIn touch', 'Ad buying',
  'Landing pages', 'CRM sync', 'Call transcripts', 'Attribution', 'Forecasting',
  'A/B testing', 'Copywriting', 'SEO audit', 'Data warehouse', 'Lead scoring',
]

const TESTIMONIALS = [
  { quote: 'It replaced three tools and half our reporting. The loop just keeps tightening every week.', role: 'VP Growth, Series B SaaS' },
  { quote: 'Very easy to use. I think I finally get how AI can actually help a revenue team.', role: 'Founder, Dev tools' },
  { quote: 'Prospect research always felt like chasing missing details. Now I get to a clean shortlist faster.', role: 'Head of Sales Development' },
  { quote: 'The attribution graph settled an argument we had been having for two quarters.', role: 'Demand Gen Lead' },
  { quote: 'We went from one campaign a month to eleven live experiments, with the same team.', role: 'Marketing Director, Fintech' },
  { quote: 'Approvals before anything sends is the reason our legal team signed off in a week.', role: 'RevOps Manager' },
]

const FAQ = [
  {
    q: 'How is this different from a normal AI chat tool?',
    a: 'Chat tools answer with text. This is an execution platform: the AI CMO plans a quarter, briefs 37 specialist agents, and those agents call real systems — your CRM, ad accounts, inbox, warehouse and site. It does not just tell you what to do, it does the work and reports on what moved.',
  },
  {
    q: 'Which models are supported?',
    a: 'Claude, GPT and Gemini families all run behind the same gateway, and you can assign different models to different agents. There is also a fully deterministic simulation mode that runs the entire product with no provider keys at all — useful for demos and for evaluating the loop before you connect live data.',
  },
  {
    q: 'What can the agents actually do?',
    a: 'Market and competitor research, ICP definition, prospect sourcing and enrichment, outbound sequences across email and LinkedIn, ad campaign build and bidding, content and landing pages, CRM hygiene, lifecycle automation, experiment design, and multi-touch attribution — each owned by a specialist agent with its own memory.',
  },
  {
    q: 'Can agents run on a schedule?',
    a: 'Yes. Describe the cadence in plain language or configure it on the Agents page. Runs are reconciled on restart, so a missed window is picked up rather than silently skipped, and every run writes back to the same revenue graph.',
  },
  {
    q: 'How do approvals work?',
    a: 'A four-level permission model gates anything outward-facing. Sends, spend changes and publishes can require a human approval step, and every action lands in an audit log with the reasoning that produced it.',
  },
  {
    q: 'What does it connect to?',
    a: 'Over 60 provider connectors covering CRM, sales engagement, enrichment, ads, analytics, warehouses, billing and messaging. Connectors use least-privilege OAuth scopes, and revoking one immediately blocks new agent calls that depend on it.',
  },
]

const FOOTER = [
  { title: 'Product', links: ['Command Centre', 'Agents', 'Intelligence', 'Outbound', 'Analytics'] },
  { title: 'Platform', links: ['Integrations', 'Connectors', 'Revenue graph', 'Simulation mode'] },
  { title: 'Company', links: ['About', 'Careers', 'Blog', 'Contact'] },
  { title: 'Legal', links: ['Privacy', 'Terms', 'Security', 'DPA'] },
]

/* =========================================================================
   Small helpers
   ========================================================================= */

/** Adds `is-in` to every `.lp-reveal` inside `root` once it scrolls into view. */
function useReveal<T extends HTMLElement>() {
  const ref = useRef<T | null>(null)
  useEffect(() => {
    const root = ref.current
    if (!root) return
    const targets = root.querySelectorAll<HTMLElement>('.lp-reveal')
    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target) } }),
      { threshold: 0.12, rootMargin: '0px 0px -8% 0px' },
    )
    targets.forEach((t) => io.observe(t))
    return () => io.disconnect()
  }, [])
  return ref
}

/** Cursor-follow glow for `.lp-card`. */
function cardGlow(e: React.MouseEvent<HTMLElement>) {
  const el = e.currentTarget
  const r = el.getBoundingClientRect()
  el.style.setProperty('--lp-gx', `${((e.clientX - r.left) / r.width) * 100}%`)
  el.style.setProperty('--lp-gy', `${((e.clientY - r.top) / r.height) * 100}%`)
}

function Reveal({ delay = 0, className = '', children }: { delay?: number; className?: string; children: React.ReactNode }) {
  return <div className={`lp-reveal ${className}`} style={{ ['--lp-delay' as string]: `${delay}ms` }}>{children}</div>
}

function SectionHead({ eyebrow, title, sub }: { eyebrow?: string; title: React.ReactNode; sub?: string }) {
  return (
    <Reveal className="max-w-3xl">
      {eyebrow && <div className="mb-4 text-sm font-bold tracking-[-0.02em] text-[color:var(--lp-teal)]">{eyebrow}</div>}
      <h2 className="lp-h2">{title}</h2>
      {sub && <p className="mt-5 text-base leading-relaxed text-[color:var(--lp-text-2)]">{sub}</p>}
    </Reveal>
  )
}

/* =========================================================================
   Hero
   ========================================================================= */

function HeroPixel() {
  const [i, setI] = useState(0)
  useEffect(() => {
    const t = setInterval(() => setI((v) => (v + 1) % PIXEL_GLYPHS.length), 4000)
    return () => clearInterval(t)
  }, [])
  return (
    <button type="button" aria-label="Switch character" className="lp-pixel" onClick={() => setI((v) => (v + 1) % PIXEL_GLYPHS.length)}>
      <span key={i} className="lp-pixel-glyph">{PIXEL_GLYPHS[i]}</span>
    </button>
  )
}

const DEMO_STEPS = [
  { agent: 'Market Scout', text: 'EU demand for revenue tooling up 38% in the last 30 days.' },
  { agent: 'ICP Analyst', text: '412 accounts match the new fit model · 71 in-market right now.' },
  { agent: 'Outbound', text: 'Sequenced 71 accounts · 3 variants live · awaiting your approval.' },
  { agent: 'Attribution', text: 'Pipeline up $184k this week · CAC down 22%.' },
]

function InteractiveDemo() {
  const [step, setStep] = useState(1)
  useEffect(() => {
    const t = setInterval(() => setStep((s) => (s % DEMO_STEPS.length) + 1), 2200)
    return () => clearInterval(t)
  }, [])

  return (
    <div className="relative">
      <div className="lp-demo-glow" aria-hidden />
      <div className="lp-cursor" aria-hidden>
        <svg viewBox="0 0 24 24" className="h-5 w-5 drop-shadow">
          <defs>
            <linearGradient id="lp-cur" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#0d83f1" /><stop offset="50%" stopColor="#13d0b9" /><stop offset="100%" stopColor="#03f58f" />
            </linearGradient>
          </defs>
          <path d="M4 4 L17 10 L12.5 12.5 L10 17 Z" fill="url(#lp-cur)" stroke="#fff" strokeWidth="1.2" strokeLinejoin="round" />
        </svg>
        <span className="lp-cursor-label">Click to explore</span>
      </div>

      <div className="lp-demo-frame">
        {/* window chrome */}
        <div className="flex items-center gap-2 border-b border-[color:var(--lp-border)] px-4 py-3">
          <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
          <span className="ml-3 text-xs font-medium text-[color:var(--lp-text-3)]">Command Centre — Q3 pipeline goal</span>
        </div>

        <div className="grid gap-4 p-4 sm:grid-cols-[1.35fr_1fr] sm:p-5">
          {/* left: agent stream */}
          <div className="space-y-3">
            <div className="rounded-xl border border-[color:var(--lp-border)] bg-[color:var(--lp-fill-1)] p-3">
              <div className="mb-1.5 text-[10px] font-bold uppercase tracking-[0.14em] text-[color:var(--lp-text-4)]">You</div>
              <p className="text-sm text-[color:var(--lp-text)]">Get us to $2M ARR by Q4. Focus on mid-market in EMEA.</p>
            </div>

            {DEMO_STEPS.map((s, idx) => (
              <div
                key={s.agent}
                className="rounded-xl border p-3 transition-all duration-500"
                style={{
                  borderColor: idx < step ? 'rgba(19,208,185,0.32)' : 'var(--lp-border)',
                  background: idx < step ? 'rgba(19,208,185,0.07)' : 'transparent',
                  opacity: idx < step ? 1 : 0.35,
                  transform: idx < step ? 'none' : 'translateY(6px)',
                }}
              >
                <div className="mb-1.5 flex items-center gap-2">
                  <span className="lp-chip-dot" style={{ background: 'var(--lp-grad)' }}>{s.agent[0]}</span>
                  <span className="text-xs font-bold text-[color:var(--lp-text)]">{s.agent}</span>
                  {idx < step
                    ? <Check className="ml-auto h-3.5 w-3.5 text-[color:var(--lp-green)]" />
                    : <span className="ml-auto h-1.5 w-1.5 animate-pulse rounded-full bg-[color:var(--lp-teal)]" />}
                </div>
                <p className="text-xs leading-relaxed text-[color:var(--lp-text-2)]">{s.text}</p>
              </div>
            ))}
          </div>

          {/* right: KPI rail */}
          <div className="space-y-3">
            {[
              ['Pipeline', '$1.42M', '+18.4%'],
              ['Qualified accounts', '412', '+71'],
              ['CAC', '$1,180', '-22%'],
              ['Agents active', '37', 'all green'],
            ].map(([label, value, delta]) => (
              <div key={label} className="rounded-xl border border-[color:var(--lp-border)] bg-[color:var(--lp-fill-1)] p-3">
                <div className="text-[10px] font-bold uppercase tracking-[0.14em] text-[color:var(--lp-text-4)]">{label}</div>
                <div className="mt-1 flex items-baseline gap-2">
                  <span className="text-xl font-extrabold tracking-tight text-[color:var(--lp-text)]">{value}</span>
                  <span className="text-[11px] font-bold text-[color:var(--lp-green)]">{delta}</span>
                </div>
              </div>
            ))}
            <div className="rounded-xl border border-[color:var(--lp-border)] p-3">
              <div className="mb-2 text-[10px] font-bold uppercase tracking-[0.14em] text-[color:var(--lp-text-4)]">This week</div>
              <div className="flex h-16 items-end gap-1.5">
                {[38, 52, 44, 67, 59, 81, 94].map((h, i) => (
                  <span key={i} className="flex-1 rounded-t" style={{ height: `${h}%`, background: i > 4 ? 'var(--lp-grad)' : 'rgba(255,255,255,0.10)' }} />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function Hero() {
  return (
    <section className="relative isolate overflow-hidden pb-24 pt-20 lg:pb-28 lg:pt-24">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10"
        style={{
          background:
            'radial-gradient(1100px 520px at 12% -6%, rgba(19,208,185,0.16), transparent 62%),' +
            'radial-gradient(900px 480px at 88% 0%, rgba(13,131,241,0.14), transparent 60%)',
        }}
      />
      <div className="lp-container grid items-center gap-12 lg:grid-cols-[0.9fr_1.1fr] lg:gap-14">
        <div className="flex min-w-0 flex-col">
          <Reveal>
            <h1 className="lp-display lp-h1">
              <span className="flex items-center gap-[0.28em]">Your<span className="lp-tile" data-tilt="a" aria-hidden /></span>
              <span className="flex items-center gap-[0.28em]"><span className="lp-tile" data-tilt="b" aria-hidden />Agentic</span>
              <span className="block">Revenue</span>
              <span className="flex items-center gap-[0.28em]">Team<HeroPixel /></span>
            </h1>
          </Reveal>

          <Reveal delay={110}>
            <p className="mt-6 text-base font-semibold tracking-[-0.03em] text-[color:var(--lp-teal)]" style={{ fontFamily: 'Raleway, Inter, sans-serif' }}>
              Real pipeline. Real revenue.
            </p>
          </Reveal>

          <Reveal delay={200}>
            <div className="mt-9 flex flex-wrap items-start gap-4">
              <Link to="/login" className="lp-btn lp-btn-primary">Start free<ArrowRight className="h-[18px] w-[18px]" /></Link>
              <Link to="/login" className="lp-btn lp-btn-ghost group">
                Try in browser
                <ArrowRight className="h-[18px] w-[18px] transition-transform duration-300 group-hover:translate-x-1" />
              </Link>
            </div>
          </Reveal>

          <Reveal delay={300}>
            <div className="mt-7 flex items-center gap-2 text-sm text-[color:var(--lp-text-3)]">
              <Globe className="h-4 w-4" />
              Trusted by revenue teams running 37 agents in production
            </div>
          </Reveal>
        </div>

        <Reveal delay={180} className="min-w-0">
          <InteractiveDemo />
        </Reveal>
      </div>
    </section>
  )
}

/* =========================================================================
   Value proposition
   ========================================================================= */

function ValueProposition() {
  const logos = [...STACK, ...STACK]
  return (
    <section id="platform" className="scroll-mt-24 py-20 lg:py-28">
      <div className="lp-container">
        <div className="max-w-3xl">
          <Reveal>
            <div className="mb-4 text-sm font-bold tracking-[-0.02em] text-[color:var(--lp-teal)]">→ Meet the revenue engine</div>
            <h2 className="lp-h2">The AI workspace for<br />modern go-to-market</h2>
            <p className="mt-5 text-base text-[color:var(--lp-text-2)]">Live simulation mode available today — no provider keys required.</p>
          </Reveal>
          <Reveal delay={120}>
            <Link to="/login" className="lp-btn lp-btn-primary lp-btn-sm mt-7">Join the waitlist<ArrowUpRight className="h-4 w-4" /></Link>
          </Reveal>
        </div>

        <div className="mt-14 grid gap-5 lg:grid-cols-2">
          {/* ecosystem */}
          <Reveal delay={60}>
            <article className="lp-card h-full p-7 lg:p-9" onMouseMove={cardGlow}>
              <h3 className="text-2xl font-extrabold tracking-[-0.02em]">Integrate with your entire GTM stack</h3>
              <p className="mt-3 max-w-xl text-sm leading-relaxed text-[color:var(--lp-text-2)]">
                Connect seamlessly to the systems revenue already runs on — Salesforce, HubSpot, Apollo, Google and Meta Ads, your warehouse.
                Automate go-to-market work with 200+ tools and specialist skills.
              </p>
              <div className="mt-8 space-y-2.5">
                {[0, 1].map((row) => (
                  <div key={row} className="lp-marquee">
                    <div className={`lp-marquee-track${row === 1 ? ' lp-marquee-track--rev' : ''}`}>
                      {logos.map((name, i) => (
                        <span key={`${name}-${i}`} className="lp-chip">
                          <span className="lp-chip-dot" style={{ background: 'var(--lp-grad)' }}>{name[0]}</span>
                          {name}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </article>
          </Reveal>

          {/* cost comparison */}
          <Reveal delay={140}>
            <article className="lp-card h-full p-7 lg:p-9" onMouseMove={cardGlow}>
              <h3 className="text-2xl font-extrabold tracking-[-0.02em]">Over 50% lower cost per pipeline dollar</h3>
              <p className="mt-3 max-w-xl text-sm leading-relaxed text-[color:var(--lp-text-2)]">
                Across a 107-task go-to-market benchmark, the closed loop completed the full set at less than half the cost of a
                comparable human-plus-point-tools workflow — at a higher qualification rate.
              </p>

              <div className="mt-8 grid grid-cols-2 gap-6">
                {[
                  { label: 'Qualification rate', quiet: 46, brand: 92, hero: 'Higher' },
                  { label: 'Total cost', quiet: 100, brand: 44, hero: '50%+ lower' },
                ].map((g) => (
                  <div key={g.label}>
                    <div className="lp-bar-pair">
                      <span className="lp-bar" style={{ height: `${g.quiet}%` }} />
                      <span className="lp-bar lp-bar--brand" style={{ height: `${g.brand}%` }} />
                    </div>
                    <div className="mt-3 text-[11px] font-bold uppercase tracking-[0.12em] text-[color:var(--lp-text-4)]">{g.label}</div>
                    <div className="mt-1 text-lg font-extrabold tracking-tight text-[color:var(--lp-teal)]">{g.hero}</div>
                  </div>
                ))}
              </div>

              <div className="mt-6 flex items-center gap-5 text-xs text-[color:var(--lp-text-3)]">
                <span className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full bg-white/20" />Point tools</span>
                <span className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full" style={{ background: 'var(--lp-grad)' }} />AI GTM OS</span>
              </div>
            </article>
          </Reveal>
        </div>
      </div>
    </section>
  )
}

/* =========================================================================
   Personas
   ========================================================================= */

function Personas() {
  const [active, setActive] = useState(0)
  const p = PERSONAS[active]
  return (
    <section className="py-20 lg:py-28">
      <div className="lp-container">
        <div className="flex flex-wrap items-end justify-between gap-6">
          <SectionHead title={<>Built for every<br />revenue motion</>} />
          <Reveal delay={80}>
            <span className="text-sm text-[color:var(--lp-text-3)]">Click one to preview</span>
          </Reveal>
        </div>

        <Reveal delay={60}>
          <div className="mt-9 flex flex-wrap gap-2.5" role="tablist" aria-label="Revenue personas">
            {PERSONAS.map((item, i) => (
              <button
                key={item.role}
                role="tab"
                aria-selected={i === active}
                data-active={i === active}
                className="lp-persona-tab"
                onClick={() => setActive(i)}
              >
                {item.short}
              </button>
            ))}
          </div>
        </Reveal>

        <Reveal delay={120}>
          <div key={active} className="lp-card mt-7 grid gap-8 p-7 lg:grid-cols-[0.85fr_1.15fr] lg:p-10" onMouseMove={cardGlow}>
            <div>
              <div className="text-xs font-bold uppercase tracking-[0.16em] text-[color:var(--lp-text-4)]">For {p.role}</div>
              <h3 className="mt-3 text-[1.75rem] font-extrabold leading-tight tracking-[-0.02em]">{p.need}</h3>
              <div className="mt-6 flex flex-wrap items-center gap-2">
                {p.workflow.map((w, i) => (
                  <span key={w} className="flex items-center gap-2">
                    <span className="lp-persona-pill">{w}</span>
                    {i < p.workflow.length - 1 && <ArrowRight className="h-3.5 w-3.5 text-[color:var(--lp-text-4)]" />}
                  </span>
                ))}
              </div>
              <p className="mt-6 text-sm leading-relaxed text-[color:var(--lp-text-2)]">{p.tagline}</p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              {p.features.map((f, i) => (
                <div
                  key={f.title}
                  className="rounded-2xl border border-[color:var(--lp-border)] bg-[color:var(--lp-fill-1)] p-5 transition-colors hover:border-[color:var(--lp-border-strong)]"
                  style={{ animation: `lpPixelIn .5s cubic-bezier(.2,.8,.2,1) ${i * 60}ms both` }}
                >
                  <div className="text-base font-bold tracking-[-0.01em]">{f.title}</div>
                  <p className="mt-2 text-sm leading-relaxed text-[color:var(--lp-text-3)]">{f.subtitle}</p>
                </div>
              ))}
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  )
}

/* =========================================================================
   Why choose — bento
   ========================================================================= */

function WhyChoose() {
  const tools = [...WHY_TOOLS, ...WHY_TOOLS]
  return (
    <section id="agents" className="scroll-mt-24 py-20 lg:py-28">
      <div className="lp-container">
        <SectionHead title="Why choose AI GTM OS?" />

        <div className="mt-12 grid gap-4 lg:grid-cols-[1.05fr_1fr]">
          {/* persona card */}
          <Reveal>
            <article className="lp-card relative h-full min-h-[420px] overflow-hidden" onMouseMove={cardGlow}>
              <div className="absolute inset-0" aria-hidden style={{ background: 'radial-gradient(85% 70% at 30% 10%, rgba(13,131,241,0.28), transparent 65%), radial-gradient(70% 70% at 85% 90%, rgba(3,245,143,0.20), transparent 65%)' }} />
              <div className="relative flex h-full flex-col justify-between p-7 lg:p-8">
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { name: 'Market Scout', bubble: 'EMEA demand up 38% in 30d.' },
                    { name: 'ICP Analyst', bubble: '412 accounts match · 71 in-market.' },
                    { name: 'Outbound', bubble: '3 sequence variants live.' },
                    { name: 'Attribution', bubble: 'Pipeline +$184k this week.' },
                  ].map((a, i) => (
                    <div key={a.name} className="rounded-2xl border border-white/10 bg-black/30 p-3 backdrop-blur-sm" style={{ marginTop: i % 2 ? '1.25rem' : 0 }}>
                      <div className="flex items-center gap-2">
                        <span className="lp-chip-dot" style={{ background: 'var(--lp-grad)' }}>{a.name[0]}</span>
                        <span className="text-xs font-bold">{a.name}</span>
                      </div>
                      <p className="mt-2 text-[11px] leading-snug text-[color:var(--lp-text-2)]">{a.bubble}</p>
                    </div>
                  ))}
                </div>
                <h3 className="lp-display mt-8 text-[2rem] leading-[0.95] lg:text-[2.5rem]">Your AI<br />revenue team</h3>
              </div>
            </article>
          </Reveal>

          <div className="grid gap-4">
            {/* robust tools */}
            <Reveal delay={80}>
              <article className="lp-card relative overflow-hidden p-7" onMouseMove={cardGlow}>
                <h3 className="text-xl font-extrabold tracking-[-0.02em]">Robust ecosystem of GTM tools</h3>
                <p className="mt-2 max-w-lg text-sm text-[color:var(--lp-text-2)]">
                  Hundreds of pre-trained revenue tools, with the domain knowledge and workflows already built in.
                </p>
                <div className="mt-6 space-y-2.5">
                  {[0, 1].map((row) => (
                    <div key={row} className="lp-marquee">
                      <div className={`lp-marquee-track${row === 1 ? ' lp-marquee-track--rev' : ''}`}>
                        {tools.map((t, i) => (
                          <span key={`${t}-${i}`} className="lp-chip">
                            <span className="lp-chip-dot" style={{ background: 'rgba(255,255,255,0.10)', color: 'var(--lp-teal)' }}>
                              <Terminal className="h-3 w-3" />
                            </span>
                            {t}
                            <span className="ml-1 rounded px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wide text-[color:var(--lp-teal)]" style={{ background: 'rgba(19,208,185,0.12)' }}>Official</span>
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </article>
            </Reveal>

            <div className="grid gap-4 sm:grid-cols-2">
              {/* models */}
              <Reveal delay={140}>
                <article className="lp-card h-full p-7" onMouseMove={cardGlow}>
                  <h3 className="text-lg font-extrabold tracking-[-0.02em]">Multiple models work together</h3>
                  <div className="mt-5 space-y-2">
                    {['Claude', 'GPT', 'Gemini', 'Simulation'].map((m, i) => (
                      <div key={m} className="flex items-center gap-2.5 rounded-xl border border-[color:var(--lp-border)] bg-[color:var(--lp-fill-1)] px-3 py-2">
                        <span className="h-2 w-2 rounded-full" style={{ background: i === 3 ? 'rgba(255,255,255,0.25)' : 'var(--lp-grad)' }} />
                        <span className="text-xs font-semibold">{m}</span>
                        <span className="ml-auto text-[10px] font-bold uppercase tracking-wide text-[color:var(--lp-text-4)]">{i === 3 ? 'offline' : 'routed'}</span>
                      </div>
                    ))}
                  </div>
                </article>
              </Reveal>

              {/* security */}
              <Reveal delay={200}>
                <article id="security" className="lp-card h-full scroll-mt-24 p-7" onMouseMove={cardGlow}>
                  <ShieldCheck className="h-7 w-7 text-[color:var(--lp-teal)]" />
                  <h3 className="mt-4 text-lg font-extrabold tracking-[-0.02em]">Security you trust</h3>
                  <p className="mt-2 text-sm leading-relaxed text-[color:var(--lp-text-2)]">
                    Sandboxed execution and least-privilege connectors. You approve every outward-facing action, and every run is audited.
                  </p>
                  <div className="mt-5 space-y-2">
                    {['Sandboxing & allowlists', 'Approval before action', 'Least-privilege OAuth'].map((s) => (
                      <div key={s} className="flex items-center gap-2 text-xs text-[color:var(--lp-text-3)]">
                        <Lock className="h-3.5 w-3.5 text-[color:var(--lp-green)]" />{s}
                      </div>
                    ))}
                  </div>
                </article>
              </Reveal>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

/* =========================================================================
   Automate anywhere
   ========================================================================= */

function Automate() {
  return (
    <section className="py-20 lg:py-28">
      <div className="lp-container">
        <SectionHead title="Run your growth from anywhere" />
        <div className="mt-12 grid gap-4 lg:grid-cols-3">
          {CHANNELS.map((c, i) => (
            <Reveal key={c.title} delay={i * 80}>
              <article className="lp-card flex h-full flex-col p-7 lg:p-8" onMouseMove={cardGlow}>
                <div className="text-xs font-bold uppercase tracking-[0.16em] text-[color:var(--lp-text-4)]">{c.title}</div>
                <h3 className="mt-3 text-2xl font-extrabold tracking-[-0.02em]">{c.tagline}</h3>
                <p className="mt-3 text-sm leading-relaxed text-[color:var(--lp-text-2)]">{c.desc}</p>
                <div className="mt-8 h-32 rounded-2xl border border-[color:var(--lp-border)]" style={{ background: 'linear-gradient(160deg, rgba(19,208,185,0.12), rgba(13,131,241,0.06) 60%, transparent)' }}>
                  <div className="flex h-full items-center justify-center">
                    <span className="lp-display text-5xl text-white/10">{String(i + 1).padStart(2, '0')}</span>
                  </div>
                </div>
              </article>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}

/* =========================================================================
   Loop chapters
   ========================================================================= */

function Loop() {
  return (
    <section className="py-20 lg:py-28">
      <div className="lp-container">
        <SectionHead title="See how the closed loop compounds" />
        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {CHAPTERS.map((c, i) => (
            <Reveal key={c.title} delay={i * 70}>
              <article className="lp-card h-full p-6" onMouseMove={cardGlow}>
                <div className="lp-display text-3xl lp-grad-text">{String(i + 1).padStart(2, '0')}</div>
                <h3 className="mt-4 text-base font-extrabold tracking-[-0.01em]">{c.title}</h3>
                <p className="mt-1.5 text-sm text-[color:var(--lp-text-3)]">{c.desc}</p>
              </article>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}

/* =========================================================================
   Testimonials
   ========================================================================= */

function Testimonials() {
  const row = [...TESTIMONIALS, ...TESTIMONIALS]
  return (
    <section className="overflow-hidden py-20 lg:py-28">
      <div className="lp-container">
        <SectionHead title="Real work. Real impact." />
      </div>
      <div className="mt-12 space-y-4">
        {[0, 1].map((r) => (
          <div key={r} className="lp-marquee">
            <div className={`lp-marquee-track${r === 1 ? ' lp-marquee-track--rev' : ''}`}>
              {row.map((t, i) => (
                <figure key={`${r}-${i}`} className="lp-card w-[330px] shrink-0 p-6">
                  <Sparkles className="h-4 w-4 text-[color:var(--lp-teal)]" />
                  <blockquote className="mt-3 text-sm leading-relaxed text-[color:var(--lp-text)]">“{t.quote}”</blockquote>
                  <figcaption className="mt-4 text-xs font-semibold text-[color:var(--lp-text-4)]">{t.role}</figcaption>
                </figure>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

/* =========================================================================
   FAQ
   ========================================================================= */

function Faq() {
  const [open, setOpen] = useState<number | null>(0)
  return (
    <section id="faq" className="scroll-mt-24 py-20 lg:py-28">
      <div className="lp-container grid gap-10 lg:grid-cols-[0.6fr_1fr] lg:gap-16">
        <SectionHead title="FAQ" sub="Everything teams ask before they connect live data." />
        <Reveal delay={80}>
          <div>
            {FAQ.map((item, i) => (
              <div key={item.q} className="lp-faq-item">
                <button className="lp-faq-q" onClick={() => setOpen(open === i ? null : i)} aria-expanded={open === i}>
                  {item.q}
                  {open === i ? <Minus className="h-5 w-5 shrink-0" /> : <Plus className="h-5 w-5 shrink-0 text-[color:var(--lp-text-3)]" />}
                </button>
                <div
                  className="overflow-hidden transition-all duration-300 ease-out"
                  style={{ maxHeight: open === i ? 320 : 0, opacity: open === i ? 1 : 0 }}
                >
                  <p className="pb-6 pr-10 text-[0.9375rem] leading-relaxed text-[color:var(--lp-text-2)]">{item.a}</p>
                </div>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  )
}

/* =========================================================================
   CTA + footer
   ========================================================================= */

function Cta() {
  return (
    <section className="pb-20 pt-10 lg:pb-28">
      <div className="lp-container">
        <Reveal>
          <div className="lp-cta-band px-7 py-20 text-center lg:px-16 lg:py-28">
            <div className="lp-prism" aria-hidden />
            <h2 className="lp-h2 relative">Slash overhead,<br /><span className="lp-grad-text">scale revenue</span></h2>
            <p className="relative mx-auto mt-6 max-w-xl text-base text-[color:var(--lp-text-2)]">
              Your agentic team for revenue growth — ready in minutes.
            </p>
            <div className="relative mt-9 flex flex-wrap justify-center gap-4">
              <Link to="/login" className="lp-btn lp-btn-primary">Start free<ArrowRight className="h-[18px] w-[18px]" /></Link>
              <Link to="/login" className="lp-btn lp-btn-ghost">Book a walkthrough</Link>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  )
}

function Footer() {
  return (
    <footer className="border-t border-[color:var(--lp-border)] py-14">
      <div className="lp-container grid gap-10 lg:grid-cols-[1.4fr_2fr]">
        <div>
          <div className="flex items-center gap-3">
            <span className="h-9 w-9 rounded-xl" style={{ background: 'var(--lp-grad)', boxShadow: 'var(--lp-teal-glow)' }} />
            <span className="text-base font-extrabold tracking-tight">AI GTM OS</span>
          </div>
          <p className="mt-4 max-w-xs text-sm leading-relaxed text-[color:var(--lp-text-3)]">
            One AI CMO orchestrating 37 specialist agents in a closed loop that keeps learning.
          </p>
        </div>
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
          {FOOTER.map((col) => (
            <div key={col.title}>
              <div className="text-xs font-bold uppercase tracking-[0.16em] text-[color:var(--lp-text-4)]">{col.title}</div>
              <ul className="mt-4 space-y-2.5">
                {col.links.map((l) => (
                  <li key={l}><span className="cursor-pointer text-sm text-[color:var(--lp-text-2)] transition-colors hover:text-white">{l}</span></li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
      <div className="lp-container mt-12 flex flex-wrap items-center justify-between gap-4 border-t border-[color:var(--lp-border)] pt-6 text-xs text-[color:var(--lp-text-4)]">
        <span>© {new Date().getFullYear()} AI GTM OS. All rights reserved.</span>
        <span>Built for revenue teams that would rather compound than coordinate.</span>
      </div>
    </footer>
  )
}

/* =========================================================================
   Nav + page
   ========================================================================= */

function Nav() {
  const [stuck, setStuck] = useState(false)
  const [menu, setMenu] = useState(false)
  useEffect(() => {
    const onScroll = () => setStuck(window.scrollY > 8)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header className="lp-nav" data-stuck={stuck}>
      <div className="lp-container flex h-[72px] items-center justify-between gap-6">
        <Link to="/landing" className="flex items-center gap-3">
          <span className="h-8 w-8 rounded-[10px]" style={{ background: 'var(--lp-grad)', boxShadow: 'var(--lp-teal-glow)' }} />
          <span className="text-base font-extrabold tracking-tight">AI GTM OS</span>
        </Link>

        <nav className="hidden items-center gap-8 md:flex">
          {NAV_LINKS.map((l) => <a key={l.label} href={l.href} className="lp-nav-link">{l.label}</a>)}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          <Link to="/login" className="lp-nav-link">Sign in</Link>
          <Link to="/login" className="lp-btn lp-btn-primary lp-btn-sm">Get started</Link>
        </div>

        <button className="md:hidden" onClick={() => setMenu(!menu)} aria-label={menu ? 'Close navigation menu' : 'Open navigation menu'}>
          {menu ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {menu && (
        <div className="border-t border-[color:var(--lp-border)] bg-[color:var(--lp-surface)] px-6 py-5 md:hidden">
          <div className="flex flex-col gap-4">
            {NAV_LINKS.map((l) => <a key={l.label} href={l.href} className="lp-nav-link" onClick={() => setMenu(false)}>{l.label}</a>)}
            <Link to="/login" className="lp-btn lp-btn-primary lp-btn-sm mt-2">Get started</Link>
          </div>
        </div>
      )}
    </header>
  )
}

export function LandingPage() {
  const root = useReveal<HTMLDivElement>()
  useEffect(() => { window.scrollTo(0, 0) }, [])
  return (
    <div ref={root} className="lp">
      <Nav />
      <Hero />
      <ValueProposition />
      <Personas />
      <WhyChoose />
      <Automate />
      <Loop />
      <Testimonials />
      <Faq />
      <Cta />
      <Footer />
    </div>
  )
}

export default LandingPage
