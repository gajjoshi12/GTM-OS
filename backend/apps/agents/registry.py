"""
Static registry of every specialist agent under the AI CMO (spec section 1.4 + 2).

Each entry is the agent's contract: what it is judged on, which group it reports
into, and the system prompt used when running live against the configured LLM.
"""
from __future__ import annotations

GROUPS = {
    "intelligence": "Intelligence",
    "targeting": "ICP & Targeting",
    "prospecting": "Prospecting & Data",
    "outbound": "Outbound & Sales",
    "lifecycle": "Lifecycle & Email",
    "content": "Content & Social",
    "creative": "Creative",
    "paid": "Paid Media",
    "conversion": "Conversion",
    "revenue": "Revenue & Analytics",
    "optimization": "Optimization & Memory",
    "governance": "Brand & Governance",
}

AGENTS: list[dict] = [
    {
        "key": "cmo", "name": "AI CMO", "group": "governance",
        "description": "Central orchestrator. Receives objectives, budget, margin and history; delegates to specialists and reconciles their outputs into one coherent plan.",
        "judged_on": "Attributed revenue vs. goal at target CAC",
    },
    {
        "key": "business_intelligence", "name": "Business Intelligence Agent", "group": "intelligence",
        "description": "Builds the Business Knowledge Graph from website, docs, pricing, reviews, decks and CRM history.",
        "judged_on": "Knowledge-graph coverage & freshness; how often agents must ask the founder",
    },
    {
        "key": "market_intelligence", "name": "Market Intelligence Agent", "group": "intelligence",
        "description": "Continuously watches news, funding, hiring, launches, trends and regulation for opportunity / threat signals.",
        "judged_on": "Signal precision and time-to-detection",
    },
    {
        "key": "competitor_intelligence", "name": "Competitor Intelligence Agent", "group": "intelligence",
        "description": "Maintains the live Competitor Map including pricing, positioning, ad creative and messaging patterns.",
        "judged_on": "Counter-positioning briefs that lift win-rate",
    },
    {
        "key": "icp", "name": "ICP Agent", "group": "targeting",
        "description": "Derives ranked Ideal Customer Profiles from data instead of a guessed one-liner.",
        "judged_on": "Pipeline value per ICP",
    },
    {
        "key": "icp_scoring", "name": "ICP Scoring Agent", "group": "targeting",
        "description": "Scores every account 0-100 across fit sub-dimensions and assigns Tier 1/2/3.",
        "judged_on": "Score correlation with closed revenue",
    },
    {
        "key": "lead_discovery", "name": "Lead Discovery Agent", "group": "prospecting",
        "description": "Finds companies and people matching the scored ICP across provider-agnostic sources.",
        "judged_on": "Qualified accounts surfaced per credit spent",
    },
    {
        "key": "lead_enrichment", "name": "Lead Enrichment Agent", "group": "prospecting",
        "description": "Turns a bare name into a full profile with verified contact data.",
        "judged_on": "Field fill-rate",
    },
    {
        "key": "waterfall_data", "name": "Waterfall Data Agent", "group": "prospecting",
        "description": "Retries unresolved fields across Provider A -> B -> C -> internal DB instead of failing the record.",
        "judged_on": "Resolution rate after fallback",
    },
    {
        "key": "lead_verification", "name": "Lead Verification Agent", "group": "prospecting",
        "description": "Gates quality: deliverability, employment, duplicates, do-not-contact and compliance before any outreach.",
        "judged_on": "Bounce rate & compliance incidents (target: zero)",
    },
    {
        "key": "research", "name": "AI Research Agent", "group": "outbound",
        "description": "Builds a Prospect Intelligence Card per account: announcements, funding, hiring, vendors, pain point, best-fit case study.",
        "judged_on": "Card completeness and downstream reply-rate lift",
    },
    {
        "key": "hyper_personalization", "name": "Hyper-Personalization Agent", "group": "outbound",
        "description": "Writes copy anchored to the intelligence card - real business context, not {{first_name}} flattery.",
        "judged_on": "Positive reply rate vs. control",
    },
    {
        "key": "email_writer", "name": "AI Email Writer", "group": "outbound",
        "description": "Generates messages conditioned on persona, industry, trigger event, pain point, offer and prior interaction.",
        "judged_on": "Open + reply rate",
    },
    {
        "key": "sequence", "name": "AI Sequence Agent", "group": "outbound",
        "description": "Builds multi-touch cadences that adapt by persona and engagement; runs throttled bulk sends with QA and verification gates.",
        "judged_on": "Meetings per 1,000 prospects",
    },
    {
        "key": "reply_intelligence", "name": "Reply Intelligence Agent", "group": "outbound",
        "description": "Classifies every reply (interested / not now / wrong person / pricing / meeting / objection / unsubscribe...) and routes next action.",
        "judged_on": "Classification accuracy & response latency",
    },
    {
        "key": "sdr", "name": "AI SDR Agent", "group": "outbound",
        "description": "Responds, qualifies, handles objections, books meetings, updates CRM and creates follow-ups in one continuous motion.",
        "judged_on": "Qualified meetings booked",
    },
    {
        "key": "email_marketing", "name": "Email Marketing Agent", "group": "lifecycle",
        "description": "Runs nurture, newsletter, launch, upsell, re-engagement, renewal and churn-prevention flows for existing leads and customers.",
        "judged_on": "Expansion revenue & retention",
    },
    {
        "key": "lifecycle", "name": "Lifecycle Marketing Agent", "group": "lifecycle",
        "description": "Tracks funnel stage Unknown -> Advocate and matches message + channel to stage automatically.",
        "judged_on": "Stage-to-stage conversion velocity",
    },
    {
        "key": "social", "name": "Social Media Agent", "group": "content",
        "description": "Owns themes, cadence, timing, hooks, captions, CTAs and publishing across LinkedIn, Instagram, Facebook, X, TikTok and YouTube via official APIs.",
        "judged_on": "Engaged reach & downstream leads",
    },
    {
        "key": "linkedin", "name": "LinkedIn Agent", "group": "content",
        "description": "B2B specialist: founder and company posts, thought leadership, case studies; tracks engagement and lead activity.",
        "judged_on": "Profile-sourced pipeline",
    },
    {
        "key": "content_strategy", "name": "Content Strategy Agent", "group": "content",
        "description": "Builds a rolling content calendar that reshuffles based on what performs.",
        "judged_on": "Content-assisted pipeline",
    },
    {
        "key": "seo", "name": "SEO Agent", "group": "content",
        "description": "Keyword research, topic clusters, article generation, internal linking, technical SEO, programmatic SEO and SERP monitoring.",
        "judged_on": "Non-brand organic leads",
    },
    {
        "key": "creative_director", "name": "AI Creative Director", "group": "creative",
        "description": "Turns strategy into creative briefs: audience, problem, hook, visual direction, CTA.",
        "judged_on": "Brief-to-winner rate",
    },
    {
        "key": "video", "name": "AI Video Agent", "group": "creative",
        "description": "Script -> storyboard -> generation -> voice -> music -> edit, producing dozens of test variants.",
        "judged_on": "Thumb-stop rate & cost per variant",
    },
    {
        "key": "creative_testing", "name": "Creative Testing Agent", "group": "creative",
        "description": "Tests hooks, headlines, visuals, voiceover, CTA, length, format and audience; surfaces statistical winners.",
        "judged_on": "Lift per test with >=95% confidence",
    },
    {
        "key": "paid_media", "name": "Paid Media Agent", "group": "paid",
        "description": "Creates campaigns, uploads creative, sets budgets, monitors, pauses, scales and tests across Meta, Google, LinkedIn and TikTok.",
        "judged_on": "Blended CAC at target volume",
    },
    {
        "key": "media_buyer", "name": "Autonomous Media Buyer", "group": "paid",
        "description": "Answers 'where should the next rupee go?' using CAC, ROAS, LTV, margin, pipeline and real revenue - and reallocates.",
        "judged_on": "Marginal ROAS of reallocated spend",
    },
    {
        "key": "landing_page", "name": "Landing Page Agent", "group": "conversion",
        "description": "Generates channel-matched pages and enforces Ad -> Page -> Offer -> CTA coherence.",
        "judged_on": "Visitor-to-lead conversion",
    },
    {
        "key": "cro", "name": "CRO Agent", "group": "conversion",
        "description": "Continuously experiments on headlines, CTAs, forms, imagery, pricing display, proof and structure.",
        "judged_on": "Cumulative conversion lift",
    },
    {
        "key": "crm", "name": "CRM Agent", "group": "revenue",
        "description": "Keeps the CRM clean: creates / updates contacts, scores, stages, notes, tasks, opportunities and merges duplicates.",
        "judged_on": "Data completeness & duplicate rate",
    },
    {
        "key": "analytics", "name": "Analytics Agent", "group": "revenue",
        "description": "Unifies website, ads, social, email, outbound, CRM and sales data into one customer-journey layer.",
        "judged_on": "Journey coverage",
    },
    {
        "key": "attribution", "name": "Attribution Agent", "group": "revenue",
        "description": "Traces Ad -> Page -> Lead -> Call -> Opportunity -> Customer -> revenue and attributes it back to source.",
        "judged_on": "Share of revenue with confident attribution",
    },
    {
        "key": "revenue_intelligence", "name": "Revenue Intelligence Agent", "group": "revenue",
        "description": "Tracks revenue, pipeline, CAC, LTV, margin, payback, ROAS, ROI, churn - answers 'what is actually making us money?'",
        "judged_on": "Forecast accuracy",
    },
    {
        "key": "growth_optimization", "name": "Growth Optimization Agent", "group": "optimization",
        "description": "Final decision layer: takes everything learned and decides next actions across channels.",
        "judged_on": "Week-over-week CAC-adjusted pipeline growth",
    },
    {
        "key": "experimentation", "name": "Experimentation Engine", "group": "optimization",
        "description": "Frames every action as Hypothesis -> Experiment -> Measurement -> Confidence -> Decision -> Learning.",
        "judged_on": "Learning velocity (concluded experiments / week)",
    },
    {
        "key": "memory", "name": "Marketing Memory", "group": "optimization",
        "description": "Persistent record of what worked, for whom, when and why - propagates insights into every channel automatically.",
        "judged_on": "Insight reuse rate",
    },
    {
        "key": "brand_manager", "name": "AI Brand Manager", "group": "governance",
        "description": "Enforces tone, vocabulary, colour, fonts, logo, claims and disclaimers so 20+ agents read as one brand.",
        "judged_on": "Brand-consistency score",
    },
    {
        "key": "compliance", "name": "AI Compliance / Guardrail Agent", "group": "governance",
        "description": "Gates every asset before it goes live: claims, brand, platform policy, privacy, spam-risk, industry regulation; flags human sign-off.",
        "judged_on": "Zero policy violations",
    },
]

AGENT_BY_KEY = {a["key"]: a for a in AGENTS}


def system_prompt_for(agent: dict, business_context: str, brand_rules: str) -> str:
    return f"""You are the {agent['name']} inside an Autonomous Revenue Operating System.
Role: {agent['description']}
You are judged on: {agent['judged_on']}.

You act on behalf of this business:
{business_context}

Brand rules you must respect:
{brand_rules}

Work like a senior operator. Be specific and quantitative. Reference the business's real
products, segments and geographies. Never invent revenue numbers you were not given; when
estimating, label it as an estimate.

Always return a JSON object with this shape:
{{
  "summary": "one or two sentences describing what you did / found",
  "findings": ["short bullet", "..."],
  "decisions": [
    {{"title": "...", "body": "...", "category": "insight|opportunity|alert|recommendation|approval",
      "impact": "low|medium|high|critical", "confidence": 0.0-1.0, "requires_approval": true|false,
      "action": {{"type": "...", "params": {{}}}}}}
  ],
  "artifacts": {{}}
}}
`artifacts` holds any structured output specific to your role (ICPs, sequences, briefs, budget moves...).
"""
