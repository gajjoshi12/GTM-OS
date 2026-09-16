# AI GTM OS — Autonomous Revenue Operating System

> Connect your business, set a revenue goal, give the AI a budget — the platform runs the
> entire marketing & growth department in one closed loop that keeps learning.

Built from `AI-GTM-OS-Product-Specification.docx`: an **AI CMO** orchestrating **37 specialist
agents** (intelligence → ICP → prospecting → outbound → content → paid → creative → conversion →
CRM → attribution → optimization → memory → brand/compliance), a **CEO Command Centre**, a
natural-language **command bar**, the **three-mode human control model**, and a
**provider-agnostic connector framework** with waterfall fallback.

```
Understand → Strategize → Find customers → Create → Launch → Sell → Measure → Learn → Optimize → Scale → Repeat
```

---

## Stack

| Layer | Tech |
|---|---|
| Backend | Django 5 · Django REST Framework · SimpleJWT · Celery (optional) · SQLite by default / Postgres via `DATABASE_URL` |
| AI | Anthropic SDK · `claude-opus-5` (adaptive thinking, server-side refusal fallbacks) · `claude-sonnet-5` as bulk worker |
| Frontend | React 18 · Vite · TypeScript · Tailwind · Framer Motion · Recharts · TanStack Query · Zustand |
| Connectors | 60+ providers (Meta, Google Ads, LinkedIn, TikTok, Apollo, HubSpot, Instantly, Stripe, GA4, Semrush, …) |

Every agent runs in **simulation mode** when its keys are blank, so the whole system is demoable
with zero credentials. Add `ANTHROPIC_API_KEY` and agents switch to live reasoning.

---

## Quick start (local, 3 minutes)

```bash
# 0. env
cp .env.example .env            # fill in only what you connect — blanks are fine

# 1. backend
cd backend
python -m venv .venv && .venv/Scripts/activate      # (Windows)   |  source .venv/bin/activate (mac/linux)
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo      # demo workspace "SkyBag Systems" with 120 days of data
python manage.py runserver 8000

# 2. frontend (new terminal)
cd frontend
npm install
npm run dev                     # http://localhost:5173  (proxies /api → :8000)
```

**Login:** `founder@demo.gtm` / `demo12345` (pre-filled on the login screen).
Django admin: http://localhost:8000/admin/ (same credentials).

Reset the demo any time: `python manage.py seed_demo --reset`.

### Docker

```bash
cp .env.example .env
docker compose up --build       # web :5173 · api :8000 · postgres · redis · celery worker
```

---

## What's inside

### Backend — `backend/`

```
config/            settings (reads repo-root .env), urls, celery
ai/client.py       Anthropic wrapper: opus-5 + adaptive thinking + fallbacks; simulation when no key
apps/
  accounts/        email-login users, workspaces (tenants), memberships, JWT
  core/            BusinessProfile (founder brief + derived plan), ControlSettings (3 modes + guardrails), BrandGuidelines
  agents/          registry.py (37 agent contracts) · orchestrator.py (AI CMO) · simulations.py · Decision feed · Command bar
  knowledge/       Knowledge graph entities, Competitor map, Market signals
  leads/           ICPs, Companies (fit score + tier), Contacts (intelligence cards, waterfall enrichment log, verification)
  outbound/        Sequences (multi-touch cadences), Enrollments, Messages, Replies (classified) + AI SDR responses
  campaigns/       Campaigns, Creatives (variants + compliance), BudgetAllocations (media buyer), Landing pages, Content calendar, SEO keywords
  analytics/       DailyMetric (unified journey layer), Attribution touches, Revenue events, Experiments, Marketing Memory
  integrations/    Connector framework: registry of 60+ providers, encrypted credentials, adapters with live pings
```

Key endpoints (all under `/api/`, JWT bearer auth):

| Endpoint | Purpose |
|---|---|
| `POST auth/login/` · `auth/register/` · `GET auth/me/` | Auth |
| `POST core/onboarding/` | Founder sentence → derived GTM plan + kicks off intelligence agents |
| `GET/PATCH core/controls/` · `core/brand/` · `core/business/` | Human control model, brand rules, business profile |
| `GET analytics/dashboard/?days=30` | Everything the Command Centre needs in one call |
| `GET agents/org-chart/` · `POST agents/agents/{id}/run/` · `POST agents/agents/run_all/` | Agent hierarchy, run one, run the full closed loop |
| `GET agents/decisions/` · `POST …/{id}/approve|reject|ask/` | AI Decisions feed with Approve / Reject / Ask AI |
| `POST agents/commands/` `{text}` | Natural-language command bar → AI CMO plans & delegates |
| `leads/icps/` · `leads/companies/` · `leads/contacts/` | ICP → discovery → scoring → enrichment → verification |
| `outbound/sequences/` · `outbound/replies/` | Cadences, reply intelligence, AI SDR |
| `campaigns/campaigns/channels/` · `campaigns/allocations/` · `campaigns/creatives/` | Channel scorecard, media-buyer log, creative lab |
| `analytics/attribution/` · `analytics/revenue-intelligence/` · `analytics/experiments/` · `analytics/memory/` | Attribution, revenue intel, experimentation engine, marketing memory |
| `integrations/` · `POST integrations/{key}/` · `POST integrations/{key}/test/` | Connector list, save encrypted credentials, live connection test |

### Frontend — `frontend/src/`

| Route | Screen |
|---|---|
| `/login` | Auth (demo creds pre-filled) |
| `/onboarding` | One-sentence founder input → animated plan derivation |
| `/` | **CEO Command Centre** — KPIs, revenue vs spend, goal, decision feed, CAC by channel, agents at work, funnel, live activity |
| `/agents` | AI CMO + 36 specialists in groups; run any agent; run logs & findings |
| `/intelligence` | Interactive knowledge graph · competitor map · market signals |
| `/prospects` | ICPs · scored/tiered accounts · contacts with intelligence cards + waterfall enrichment |
| `/outbound` | Sequences (Day 1/3/6/10/15 cadence) · reply inbox with classification + AI SDR drafts |
| `/campaigns` | Channel scorecard · campaigns · creative lab (variants, winners, compliance) · media-buyer reallocation log |
| `/content` | Rolling content calendar · SEO keyword clusters & SERP movement |
| `/conversion` | Channel-matched landing pages with CRO experiments |
| `/experiments` | Experimentation engine · Marketing Memory insights |
| `/analytics` | Revenue intelligence (LTV:CAC, payback, ROI) · multi-touch attribution · won journeys |
| `/integrations` | 60+ connectors by category; paste keys (encrypted) or use `.env`; live test |
| `/settings` | Control mode (copilot / approval / full autonomy), spend caps, permissions, per-agent overrides, brand rules |

Press **⌘K / Ctrl+K** anywhere to open the command bar:
*"Find me 5,000 European companies that match our ICP and launch an outbound campaign."*

---

## Environment / API keys

**Start with [`AI-GTM-OS-API-Acquisition.xlsx`](AI-GTM-OS-API-Acquisition.xlsx)** — the working tracker for getting
every key: 67 providers with difficulty, lead time, indicative cost, step-by-step signup instructions, gotchas and a
status dropdown, plus a 30-day plan, the non-API prerequisites that gate everything, a cost model and a map of all
193 `.env` variables to the provider that fills them.

Regenerate it after editing the catalogue:

```bash
backend/.venv/Scripts/python tools/generate_api_workbook.py    # data lives in tools/api_catalog.py
```

All keys live in the repo-root `.env` — see **`.env.example`** for the full draft, grouped by:

1. Core platform (Django, DB, Redis, JWT, credential encryption)
2. AI / LLM providers (Anthropic primary; embeddings, vector store, image/video/voice generation)
3. Paid media — Meta Ads, Google Ads, LinkedIn, TikTok, X
4. Organic social — YouTube, TikTok content, Ayrshare/Buffer
5. Prospecting & enrichment (waterfall order) — Apollo, Clearbit, PDL, Hunter, ZoomInfo, Crunchbase, BuiltWith + email verification
6. Outbound sending — Instantly / Smartlead / lemlist / SMTP; Gmail / Outlook inbox; Calendly / Cal.com
7. Email marketing / lifecycle / WhatsApp / SMS
8. CRM — HubSpot, Salesforce, Pipedrive
9. Analytics & revenue — GA4, Search Console, Stripe, Shopify, Segment, PostHog, Mixpanel, warehouses
10. SEO & research — Semrush, Ahrefs, SerpApi, DataForSEO, Firecrawl, Tavily, Exa, NewsAPI, CMS
11. Landing pages / CRO / hosting
12. Storage, alerts, observability
13. Human-control defaults
14. Frontend `VITE_*` vars (put in `frontend/.env`)

The **Integrations** screen shows, per provider, which `.env` keys it reads, whether it's configured,
and lets you paste credentials instead (encrypted with `CREDENTIALS_ENCRYPTION_KEY`).

---

## How the agents run

`apps/agents/orchestrator.py`

- `run_agent(workspace, key, payload)` — builds the agent's system prompt from `registry.py` + the
  workspace's business context + brand rules, calls Claude (JSON contract: `summary`, `findings`,
  `decisions`, `artifacts`) and materialises decision cards. Without an API key it uses
  `simulations.py` (deterministic, anchored to the business profile).
- `interpret_command(...)` — the command bar: AI CMO picks intent + agent sequence (rule-based fallback), runs them, returns a founder-facing response.
- `derive_plan(business)` — onboarding: founder sentence → segments, personas, geos, messaging, channel mix, offers, landing pages, experiment backlog, monthly targets.
- `resolve_decision(...)` — Approve applies the action (budget reallocation, sequence launch, campaign scale…), Reject records it, Ask AI answers in-thread.
- Control mode is enforced when decisions are created: **copilot** → everything needs a human; **approval** → as the agent proposes; **full autonomy** → auto-executed unless explicitly gated (compliance, spend caps).

With `REDIS_URL` set, agent jobs can be dispatched to the Celery worker; without it they run inline.

---

## Next steps to go live

1. Set `ANTHROPIC_API_KEY` → agents reason for real.
2. Connect one channel pair first (spec's advice): **Apollo + Instantly** (outbound) and **Google Ads** (paid).
3. Wire the write-side adapter methods in `apps/integrations/providers/adapters.py` (create campaign, push sequence, sync CRM) — read-side pings are already there.
4. Point `DATABASE_URL` at Postgres and `REDIS_URL` at Redis for background runs.
