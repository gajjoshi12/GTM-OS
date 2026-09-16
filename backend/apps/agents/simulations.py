"""
Deterministic simulated outputs for every agent.

Used when the LLM provider key is blank (or a provider is not connected) so the whole
closed loop stays demoable end-to-end. Every simulation is anchored to the
workspace's business profile so the output reads as the customer's own business.
"""
from __future__ import annotations

import random
from typing import Any


def _ctx(business) -> dict[str, Any]:
    if business is None:
        return {"company": "Your company", "industry": "B2B SaaS", "geo": "Europe", "currency": "INR", "product": "your product"}
    geos = business.target_geographies or ["Europe"]
    return {
        "company": business.company_name,
        "industry": business.industry or "B2B SaaS",
        "geo": geos[0] if geos else "Europe",
        "geos": geos,
        "currency": business.currency,
        "product": (business.description or "your product").split(".")[0][:80],
        "goal": float(business.revenue_goal or 0),
        "budget": float(business.marketing_budget or 0),
        "acv": float(business.average_deal_size or 0),
    }


def simulate(agent_key: str, business, payload: dict | None = None) -> dict:
    payload = payload or {}
    c = _ctx(business)
    rnd = random.Random(f"{agent_key}:{c['company']}")
    fn = SIMULATIONS.get(agent_key, _generic)
    return fn(c, rnd, payload)


# --------------------------------------------------------------------------- helpers
def _decision(title, body, category="recommendation", impact="medium", confidence=0.82, requires_approval=True, action=None, metrics=None):
    return {
        "title": title, "body": body, "category": category, "impact": impact, "confidence": confidence,
        "requires_approval": requires_approval, "action": action or {}, "metrics": metrics or {},
    }


def _generic(c, rnd, p):
    return {
        "summary": f"Completed a scheduled pass for {c['company']} and refreshed working state.",
        "findings": ["No anomalies detected", "Inputs current as of this run"],
        "decisions": [],
        "artifacts": {},
    }


# --------------------------------------------------------------------------- agents
def cmo(c, rnd, p):
    return {
        "summary": f"Reconciled specialist outputs into a single plan for {c['company']}: outbound + paid as the wedge, content and SEO compounding in parallel.",
        "findings": [
            f"Goal of {c['currency']} {c['goal']:,.0f} implies ~{max(1, int(c['goal'] / max(c['acv'], 1)))} new customers at current ACV",
            "Outbound has the lowest modelled CAC; paid search is the fastest inbound channel to test",
            "Two Tier-1 ICPs cover ~70% of addressable pipeline",
        ],
        "decisions": [
            _decision("Adopt Outbound + Google Search as the launch wedge",
                      "Model shows the fastest path to pipeline is 2 outbound sequences against ICP #1 and #2 plus a high-intent search campaign. Meta reserved for retargeting only in month 1.",
                      "recommendation", "high", 0.86, True, {"type": "adopt_plan", "params": {"wedge": ["outbound", "google_search"]}}),
        ],
        "artifacts": {},
    }


def business_intelligence(c, rnd, p):
    return {
        "summary": f"Rebuilt the Business Knowledge Graph for {c['company']}: 42 entities across product, customer, problem, differentiation, pricing, objections and outcomes.",
        "findings": [
            "Website + pricing page + 6 case studies crawled; 3 sales decks parsed",
            "Coverage 91% - missing: churn reasons, partner ecosystem",
            f"Primary outcome claim: measurable operational cost reduction for {c['industry']} buyers",
        ],
        "decisions": [
            _decision("Knowledge gap: churn reasons missing", "No source describes why customers churn. Connect CRM closed-lost reasons or answer 3 questions so the messaging agents can pre-empt objections.",
                      "alert", "medium", 0.9, False, {"type": "request_context", "params": {"fields": ["churn_reasons", "partners"]}}),
        ],
        "artifacts": {"coverage": 0.91, "entities": 42},
    }


def market_intelligence(c, rnd, p):
    return {
        "summary": f"Scanned 1,240 sources. 3 high-relevance signals for {c['industry']} in {c['geo']}.",
        "findings": [
            f"Three competitors have started targeting {c['geo']} buyers in the last 30 days",
            f"Capex for modernization projects in {c['industry']} is rising in the Middle East - emerging opportunity",
            "Search interest for the core category is up 18% quarter over quarter",
        ],
        "decisions": [
            _decision(f"Emerging opportunity: Middle East {c['industry']} modernization",
                      "Investment announcements up 34% YoY. Recommend spinning up ICP #3 (GCC region) and a 200-account discovery run.",
                      "opportunity", "high", 0.78, True, {"type": "create_icp", "params": {"region": "GCC"}}),
        ],
        "artifacts": {"sources_scanned": 1240},
    }


def competitor_intelligence(c, rnd, p):
    return {
        "summary": "Competitor Map refreshed: 6 tracked competitors, 2 changed pricing, 1 launched a new ad message.",
        "findings": [
            "Competitor A now leads with a '30% reduction in mishandled operations' claim across LinkedIn ads",
            "Competitor B raised entry pricing by 12%; opening for a value-led counter-offer",
            "Competitor C hiring 9 enterprise AEs in Europe - expect increased outbound pressure",
        ],
        "decisions": [
            _decision("Counter-position against Competitor A's '30% reduction' claim",
                      "Their claim is unqualified. Brief: lead with audited customer outcomes and a savings calculator CTA. Applies to LinkedIn + landing page variant B.",
                      "recommendation", "high", 0.84, True, {"type": "create_creative_brief", "params": {"angle": "audited_outcomes"}}),
        ],
        "artifacts": {},
    }


def icp(c, rnd, p):
    return {
        "summary": "Derived and ranked 3 ICPs from knowledge graph, CRM wins and market signals.",
        "findings": [
            f"ICP #1: {c['geo']} enterprises, 500+ employees, active modernization project, high intent",
            "ICP #2: mid-market operators with legacy incumbent vendor and upcoming renewal",
            "ICP #3 (emerging): GCC region greenfield projects",
        ],
        "decisions": [
            _decision("Approve ICP #1 and #2 for outbound", "Both ICPs score above 80 on data fit and account for 70% of past won revenue.",
                      "approval", "high", 0.9, True, {"type": "approve_icps", "params": {"ranks": [1, 2]}}),
        ],
        "artifacts": {},
    }


def icp_scoring(c, rnd, p):
    n = p.get("count", 4200)
    return {
        "summary": f"Scored {n:,} accounts: {int(n*0.11):,} Tier 1, {int(n*0.27):,} Tier 2, remainder Tier 3.",
        "findings": ["Buying-signal sub-score is the strongest predictor of reply", "Geography fit re-weighted after Middle East signal"],
        "decisions": [
            _decision(f"{int(n*0.11):,} new prospects match ICP #2", "Fresh Tier-1 accounts ready for enrichment and sequencing.", "insight", "medium", 0.88, False),
        ],
        "artifacts": {"tier1": int(n*0.11), "tier2": int(n*0.27)},
    }


def lead_discovery(c, rnd, p):
    n = p.get("count", 5000)
    return {
        "summary": f"Discovered {n:,} candidate accounts in {p.get('region', c['geo'])} across Apollo, directories and CRM; deduplicated to {int(n*0.86):,}.",
        "findings": ["Apollo resolved 62%, directories 24%, CRM re-activation 14%", "No single provider load-bearing (max share 62%)"],
        "decisions": [],
        "artifacts": {"discovered": n, "unique": int(n*0.86)},
    }


def lead_enrichment(c, rnd, p):
    return {
        "summary": "Enriched 1,860 contacts: title, LinkedIn, verified email, tech stack, funding and hiring signals.",
        "findings": ["Email fill-rate 88% after waterfall (Apollo 61% -> Clearbit +14% -> PDL +9% -> Hunter +4%)", "Phone resolved for 31% where legitimate"],
        "decisions": [],
        "artifacts": {"fill_rate": 0.88},
    }


def waterfall_data(c, rnd, p):
    return {
        "summary": "Recovered 512 records that failed on the primary provider by cascading to secondary providers and the internal graph.",
        "findings": ["Provider B resolved 58% of fallbacks", "Internal DB resolved 9% - prior relationship data"],
        "decisions": [],
        "artifacts": {},
    }


def lead_verification(c, rnd, p):
    return {
        "summary": "Verified 1,860 contacts: 1,644 valid, 121 risky (held), 95 invalid (purged). 0 do-not-contact violations.",
        "findings": ["Duplicate rate 2.1% - merged", "14 contacts flagged as changed employer - re-enriched"],
        "decisions": [
            _decision("95 invalid records purged before outbound", "Bad data auto-purged per policy; nothing was sent to outbound.", "insight", "low", 0.97, False),
        ],
        "artifacts": {"valid": 1644, "risky": 121, "invalid": 95},
    }


def research(c, rnd, p):
    return {
        "summary": "Built 340 Prospect Intelligence Cards with announcements, funding, hiring, current vendor and best-fit case study.",
        "findings": ["61% of Tier-1 accounts have a public modernization or expansion trigger", "Incumbent vendor identified for 74%"],
        "decisions": [],
        "artifacts": {"cards": 340},
    }


def hyper_personalization(c, rnd, p):
    return {
        "summary": "Wrote 340 first-touch messages anchored to intelligence cards; AI QA passed 322, 18 sent back for rewrite.",
        "findings": ["Trigger-event openers outperform generic by an estimated 2.1x", "Avg. 38 words per opener"],
        "decisions": [],
        "artifacts": {},
    }


def email_writer(c, rnd, p):
    return {
        "summary": "Generated 5-step copy set for persona 'Head of Operations' with cost-saving angle.",
        "findings": ["Subject lines kept under 6 words", "CTA: 15-minute walkthrough"],
        "decisions": [],
        "artifacts": {
            "steps": [
                {"day": 1, "type": "opener", "subject": "{{trigger_event}} at {{company}}", "body": "Saw the news on {{trigger_event}}. Teams like {{peer_customer}} used that moment to cut operational cost by {{proof_metric}}. Worth a 15-minute look at how?"},
                {"day": 3, "type": "insight", "subject": "one number", "body": "One thing most {{persona}}s miss: {{insight}}. Happy to share the benchmark we built for {{industry}}."},
                {"day": 6, "type": "case_study", "subject": "how {{peer_customer}} did it", "body": "Short case study attached - same incumbent vendor as you ({{incumbent}}). 90-day payback."},
                {"day": 10, "type": "alt_value", "subject": "different angle", "body": "If cost is not the priority, the other reason teams switch is {{alt_value}}. Which matters more this year?"},
                {"day": 15, "type": "breakup", "subject": "closing the loop", "body": "Will stop here. If timing changes, reply 'later' and I will check back next quarter."},
            ]
        },
    }


def sequence(c, rnd, p):
    return {
        "summary": "Built a 5-touch adaptive cadence (Day 1/3/6/10/15) and enrolled 1,644 verified contacts with throttled sending at 150/day.",
        "findings": ["Cadence branches on open/no-open at step 2", "LinkedIn touch inserted for Tier-1 only"],
        "decisions": [
            _decision("Approve sequence launch: ICP #1 / Head of Operations", "1,644 verified contacts, compliance gate passed, daily cap 150.", "approval", "high", 0.9, True,
                      {"type": "launch_sequence", "params": {"contacts": 1644}}),
        ],
        "artifacts": {},
    }


def reply_intelligence(c, rnd, p):
    return {
        "summary": "Classified 128 replies: 31 interested, 14 meeting requests, 22 not now, 9 wrong person, 6 pricing, 41 other.",
        "findings": ["Objection cluster: 'already have a vendor' - routed to alt-value step", "9 wrong-person replies produced 7 referrals"],
        "decisions": [
            _decision("17 Tier-1 prospects responded to the modernization campaign", "Positive intent detected; AI SDR is qualifying and proposing times.", "insight", "high", 0.93, False),
        ],
        "artifacts": {},
    }


def sdr(c, rnd, p):
    return {
        "summary": "Handled 45 conversations: qualified 26, booked 12 meetings, logged all to CRM, created 19 follow-up tasks.",
        "findings": ["Median time-to-first-response 4 minutes", "Top objection handled: integration effort"],
        "decisions": [],
        "artifacts": {"meetings": 12},
    }


def email_marketing(c, rnd, p):
    return {
        "summary": "Ran lifecycle sends: 4 nurture flows, 1 newsletter, 1 renewal-risk flow. 3 upsell opportunities surfaced.",
        "findings": ["Renewal flow recovered 2 at-risk accounts", "Newsletter CTR 4.8%"],
        "decisions": [],
        "artifacts": {},
    }


def lifecycle(c, rnd, p):
    return {
        "summary": "Re-staged 612 contacts across the funnel; 38 promoted to MQL, 11 to SQL.",
        "findings": ["Visitor -> Lead conversion improved to 3.1%", "SQL stall detected at 'pricing sent' - triggered SDR follow-up"],
        "decisions": [],
        "artifacts": {},
    }


def social(c, rnd, p):
    return {
        "summary": "Scheduled 14 posts across LinkedIn, Instagram and X for the week; aligned to the content calendar themes.",
        "findings": ["Best posting window: Tue/Thu 09:00 local", "Carousel format leads engagement"],
        "decisions": [
            _decision("Approve this week's social calendar (14 posts)", "All posts passed brand + compliance checks.", "approval", "low", 0.9, True, {"type": "publish_social", "params": {"count": 14}}),
        ],
        "artifacts": {},
    }


def linkedin(c, rnd, p):
    return {
        "summary": "Drafted 5 founder posts and 3 company posts; last week's founder POV drove 214 profile visits and 6 inbound leads.",
        "findings": ["Founder POV posts convert 3x better than company posts", "Case-study format: strongest save rate"],
        "decisions": [],
        "artifacts": {},
    }


def content_strategy(c, rnd, p):
    return {
        "summary": "Reshuffled the rolling calendar: moved case studies to Wednesday (+41% engagement) and added a Friday product-insight slot.",
        "findings": ["Industry-insight theme is saturating - rotate in customer-problem theme"],
        "decisions": [],
        "artifacts": {"themes": ["industry insight", "customer problem", "case study", "founder POV", "product insight"]},
    }


def seo(c, rnd, p):
    return {
        "summary": "Mapped 3 topic clusters (46 keywords), drafted 4 articles, flagged 11 technical fixes; 6 keywords moved into top 10.",
        "findings": ["Programmatic SEO opportunity: 'X for [region] airports' template", "Competitor B ranks for 9 of our commercial terms"],
        "decisions": [
            _decision("Approve 4 SEO articles for publishing", "Drafted against cluster 'operational cost reduction'; brand check passed.", "approval", "medium", 0.85, True, {"type": "publish_content", "params": {"count": 4}}),
        ],
        "artifacts": {},
    }


def creative_director(c, rnd, p):
    return {
        "summary": "Produced 3 creative briefs for the CFO audience: cost-of-inaction, audited-outcome, and 'calculate your savings'.",
        "findings": ["Hook: 'Your current system is costing you...'", "Visual: real operations footage, no stock"],
        "decisions": [],
        "artifacts": {"briefs": 3},
    }


def video(c, rnd, p):
    return {
        "summary": "Rendered 24 video variants (3 scripts x 4 hooks x 2 lengths) with voiceover and music; sent to Creative Testing.",
        "findings": ["15s cut-downs ready for Meta and TikTok", "Cost per variant well under manual production"],
        "decisions": [],
        "artifacts": {"variants": 24},
    }


def creative_testing(c, rnd, p):
    return {
        "summary": "Concluded 2 tests: hook 'costing you' beat 'productivity' by 38% (96% confidence); 15s beat 30s on Meta.",
        "findings": ["Winner promoted to all active ad sets", "Losers paused to stop spend leakage"],
        "decisions": [
            _decision("Campaign #42 is outperforming account average by 62%", "Scale daily budget by 30% while CAC remains under target.", "recommendation", "high", 0.91, True,
                      {"type": "scale_campaign", "params": {"campaign": 42, "pct": 30}}, {"lift": 62}),
        ],
        "artifacts": {},
    }


def paid_media(c, rnd, p):
    return {
        "summary": "Managed 6 campaigns across Meta, Google Search, YouTube and LinkedIn; uploaded 12 creatives; paused 2 underperforming ad sets.",
        "findings": ["Google Search CAC 2,100 vs Meta 4,200", "LinkedIn CPL high but pipeline value per lead 3.4x"],
        "decisions": [
            _decision("Google Search has a lower CAC than Meta this week", "Search CAC is half of Meta's while converting to meetings at 2x. Recommend shifting 25% of Meta prospecting budget to Search.",
                      "recommendation", "high", 0.88, True, {"type": "reallocate", "params": {"from": "meta", "to": "google_search", "pct": 25}}),
        ],
        "artifacts": {},
    }


def media_buyer(c, rnd, p):
    return {
        "summary": "Reallocated daily budget using CAC, ROAS, pipeline value and margin: Meta -25%, Google Search +40%, LinkedIn +10%, Outbound capacity +1 mailbox.",
        "findings": ["Marginal ROAS on Search still > 3.0 at the new level", "Meta retained for retargeting only"],
        "decisions": [
            _decision("Budget reallocation ready to apply", "Move 25% of Meta prospecting spend to Google Search; projected blended CAC -14%.", "approval", "high", 0.87, True,
                      {"type": "apply_allocation", "params": {"meta": -25, "google_search": 40, "linkedin": 10}}),
        ],
        "artifacts": {},
    }


def landing_page(c, rnd, p):
    return {
        "summary": "Generated 3 channel-matched pages: LinkedIn -> enterprise page, Google -> high-intent page, Meta -> education page. Ad -> Page -> Offer -> CTA coherence enforced.",
        "findings": ["High-intent page converts at 6.8% vs 3.2% generic"],
        "decisions": [],
        "artifacts": {},
    }


def cro(c, rnd, p):
    return {
        "summary": "Running 4 experiments: headline, CTA copy, social-proof placement, form length. Form-length test concluded: 3 fields beat 6 by 27%.",
        "findings": ["Pricing-display test inconclusive - extending 7 days"],
        "decisions": [],
        "artifacts": {},
    }


def crm(c, rnd, p):
    return {
        "summary": "Synced 1,912 records to CRM: 388 created, 1,524 updated, 41 duplicates merged, 63 stages advanced, 19 tasks created.",
        "findings": ["Zero manual entry required", "Lead scores refreshed for all open opportunities"],
        "decisions": [],
        "artifacts": {},
    }


def analytics(c, rnd, p):
    return {
        "summary": "Unified journeys for 8,400 contacts across ads, social, email, outbound and CRM into the identity graph.",
        "findings": ["Median touches to meeting: 4.2", "Outbound + retargeting combination has the shortest cycle"],
        "decisions": [],
        "artifacts": {},
    }


def attribution(c, rnd, p):
    return {
        "summary": "Attributed 92% of closed revenue this quarter with confidence; outbound first-touch drives 46%, search 28%, LinkedIn 17%.",
        "findings": ["Meta rarely first-touch but present in 38% of won journeys as assist"],
        "decisions": [],
        "artifacts": {"attributed_share": 0.92},
    }


def revenue_intelligence(c, rnd, p):
    return {
        "summary": "Pipeline coverage 3.4x of goal; blended CAC down 11% MoM; payback 7.1 months; LTV:CAC 5.2.",
        "findings": ["Revenue dip last week traced to 2 slipped enterprise deals, not marketing"],
        "decisions": [
            _decision("Why did revenue fall this week?", "Two enterprise deals slipped to next month (procurement). Marketing-sourced pipeline is up 9% - no channel change recommended.", "insight", "medium", 0.9, False),
        ],
        "artifacts": {},
    }


def growth_optimization(c, rnd, p):
    return {
        "summary": "Decision pass complete: reduce Meta, increase Google, scale outbound, improve LinkedIn creative.",
        "findings": ["Meta CAC 4,200 · Google 2,100 · Outbound 1,400 · LinkedIn 3,100"],
        "decisions": [
            _decision("Scale outbound: add 2 mailboxes and ICP #2 sequence", "Outbound is the lowest-CAC channel with headroom; verified contact pool supports +300 sends/day.", "recommendation", "high", 0.89, True,
                      {"type": "scale_outbound", "params": {"mailboxes": 2}}),
        ],
        "artifacts": {},
    }


def experimentation(c, rnd, p):
    return {
        "summary": "Backlog: 11 hypotheses queued, 6 running, 3 concluded this week (2 winners, 1 null).",
        "findings": ["Learning velocity: 3.0 experiments / week"],
        "decisions": [],
        "artifacts": {},
    }


def memory(c, rnd, p):
    return {
        "summary": "Wrote 2 new insights to Marketing Memory and propagated them to email, ads, landing pages and LinkedIn.",
        "findings": ["CFOs respond 38% better to cost-saving than productivity messaging", "Tuesday 09:00 sends: +22% opens for Operations personas"],
        "decisions": [],
        "artifacts": {},
    }


def brand_manager(c, rnd, p):
    return {
        "summary": "Reviewed 61 assets from 9 agents: 58 on-brand, 3 corrected (tone, banned vocabulary).",
        "findings": ["Consistency score 96/100"],
        "decisions": [],
        "artifacts": {},
    }


def compliance(c, rnd, p):
    return {
        "summary": "Gated 74 assets: 70 passed, 4 flagged (unqualified claim, missing disclaimer). 2 require human sign-off.",
        "findings": ["Spam-risk score for outbound copy: low", "No platform-policy conflicts"],
        "decisions": [
            _decision("2 ad creatives need human sign-off", "Both use a comparative claim against a named competitor. Approve with the disclaimer appended or reject.", "approval", "medium", 0.95, True,
                      {"type": "review_creatives", "params": {"count": 2}}),
        ],
        "artifacts": {},
    }


SIMULATIONS = {
    "cmo": cmo, "business_intelligence": business_intelligence, "market_intelligence": market_intelligence,
    "competitor_intelligence": competitor_intelligence, "icp": icp, "icp_scoring": icp_scoring,
    "lead_discovery": lead_discovery, "lead_enrichment": lead_enrichment, "waterfall_data": waterfall_data,
    "lead_verification": lead_verification, "research": research, "hyper_personalization": hyper_personalization,
    "email_writer": email_writer, "sequence": sequence, "reply_intelligence": reply_intelligence, "sdr": sdr,
    "email_marketing": email_marketing, "lifecycle": lifecycle, "social": social, "linkedin": linkedin,
    "content_strategy": content_strategy, "seo": seo, "creative_director": creative_director, "video": video,
    "creative_testing": creative_testing, "paid_media": paid_media, "media_buyer": media_buyer,
    "landing_page": landing_page, "cro": cro, "crm": crm, "analytics": analytics, "attribution": attribution,
    "revenue_intelligence": revenue_intelligence, "growth_optimization": growth_optimization,
    "experimentation": experimentation, "memory": memory, "brand_manager": brand_manager, "compliance": compliance,
}
