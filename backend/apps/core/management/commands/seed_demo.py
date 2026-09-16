"""
Seed a fully-populated demo workspace so the Command Centre is alive on first run.

    python manage.py seed_demo            # idempotent - skips if demo exists
    python manage.py seed_demo --reset    # wipe + recreate the demo workspace

Login:  founder@demo.gtm / demo12345
"""
from __future__ import annotations

import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import Membership, User, Workspace
from apps.agents import orchestrator
from apps.agents.models import ActivityEvent, Agent, AgentRun, Decision
from apps.analytics.models import AttributionTouch, DailyMetric, Experiment, MemoryInsight, RevenueEvent
from apps.campaigns.models import BudgetAllocation, Campaign, ContentItem, Creative, LandingPage, SEOKeyword
from apps.core.models import BrandGuidelines, BusinessProfile, ControlSettings
from apps.integrations.models import Connector
from apps.knowledge.models import Competitor, KnowledgeEntity, MarketSignal
from apps.leads.models import ICP, Company, Contact
from apps.outbound.models import Enrollment, OutboundMessage, Reply, Sequence

DEMO_EMAIL = "founder@demo.gtm"
DEMO_PASSWORD = "demo12345"
rnd = random.Random(42)

FIRST = ["Amelia", "Lukas", "Sofia", "Mateo", "Ingrid", "Noah", "Freya", "Karim", "Elena", "Tobias", "Priya", "Jonas", "Chiara", "Omar", "Hanna", "Felix", "Aisha", "Nikolai", "Leonie", "Rafael"]
LAST = ["Berg", "Rossi", "Novak", "Haddad", "Larsen", "Weber", "Moreau", "Fischer", "Costa", "Ivanova", "Schmidt", "Lindqvist", "Dubois", "Petrov", "Keller", "Marin", "Andersen", "Silva", "Bauer", "Nagy"]
TITLES = [("Head of Baggage Operations", "Operations", "director"), ("VP Airport Operations", "Operations", "vp"), ("CFO", "Finance", "c_level"),
          ("Chief Operating Officer", "Operations", "c_level"), ("Head of IT Infrastructure", "IT", "director"), ("Director of Ground Handling", "Operations", "director"),
          ("Terminal Systems Manager", "IT", "manager"), ("Head of Passenger Experience", "Operations", "director"), ("CIO", "IT", "c_level"), ("Procurement Director", "Finance", "director")]
AIRPORTS = [
    ("Munich Airport", "munich-airport.de", "Germany", "Munich", 9800), ("Schiphol Group", "schiphol.nl", "Netherlands", "Amsterdam", 2900),
    ("Aeroporti di Roma", "adr.it", "Italy", "Rome", 3200), ("Copenhagen Airports", "cph.dk", "Denmark", "Copenhagen", 2600),
    ("Zurich Airport", "zurich-airport.com", "Switzerland", "Zurich", 1900), ("Vienna International Airport", "viennaairport.com", "Austria", "Vienna", 5200),
    ("Manchester Airports Group", "magairports.com", "United Kingdom", "Manchester", 6100), ("Aena", "aena.es", "Spain", "Madrid", 8400),
    ("Brussels Airport Company", "brusselsairport.be", "Belgium", "Brussels", 1100), ("Oslo Lufthavn", "avinor.no", "Norway", "Oslo", 3300),
    ("Dublin Airport Authority", "daa.ie", "Ireland", "Dublin", 3500), ("Lisbon Airport / ANA", "ana.pt", "Portugal", "Lisbon", 2700),
    ("Hamad International Airport", "dohahamadairport.com", "Qatar", "Doha", 4400), ("Dubai Airports", "dubaiairports.ae", "UAE", "Dubai", 6000),
    ("Riyadh Airports Company", "riyadhairports.com", "Saudi Arabia", "Riyadh", 2100), ("Athens International Airport", "aia.gr", "Greece", "Athens", 1200),
    ("Warsaw Chopin Airport", "lotnisko-chopina.pl", "Poland", "Warsaw", 1800), ("Prague Airport", "prg.aero", "Czechia", "Prague", 2300),
    ("Helsinki Airport / Finavia", "finavia.fi", "Finland", "Helsinki", 2000), ("Stockholm Arlanda / Swedavia", "swedavia.se", "Sweden", "Stockholm", 2500),
    ("Geneva Airport", "gva.ch", "Switzerland", "Geneva", 1000), ("Budapest Airport", "bud.hu", "Hungary", "Budapest", 1400),
    ("Bahrain Airport Company", "bahrainairport.bh", "Bahrain", "Manama", 900), ("Muscat International Airport", "omanairports.co.om", "Oman", "Muscat", 1300),
    ("Nice Cote d'Azur Airport", "nice.aeroport.fr", "France", "Nice", 800), ("Paris Aeroport / Groupe ADP", "parisaeroport.fr", "France", "Paris", 24000),
    ("Fraport", "fraport.com", "Germany", "Frankfurt", 22000), ("Heathrow Airport Holdings", "heathrow.com", "United Kingdom", "London", 7000),
    ("Gatwick Airport", "gatwickairport.com", "United Kingdom", "London", 3000), ("Milan Airports / SEA", "seamilano.eu", "Italy", "Milan", 2800),
    ("Berlin Brandenburg Airport", "berlin-airport.de", "Germany", "Berlin", 2200), ("Hamburg Airport", "hamburg-airport.de", "Germany", "Hamburg", 1900),
    ("Istanbul Grand Airport", "istairport.com", "Turkey", "Istanbul", 5000), ("Abu Dhabi Airports", "adac.ae", "UAE", "Abu Dhabi", 3000),
    ("Kuwait Airport", "kuwait-airport.com.kw", "Kuwait", "Kuwait City", 1200), ("Malta International Airport", "maltairport.com", "Malta", "Luqa", 400),
]
TECH = ["SITA BagManager", "Vanderlande", "Siemens Logistics", "Daifuku", "BEUMER", "Amadeus", "SAP", "Oracle", "Salesforce", "ServiceNow"]
SIGNALS = ["Terminal expansion announced", "Baggage-system RFP expected", "Hiring: Head of Baggage Systems", "Incumbent contract renewal in 9 months",
           "IATA Resolution 753 compliance project", "New CFO appointed", "Passenger volume +14% YoY", "Sustainability capex programme", "Self-bag-drop rollout", "Digital-twin pilot"]
CHANNELS = ["outbound", "google_search", "linkedin", "meta", "youtube", "organic"]
CHANNEL_PROFILE = {  # daily spend base, cost per lead, lead->customer rate, avg deal
    "outbound": (18000, 1400, 0.07), "google_search": (32000, 2100, 0.06), "linkedin": (26000, 3100, 0.08),
    "meta": (22000, 4200, 0.025), "youtube": (9000, 3600, 0.02), "organic": (6000, 900, 0.04),
}


class Command(BaseCommand):
    help = "Seed the demo workspace"

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true")

    def handle(self, *args, **opts):
        user = User.objects.filter(email=DEMO_EMAIL).first()
        if user and not opts["reset"]:
            if Workspace.objects.filter(owner=user).exists():
                self.stdout.write(self.style.WARNING("Demo workspace already exists - use --reset to recreate."))
                return
        if user and opts["reset"]:
            Workspace.objects.filter(owner=user).delete()
        if not user:
            user = User.objects.create_user(email=DEMO_EMAIL, password=DEMO_PASSWORD, full_name="Aarav Mehta", is_staff=True, is_superuser=True)

        ws = Workspace.objects.create(name="SkyBag Systems", owner=user, plan="scale", onboarding_completed=True)
        Membership.objects.create(workspace=ws, user=user, role=Membership.Role.OWNER)
        user.current_workspace = ws
        user.save(update_fields=["current_workspace"])

        now = timezone.now()
        today = now.date()
        self._business(ws)
        orchestrator.ensure_agents(ws)
        self._knowledge(ws, now)
        icps = self._icps(ws)
        companies, contacts = self._leads(ws, icps, now)
        seqs = self._outbound(ws, icps, contacts, now)
        lps, camps = self._campaigns(ws, icps, today)
        self._content(ws, now)
        self._metrics(ws, today)
        self._revenue(ws, companies, contacts, camps, now)
        self._experiments(ws, now)
        self._agents_activity(ws, now)
        self._decisions(ws, now)
        self._connectors(ws)

        self.stdout.write(self.style.SUCCESS(f"Seeded demo workspace '{ws.name}'.  Login: {DEMO_EMAIL} / {DEMO_PASSWORD}"))

    # ------------------------------------------------------------------ business
    def _business(self, ws):
        b = BusinessProfile.objects.create(
            workspace=ws, company_name="SkyBag Systems", website="https://skybag.example.com", industry="Airport baggage-management software",
            description="Enterprise baggage-management and reconciliation software for airports and ground handlers. Cuts mishandled bags, automates IATA 753 compliance and integrates with incumbent BHS vendors.",
            founder_brief="We sell enterprise baggage-management software to airports. We want 30 qualified airport prospects per month and ₹5 crore of pipeline.",
            currency="INR", revenue_goal=Decimal("50000000"), marketing_budget=Decimal("12000000"), gross_margin_pct=Decimal("78"),
            target_geographies=["Europe", "Middle East"], business_model="b2b_saas", average_deal_size=Decimal("1200000"), sales_cycle_days=110,
        )
        b.derived_plan = orchestrator._simulated_plan(b)
        b.plan_generated_at = timezone.now()
        b.save()
        ControlSettings.objects.create(workspace=ws, mode="autonomous_with_approval", daily_spend_cap=Decimal("200000"), monthly_spend_cap=Decimal("4000000"),
                                       max_daily_outbound=600, agent_mode_overrides={"paid_media": "autonomous_with_approval", "sdr": "full_autonomy", "seo": "full_autonomy"})
        BrandGuidelines.objects.create(
            workspace=ws, tone="Confident, precise, outcome-led. Speak like an airport-operations insider. No hype.",
            voice_rules=["Lead with the measurable outcome", "Name the incumbent system when known", "Never disparage a competitor by name in public assets"],
            vocabulary_preferred=["mishandled-bag rate", "reconciliation", "IATA 753", "turnaround", "ground handling"],
            vocabulary_banned=["revolutionary", "game-changing", "AI-powered", "synergy"],
            approved_claims=["Customers reduce mishandled bags by 20-35% within two quarters (audited)", "90-day median payback"],
            forbidden_claims=["Guaranteed results", "Zero mishandled bags"],
            legal_disclaimer="Results vary by airport size, incumbent system and integration scope.",
        )

    # ------------------------------------------------------------------ knowledge
    def _knowledge(self, ws, now):
        ents = {
            "product": ["SkyBag Reconcile", "SkyBag Track (RFID/BLE)", "SkyBag Insights"],
            "customer": ["Hub airports 20M+ pax", "Regional airports 3-20M pax", "Ground-handling operators"],
            "problem": ["Mishandled bags cost EUR 100+ each", "IATA 753 compliance gaps", "Manual reconciliation at transfer points", "Slow turnaround at peak"],
            "solution": ["Real-time bag reconciliation", "Predictive misconnect alerts", "Automated 753 reporting"],
            "differentiator": ["Vendor-agnostic BHS integration", "Audited 20-35% mishandled-bag reduction", "90-day payback"],
            "pricing": ["Per-passenger platform fee", "Enterprise annual licence EUR 350k-1.2M"],
            "objection": ["Already have SITA/Vanderlande", "Integration effort with legacy BHS", "Procurement cycle 9-14 months"],
            "use_case": ["Transfer-bag reconciliation", "Self-bag-drop tracking", "Baggage claim ETA"],
            "outcome": ["-31% mishandled bags at Copenhagen", "EUR 2.1M annual savings at Vienna"],
            "persona": ["Head of Baggage Operations", "CFO", "CIO"],
            "geography": ["Western Europe", "Nordics", "GCC"],
            "sales_cycle": ["110-day median, RFP-driven"],
        }
        created = {}
        for kind, names in ents.items():
            for n in names:
                created[n] = KnowledgeEntity.objects.create(workspace=ws, kind=kind, name=n, summary=f"{n} - captured from website, decks and CRM history.",
                                                            confidence=round(rnd.uniform(0.7, 0.98), 2), freshness=now.date() - timedelta(days=rnd.randint(0, 20)), source=rnd.choice(["website", "sales deck", "CRM", "case study"]))
        links = [("SkyBag Reconcile", "Real-time bag reconciliation"), ("Real-time bag reconciliation", "Mishandled bags cost EUR 100+ each"),
                 ("SkyBag Reconcile", "Transfer-bag reconciliation"), ("Audited 20-35% mishandled-bag reduction", "-31% mishandled bags at Copenhagen"),
                 ("CFO", "90-day payback"), ("Head of Baggage Operations", "Mishandled bags cost EUR 100+ each"), ("CIO", "Vendor-agnostic BHS integration"),
                 ("Already have SITA/Vanderlande", "Vendor-agnostic BHS integration"), ("Hub airports 20M+ pax", "Transfer-bag reconciliation"),
                 ("Automated 753 reporting", "IATA 753 compliance gaps"), ("SkyBag Track (RFID/BLE)", "Self-bag-drop tracking"), ("GCC", "Hub airports 20M+ pax")]
        for a, b in links:
            created[a].related.add(created[b])

        comps = [
            ("SITA BagManager", "high", "Incumbent everywhere; positions on global network and reliability.", "'The industry standard for baggage' / '30% reduction in mishandled bags'", 0.34),
            ("Vanderlande VIBES", "high", "BHS hardware vendor bundling software; positions on end-to-end.", "'One partner for the whole baggage journey'", 0.22),
            ("Amadeus Baggage", "medium", "Airline-side reconciliation; growing airport push.", "'Reconcile every bag, every flight'", 0.15),
            ("Brock Solutions", "medium", "North-American focus; strong on RFID.", "'RFID-first baggage tracking'", 0.09),
            ("Damarel", "low", "Ground-handler focused; low price point.", "'Affordable baggage reconciliation'", 0.07),
            ("In-house / legacy", "medium", "Airports with custom BRS built 10+ years ago.", "-", 0.13),
        ]
        for name, threat, pos, ad, sov in comps:
            Competitor.objects.create(workspace=ws, name=name, website=f"https://{name.split()[0].lower()}.example.com", positioning=pos, threat_level=threat, share_of_voice=sov,
                                      target_customer="Hub and regional airports", pricing=rnd.choice(["Enterprise licence", "Per-pax fee", "Bundled with hardware"]),
                                      usps=["Installed base", "Brand trust"], weaknesses=["Slow roadmap", "Vendor lock-in", "Opaque pricing"],
                                      ad_messages=[ad], funding=rnd.choice(["Public", "Private", "PE-backed"]), headcount=rnd.randint(200, 5000),
                                      tech_stack=["Java", "Oracle"], last_seen=now - timedelta(hours=rnd.randint(1, 72)))
        sigs = [
            ("competitor", "SITA launches 'Bag Journey' campaign targeting European hubs", "SITA", 0.92, True, "negative"),
            ("funding", "Riyadh Airports announces USD 1.2B terminal modernization capex", "Riyadh Airports Company", 0.95, True, "positive"),
            ("hiring", "Fraport hiring Head of Baggage Systems Transformation", "Fraport", 0.88, True, "positive"),
            ("regulatory", "IATA tightens Resolution 753 reporting audits for 2027", "IATA", 0.9, True, "positive"),
            ("trend", "Search interest 'baggage reconciliation software' +18% QoQ", "Google Trends", 0.7, False, "positive"),
            ("launch", "Vanderlande announces AI-based BHS predictive maintenance", "Vanderlande", 0.75, False, "neutral"),
            ("news", "Schiphol reports record mishandled-bag summer, plans RFP", "Schiphol Group", 0.97, True, "positive"),
            ("pricing", "Amadeus raises baggage module pricing 12% for 2026 renewals", "Amadeus", 0.8, True, "positive"),
            ("complaint", "Reddit / LinkedIn threads: legacy BRS outages at two UK airports", "Manchester Airports Group", 0.66, True, "positive"),
            ("hiring", "Dubai Airports posting 6 roles in baggage digitalisation", "Dubai Airports", 0.84, True, "positive"),
        ]
        for i, (kind, title, ent, rel, opp, sent) in enumerate(sigs):
            MarketSignal.objects.create(workspace=ws, kind=kind, title=title, entity=ent, relevance=rel, opportunity=opp, sentiment=sent,
                                        summary=f"Detected via {rnd.choice(['news API', 'job boards', 'ad library', 'search trends', 'social listening'])}.",
                                        detected_at=now - timedelta(hours=3 * i + rnd.randint(0, 5)), actioned=i in (1, 3))

    # ------------------------------------------------------------------ ICPs
    def _icps(self, ws):
        data = [
            ("European hub airports with an active modernization project", 1, "approved", 4200000, 180, {"industry": "Airports", "headcount": "500+", "pax": ">10M/yr", "geo": ["Western Europe", "Nordics", "UK"], "tech": ["Existing BHS automation"], "signals": ["Terminal expansion", "RFP expected", "753 audit"]},
             "Highest intent and budget already allocated. 61% of past won revenue.", 0.081, 0.031),
            ("Mid-size airports on legacy in-house BRS nearing renewal", 2, "approved", 2100000, 260, {"industry": "Airports", "headcount": "200-2000", "pax": "3-20M/yr", "geo": ["Europe"], "tech": ["In-house BRS", "Damarel"], "signals": ["Contract renewal <12 months", "Outage reports"]},
             "Switching window opens every 3-5 years; lower ACV, faster cycle.", 0.064, 0.022),
            ("GCC greenfield & expansion projects", 3, "draft", 6800000, 40, {"industry": "Airports", "headcount": "1000+", "pax": ">20M/yr", "geo": ["UAE", "Qatar", "Saudi Arabia", "Oman", "Bahrain"], "tech": ["New terminal"], "signals": ["Capex announcement", "Digitalisation hiring"]},
             "Emerging: rising capex, fewer incumbents. Flagged by Market Intelligence.", 0.0, 0.0),
        ]
        out = []
        for name, rank, status, acv, tam, crit, fit, rr, mr in data:
            out.append(ICP.objects.create(workspace=ws, name=name, rank=rank, status=status, expected_acv=acv, estimated_tam=tam, criteria=crit, fit_summary=fit,
                                          description=fit, reply_rate=rr, meeting_rate=mr, cac=Decimal(rnd.choice([1400, 2100, 0])),
                                          personas=[{"title": "Head of Baggage Operations", "pain": "Mishandled bags, SLA penalties", "angle": "Audited reduction"},
                                                    {"title": "CFO", "pain": "Cost of inaction", "angle": "90-day payback calculator"},
                                                    {"title": "CIO", "pain": "Legacy integration risk", "angle": "Vendor-agnostic reference architecture"}],
                                          buying_signals=crit.get("signals", [])))
        return out

    # ------------------------------------------------------------------ leads
    def _leads(self, ws, icps, now):
        companies, contacts = [], []
        for i, (name, domain, country, city, hc) in enumerate(AIRPORTS):
            gcc = country in ("Qatar", "UAE", "Saudi Arabia", "Bahrain", "Oman", "Kuwait")
            icp = icps[2] if gcc else (icps[0] if hc > 2000 else icps[1])
            base = 88 if icp is icps[0] else (74 if icp is icps[1] else 69)
            score = max(35, min(99, base + rnd.randint(-14, 10)))
            tier = 1 if score >= 80 else (2 if score >= 60 else 3)
            c = Company.objects.create(
                workspace=ws, name=name, domain=domain, industry="Airport operator", country=country, city=city, headcount=hc,
                revenue=Decimal(hc * rnd.randint(180000, 420000)), funding_stage=rnd.choice(["Public", "State-owned", "PE-backed", "Private"]),
                tech_stack=rnd.sample(TECH, 3), signals=rnd.sample(SIGNALS, rnd.randint(1, 3)), icp=icp, fit_score=score, tier=tier,
                score_breakdown={"industry_fit": rnd.randint(85, 100), "size": rnd.randint(60, 100), "geography": rnd.randint(55, 100),
                                 "tech_fit": rnd.randint(50, 95), "buying_signal": rnd.randint(30, 100), "revenue_potential": rnd.randint(50, 100)},
                source=rnd.choice(["apollo", "apollo", "directory", "crm", "linkedin"]), enriched=rnd.random() > 0.15,
                linkedin_url=f"https://linkedin.com/company/{domain.split('.')[0]}", logo_seed=domain,
            )
            companies.append(c)
            for j in range(rnd.randint(1, 3)):
                title, persona, sen = rnd.choice(TITLES)
                fn, ln = rnd.choice(FIRST), rnd.choice(LAST)
                est = rnd.choices(["valid", "valid", "valid", "risky", "invalid", "unverified"], k=1)[0]
                stage = rnd.choices(["lead", "lead", "mql", "sql", "opportunity", "customer"], weights=[40, 20, 18, 12, 7, 3])[0]
                contacts.append(Contact.objects.create(
                    workspace=ws, company=c, first_name=fn, last_name=ln, title=title, persona=persona, seniority=sen,
                    email=f"{fn.lower()}.{ln.lower()}@{domain}", email_status=est, linkedin_url=f"https://linkedin.com/in/{fn.lower()}{ln.lower()}",
                    stage=stage, lead_score=min(99, score + rnd.randint(-20, 10)), source=c.source,
                    intelligence_card={
                        "trigger_event": rnd.choice(c.signals), "incumbent": c.tech_stack[0], "recent_activity": f"Commented on IATA 753 audit changes ({rnd.randint(2, 20)}d ago)",
                        "pain_point": rnd.choice(["Transfer misconnects at peak", "Manual reconciliation", "Audit reporting burden"]),
                        "best_case_study": rnd.choice(["Copenhagen -31% mishandled", "Vienna EUR 2.1M savings"]),
                        "funding": c.funding_stage, "hiring": rnd.choice(["3 baggage-systems roles open", "No relevant hiring", "Head of BHS role open"]),
                    },
                    enrichment_log=[{"provider": "apollo", "fields": ["title", "linkedin"], "ok": True}, {"provider": "clearbit", "fields": ["email"], "ok": est != "unverified"}],
                    verification={"deliverable": est == "valid", "employed": True, "duplicate": False, "dnc": False, "checked_at": (now - timedelta(days=rnd.randint(0, 9))).isoformat()},
                    last_activity_at=now - timedelta(hours=rnd.randint(1, 400)),
                ))
        for icp in icps:
            icp.prospects_count = Company.objects.filter(icp=icp).count() * rnd.randint(40, 120)
            icp.save(update_fields=["prospects_count"])
        return companies, contacts

    # ------------------------------------------------------------------ outbound
    def _outbound(self, ws, icps, contacts, now):
        steps = [
            {"day": 1, "channel": "email", "type": "opener", "subject": "{{trigger_event}} at {{company}}", "body": "Saw the news on {{trigger_event}}. Airports like Copenhagen used that moment to cut mishandled bags 31% within two quarters - on top of {{incumbent}}, not replacing it. Worth a 15-minute look?"},
            {"day": 3, "channel": "email", "type": "insight", "subject": "one number", "body": "One thing most Heads of Baggage Ops miss: 60% of misconnects are predictable 40 minutes out. Happy to share the transfer-bag benchmark we built for European hubs."},
            {"day": 6, "channel": "linkedin", "type": "touch", "subject": "", "body": "Connection request + short note referencing {{recent_activity}}."},
            {"day": 6, "channel": "email", "type": "case_study", "subject": "how Vienna did it", "body": "Short case study attached - same incumbent as you ({{incumbent}}). EUR 2.1M annual savings, 90-day payback."},
            {"day": 10, "channel": "email", "type": "alt_value", "subject": "different angle", "body": "If mishandled bags are not the priority, the other reason airports switch is IATA 753 audit burden. Which matters more this year?"},
            {"day": 15, "channel": "email", "type": "breakup", "subject": "closing the loop", "body": "Will stop here. If timing changes, reply 'later' and I will check back next quarter."},
        ]
        defs = [
            ("ICP #1 · Head of Baggage Ops · Modernization trigger", icps[0], "Operations", "multi", "active", 1644, 1180, 612, 96, 41, 14, 7, "passed"),
            ("ICP #1 · CFO · Cost-of-inaction", icps[0], "Finance", "email", "active", 620, 540, 251, 39, 17, 6, 3, "passed"),
            ("ICP #2 · Renewal window · Legacy BRS", icps[1], "Operations", "email", "active", 880, 610, 288, 44, 19, 5, 4, "passed"),
            ("ICP #1 · CIO · Integration-risk angle", icps[0], "IT", "multi", "paused", 410, 402, 150, 21, 6, 2, 2, "passed"),
            ("ICP #3 · GCC greenfield · Capex trigger", icps[2], "Operations", "multi", "pending_approval", 0, 0, 0, 0, 0, 0, 0, "passed"),
            ("Re-activation · Closed-lost 2024", icps[1], "Operations", "email", "draft", 0, 0, 0, 0, 0, 0, 0, "pending"),
        ]
        seqs = []
        for name, icp, persona, ch, st, enr, sent, op, rep, pos, mt, bn, comp in defs:
            seqs.append(Sequence.objects.create(workspace=ws, name=name, icp=icp, persona=persona, channel=ch, status=st, steps=steps, daily_cap=150,
                                                goal="Book qualified discovery meetings", enrolled=enr, sent=sent, opened=op, replied=rep, positive_replies=pos, meetings=mt, bounced=bn, compliance_status=comp))
        active = [s for s in seqs if s.status == "active"]
        for ct in contacts:
            if ct.email_status == "valid" and rnd.random() < 0.8:
                seq = rnd.choice(active)
                step = rnd.randint(0, 5)
                e = Enrollment.objects.create(workspace=ws, sequence=seq, contact=ct, current_step=step, personalization=ct.intelligence_card,
                                              status=rnd.choices(["active", "replied", "completed"], weights=[6, 2, 2])[0], next_send_at=now + timedelta(days=rnd.randint(1, 4)))
                for si in range(min(step + 1, 3)):
                    s = steps[si]
                    body = s["body"].replace("{{trigger_event}}", ct.intelligence_card.get("trigger_event", "the expansion")).replace("{{company}}", ct.company.name).replace("{{incumbent}}", ct.intelligence_card.get("incumbent", "your BHS")).replace("{{recent_activity}}", ct.intelligence_card.get("recent_activity", "your post"))
                    OutboundMessage.objects.create(workspace=ws, enrollment=e, contact=ct, sequence=seq, step_index=si, channel=s["channel"],
                                                   subject=s["subject"].replace("{{trigger_event}}", ct.intelligence_card.get("trigger_event", "the expansion")).replace("{{company}}", ct.company.name), body=body,
                                                   personalization_hooks=[ct.intelligence_card.get("trigger_event"), ct.intelligence_card.get("incumbent")],
                                                   status="sent", qa={"spam_score": round(rnd.uniform(0.5, 2.5), 1), "brand": "pass", "claims": "pass"},
                                                   sent_at=now - timedelta(days=(3 - si) * 3 + rnd.randint(0, 2)), opened_at=now - timedelta(days=rnd.randint(0, 6)) if rnd.random() < 0.5 else None)
        reply_pool = [
            ("interested", "Interesting timing - we are scoping exactly this for the T2 expansion. Can you send a short overview and some times next week?", 0.94, "Send overview + propose 3 slots", True),
            ("meeting_request", "Let's talk. Thursday 10:00 CET works on my side.", 0.97, "Book meeting Thursday 10:00", True),
            ("pricing_request", "What does licensing look like for a 25M pax airport with existing Vanderlande BHS?", 0.9, "Send pricing framework + payback calculator", False),
            ("not_now", "Not this year - budget locked until the new fiscal. Reach out in Q1.", 0.92, "Snooze 5 months, add to nurture", False),
            ("wrong_person", "I moved to a different role - the right contact is our Head of Baggage Systems, Lena Fischer.", 0.95, "Create contact Lena Fischer; restart sequence", False),
            ("objection", "We already have SITA BagManager, why would we add another layer?", 0.88, "Send integration one-pager; alt-value step", False),
            ("send_info", "Can you send the Copenhagen case study?", 0.93, "Send case study; follow up in 3 days", False),
            ("unsubscribe", "Please remove me from this list.", 0.99, "Unsubscribe + DNC flag", False),
            ("out_of_office", "I am out of office until the 24th with limited access to email.", 0.98, "Pause until 25th", False),
            ("negative", "Not interested, stop emailing.", 0.96, "Close + DNC", False),
        ]
        enrolled = list(Enrollment.objects.filter(workspace=ws).select_related("contact"))
        rnd.shuffle(enrolled)
        for i, e in enumerate(enrolled[:34]):
            cls, body, conf, nxt, meeting = rnd.choices(reply_pool, weights=[20, 12, 8, 14, 7, 12, 10, 4, 8, 5])[0]
            Reply.objects.create(workspace=ws, contact=e.contact, sequence=e.sequence, body=body, classification=cls, confidence=conf, next_action=nxt,
                                 sdr_response=("Thanks - sending the overview now. Would Tue 11:00 or Thu 15:00 CET suit for a 20-minute walkthrough?" if cls in ("interested", "meeting_request", "send_info", "pricing_request") else ""),
                                 handled=i > 9, meeting_booked_at=(now + timedelta(days=rnd.randint(1, 8))) if meeting else None,
                                 received_at=now - timedelta(hours=rnd.randint(1, 160)))
        return seqs

    # ------------------------------------------------------------------ campaigns
    def _campaigns(self, ws, icps, today):
        lps = [
            LandingPage.objects.create(workspace=ws, name="Enterprise · Modernize without migration risk", slug="enterprise", channel="linkedin", audience="Heads of Ops / CIO at hub airports", headline="Modernize baggage reconciliation without the migration risk", subheadline="Runs on top of SITA, Vanderlande or in-house BHS. Audited 20-35% fewer mishandled bags.", cta="Book a walkthrough", offer="Reference-architecture workshop", status="live", visitors=4820, conversions=241, active_experiment="Headline: outcome vs. risk framing", sections=["hero", "logos", "outcome_stats", "architecture", "case_study", "cta"], variants=[{"label": "A", "headline": "Modernize baggage reconciliation without the migration risk", "cr": 5.0}, {"label": "B", "headline": "20-35% fewer mishandled bags. Audited.", "cr": 5.6}]),
            LandingPage.objects.create(workspace=ws, name="High-intent · Baggage reconciliation software", slug="reconciliation-software", channel="google_search", audience="Search: baggage reconciliation software", headline="The baggage reconciliation platform with a 90-day payback", subheadline="Compare against your current mishandled-bag cost in 2 minutes.", cta="Calculate your savings", offer="Savings calculator", status="live", visitors=6210, conversions=422, active_experiment="Form: 3 fields vs 6 fields", sections=["hero", "calculator", "proof", "faq", "cta"], variants=[{"label": "A", "headline": "The baggage reconciliation platform with a 90-day payback", "cr": 6.8}, {"label": "B", "headline": "Stop paying EUR 100 per mishandled bag", "cr": 6.1}]),
            LandingPage.objects.create(workspace=ws, name="Education · What your current system costs", slug="cost-of-inaction", channel="meta", audience="Retargeting: airport ops professionals", headline="What your current baggage system is really costing you", subheadline="A 4-minute explainer with the numbers finance teams ask for.", cta="Watch the 4-min explainer", offer="Video + benchmark PDF", status="live", visitors=9100, conversions=291, active_experiment="Video thumbnail", sections=["hero_video", "benchmark", "cta"], variants=[]),
            LandingPage.objects.create(workspace=ws, name="GCC · New-terminal readiness", slug="gcc-terminal", channel="linkedin", audience="GCC airport programme directors", headline="Open your new terminal with zero-legacy baggage reconciliation", subheadline="Built for greenfield programmes in the Gulf.", cta="Talk to the programme team", offer="Terminal-readiness checklist", status="pending_approval", visitors=0, conversions=0, sections=["hero", "checklist", "cta"], variants=[]),
        ]
        cdefs = [
            ("Search · Baggage reconciliation (EU)", "google_search", "active", 32000, lps[1], icps[0], 41, 2.4, 4200000),
            ("Search · IATA 753 compliance", "google_search", "active", 14000, lps[1], icps[1], 22, 1.1, 1900000),
            ("LinkedIn · ABM Tier-1 hubs", "linkedin", "active", 26000, lps[0], icps[0], 42, 3.9, 9800000),
            ("Meta · Retargeting explainer", "meta", "active", 22000, lps[2], icps[0], 38, 0.6, 1200000),
            ("YouTube · Cost-of-inaction 30s", "youtube", "active", 9000, lps[2], icps[1], 45, 0.3, 600000),
            ("LinkedIn · GCC programme directors", "linkedin", "pending_approval", 18000, lps[3], icps[2], 0, 0, 0),
            ("Meta · Prospecting lookalike", "meta", "paused", 12000, lps[2], icps[1], 30, 0.2, 300000),
        ]
        camps = []
        for i, (name, ch, st, daily, lp, icp, days, pipe_m, pipe) in enumerate(cdefs):
            spend = daily * days
            _, cpl, conv = CHANNEL_PROFILE[ch]
            leads = int(spend / cpl) if spend else 0
            camps.append(Campaign.objects.create(
                workspace=ws, name=name, channel=ch, status=st, daily_budget=daily, total_spend=spend, icp=icp, landing_page=lp,
                impressions=leads * rnd.randint(400, 900), clicks=leads * rnd.randint(9, 20), conversions=leads, leads=leads, meetings=int(leads * 0.18),
                pipeline_value=pipe, revenue=Decimal(int(pipe * rnd.uniform(0.18, 0.32))) if st == "active" and i < 5 else 0,
                audience={"geo": icp.criteria.get("geo", []), "titles": [p["title"] for p in icp.personas], "seniority": ["director", "vp", "c_level"]},
                external_id=f"{ch[:2].upper()}-{100234 + i}", started_at=timezone.now() - timedelta(days=days) if days else None,
            ))
        hooks = [("Your current system is costing you EUR 100 per bag", "cost"), ("Audited: 31% fewer mishandled bags in two quarters", "proof"),
                 ("Runs on top of SITA. No rip-and-replace.", "integration"), ("What happens 40 minutes before a misconnect", "curiosity"),
                 ("IATA 753 audits are getting stricter in 2027", "urgency"), ("Productivity gains for baggage teams", "productivity")]
        for camp in camps[:5]:
            for vi, (hook, tag) in enumerate(rnd.sample(hooks, 4)):
                imp = rnd.randint(40000, 220000)
                ctr = rnd.uniform(0.6, 2.4) * (1.4 if tag in ("cost", "proof") else 0.8)
                clicks = int(imp * ctr / 100)
                Creative.objects.create(workspace=ws, campaign=camp, kind=rnd.choice(["image", "video", "video", "carousel"]), variant_label="ABCD"[vi], hook=hook, headline=hook,
                                        primary_text=f"{hook}. See how European hubs cut mishandled bags without replacing their BHS.", cta=rnd.choice(["Calculate your savings", "Book a walkthrough", "Watch the explainer"]),
                                        visual_direction=rnd.choice(["Real airport ops footage, dawn light", "Split-screen: bag hall vs dashboard", "CFO desk with savings calc"]), gradient_seed=rnd.randint(1, 8),
                                        audience_label=rnd.choice(["Heads of Ops", "CFOs", "CIOs"]), impressions=imp, clicks=clicks, conversions=int(clicks * rnd.uniform(0.03, 0.09)),
                                        spend=Decimal(int(imp * rnd.uniform(0.08, 0.2))), is_winner=(vi == 0 and tag in ("cost", "proof")), statistical_confidence=round(rnd.uniform(0.6, 0.99), 2),
                                        compliance_status=rnd.choices(["passed", "passed", "passed", "flagged"], k=1)[0], compliance_notes=[] if rnd.random() > 0.2 else ["Comparative claim needs disclaimer"], active=vi < 3)
        # allocations
        moves = [("meta", 30000, 22000, "Meta CAC 4,200 vs blended 2,600; retained for retargeting only", 3), ("google_search", 24000, 32000, "Search CAC 2,100 with marginal ROAS > 3.0", 3),
                 ("linkedin", 24000, 26000, "Pipeline value per lead 3.4x; scale ABM to Tier-1", 3), ("youtube", 12000, 9000, "View-through leads not converting to SQL", 10),
                 ("outbound", 14000, 18000, "Lowest CAC (1,400); added 2 mailboxes", 10), ("meta", 36000, 30000, "Prospecting lookalike paused after creative test", 17)]
        for ch, prev, new, why, ago in moves:
            BudgetAllocation.objects.create(workspace=ws, date=today - timedelta(days=ago), channel=ch, previous_daily=prev, new_daily=new, reason=why, applied=True,
                                            metrics={"cac": CHANNEL_PROFILE[ch][1], "roas": round(rnd.uniform(1.2, 4.8), 2), "pipeline_per_lead": rnd.randint(80000, 420000)})
        return lps, camps

    # ------------------------------------------------------------------ content
    def _content(self, ws, now):
        themes = {0: "Industry insight", 1: "Customer problem", 2: "Case study", 3: "Founder POV", 4: "Product insight"}
        titles = {
            "Industry insight": ["Why 2027 IATA 753 audits change baggage budgets", "The real cost curve of a mishandled bag", "Transfer hubs vs O&D: different baggage problems"],
            "Customer problem": ["The 40-minute window before a misconnect", "Why manual reconciliation breaks at peak", "Legacy BRS outages: what UK airports learned"],
            "Case study": ["Copenhagen: -31% mishandled bags in two quarters", "Vienna: EUR 2.1M annual savings on top of Vanderlande", "How a 6M-pax airport passed its 753 audit"],
            "Founder POV": ["We should stop selling 'AI' to airport operators", "Baggage is a data problem wearing a hardware costume", "What CFOs actually ask about payback"],
            "Product insight": ["Predictive misconnect alerts, explained", "Vendor-agnostic integration: how it works", "RFID + BLE: when each wins"],
        }
        kinds = ["linkedin_post", "linkedin_post", "blog", "video", "x_post", "newsletter", "instagram", "youtube"]
        start = now - timedelta(days=now.weekday() + 7)
        for d in range(21):
            day = start + timedelta(days=d)
            if day.weekday() >= 5:
                continue
            theme = themes[day.weekday()]
            for k in rnd.sample(kinds, 2):
                title = rnd.choice(titles[theme])
                past = day < now
                ContentItem.objects.create(workspace=ws, title=title, kind=k, theme=theme, platform=k.split("_")[0], scheduled_for=day.replace(hour=9, minute=0),
                                           status="published" if past else rnd.choice(["scheduled", "scheduled", "pending_approval", "drafted"]),
                                           body=f"{title}. Draft generated by the Content Strategy Agent and reviewed by the Brand Manager.",
                                           hooks=[title.split(":")[0]], hashtags=["#airports", "#baggage", "#IATA753"], seo_keyword=rnd.choice(["baggage reconciliation software", "mishandled bags", "IATA 753"]),
                                           engagement={"impressions": rnd.randint(1200, 24000), "likes": rnd.randint(20, 400), "comments": rnd.randint(2, 60), "clicks": rnd.randint(10, 500), "leads": rnd.randint(0, 6)} if past else {},
                                           compliance_status="passed")
        kws = [("baggage reconciliation software", "Reconciliation", "commercial", 1900, 41, 7, 12), ("mishandled baggage cost", "Cost", "informational", 2400, 28, 4, 9),
               ("IATA resolution 753 compliance", "Compliance", "informational", 1300, 22, 2, 3), ("baggage handling system software", "Reconciliation", "commercial", 2900, 55, 14, 21),
               ("airport baggage tracking RFID", "Tracking", "commercial", 1600, 38, 9, 15), ("bag reconciliation system airport", "Reconciliation", "commercial", 880, 33, 5, 11),
               ("transfer baggage misconnect", "Cost", "informational", 720, 19, 3, 6), ("baggage handling KPIs", "Cost", "informational", 590, 15, 1, 2),
               ("self bag drop tracking", "Tracking", "commercial", 480, 27, 18, 24), ("SITA BagManager alternative", "Competitor", "commercial", 260, 12, 6, None)]
        for kw, cl, intent, vol, diff, cur, prev in kws:
            SEOKeyword.objects.create(workspace=ws, keyword=kw, cluster=cl, intent=intent, volume=vol, difficulty=diff, current_rank=cur, previous_rank=prev, target_url=f"https://skybag.example.com/{cl.lower()}")

    # ------------------------------------------------------------------ metrics
    def _metrics(self, ws, today):
        rows = []
        for d in range(120, -1, -1):
            date = today - timedelta(days=d)
            growth = 1 + (120 - d) / 120 * 0.55  # improving over time
            weekend = 0.55 if date.weekday() >= 5 else 1.0
            for ch, (spend_base, cpl, conv) in CHANNEL_PROFILE.items():
                noise = rnd.uniform(0.8, 1.2)
                spend = spend_base * weekend * noise * (0.85 if ch == "meta" and d < 20 else 1) * (1.25 if ch == "google_search" and d < 20 else 1)
                leads = max(0, int(spend / cpl * growth * rnd.uniform(0.8, 1.25)))
                mqls = int(leads * rnd.uniform(0.45, 0.65)); sqls = int(mqls * rnd.uniform(0.4, 0.6)); meetings = int(sqls * rnd.uniform(0.6, 0.9))
                opps = int(meetings * rnd.uniform(0.4, 0.7)); customers = 1 if rnd.random() < leads * conv * 0.07 else 0
                pipeline = opps * rnd.randint(1800000, 5200000)
                revenue = int(spend * rnd.uniform(1.0, 1.5) * growth) + customers * rnd.randint(300000, 700000)  # ratable recurring + new-deal bumps
                rows.append(DailyMetric(workspace=ws, date=date, channel=ch, spend=Decimal(int(spend)), impressions=int(spend * rnd.uniform(3, 9)), clicks=int(spend / rnd.uniform(35, 90)),
                                        visitors=int(spend / rnd.uniform(40, 100)), leads=leads, mqls=mqls, sqls=sqls, meetings=meetings, opportunities=opps, customers=customers,
                                        pipeline_value=pipeline, revenue=revenue))
        DailyMetric.objects.bulk_create(rows)

    # ------------------------------------------------------------------ revenue & attribution
    def _revenue(self, ws, companies, contacts, camps, now):
        customers = [c for c in contacts if c.stage == "customer"] or contacts[:6]
        paths = [["outbound", "linkedin", "google_search", "meeting"], ["google_search", "landing_page", "outbound", "meeting"], ["linkedin", "meta", "linkedin", "meeting"],
                 ["organic", "google_search", "meeting"], ["outbound", "meeting"], ["meta", "google_search", "outbound", "meeting"]]
        for i, ct in enumerate(customers[:14]):
            path = paths[i % len(paths)]
            closed = now - timedelta(days=rnd.randint(2, 85))
            for j, ch in enumerate(path):
                AttributionTouch.objects.create(workspace=ws, contact=ct, channel=ch if ch not in ("meeting", "landing_page") else path[0], campaign=rnd.choice(camps) if ch in ("meta", "google_search", "linkedin") else None,
                                                touch_type={"meeting": "meeting_booked", "landing_page": "page_view"}.get(ch, "ad_click" if ch in ("meta", "google_search", "linkedin", "youtube") else "email_reply"),
                                                occurred_at=closed - timedelta(days=(len(path) - j) * rnd.randint(6, 18)), weight=1.0)
            chans = [c for c in path if c not in ("meeting", "landing_page")]
            split = {c: round(chans.count(c) / len(chans), 2) for c in set(chans)}
            RevenueEvent.objects.create(workspace=ws, company=ct.company, contact=ct, amount=Decimal(rnd.randint(800000, 1800000)), kind=rnd.choices(["new", "expansion", "renewal"], weights=[6, 2, 2])[0],
                                        source_channel=chans[0], closing_channel=chans[-1], attribution=split, closed_at=closed, days_to_close=rnd.randint(60, 160))
            ct.stage = "customer"
            ct.save(update_fields=["stage"])

    # ------------------------------------------------------------------ experiments & memory
    def _experiments(self, ws, now):
        exps = [
            ("Cost-saving vs productivity messaging (CFO)", "CFOs respond better to cost-saving than productivity framing", "outbound", "message_angle", [{"label": "Cost-saving", "exposures": 620, "conversions": 71}, {"label": "Productivity", "exposures": 615, "conversions": 51}], "concluded", 0.96, "Cost-saving", 38.0, "Cost-saving framing lifts positive replies 38% for finance personas. Propagated to ads, LPs, LinkedIn.", 21, 4),
            ("3-field vs 6-field form (high-intent LP)", "Fewer fields raise conversion without hurting lead quality", "landing_page", "form_length", [{"label": "3 fields", "exposures": 2100, "conversions": 151}, {"label": "6 fields", "exposures": 2080, "conversions": 119}], "concluded", 0.97, "3 fields", 27.0, "3 fields wins; SQL rate unchanged. Applied to all live pages.", 18, 3),
            ("15s vs 30s video (Meta retargeting)", "Shorter cut-downs win on thumb-stop and CPL", "meta", "video_length", [{"label": "15s", "exposures": 88000, "conversions": 312}, {"label": "30s", "exposures": 87500, "conversions": 241}], "concluded", 0.95, "15s", 29.0, "15s wins on CPL; 30s retains better for CFO audience - keep 30s for that segment.", 14, 2),
            ("Headline: outcome vs risk framing (Enterprise LP)", "Outcome-led headline beats risk-led for Heads of Ops", "linkedin", "headline", [{"label": "Outcome", "exposures": 1400, "conversions": 78}, {"label": "Risk", "exposures": 1380, "conversions": 70}], "running", 0.71, "", 0, "", 6, None),
            ("Send time: Tue 09:00 vs Thu 14:00", "Morning sends outperform for Operations personas", "outbound", "send_time", [{"label": "Tue 09:00", "exposures": 410, "conversions": 39}, {"label": "Thu 14:00", "exposures": 405, "conversions": 31}], "running", 0.78, "", 0, "", 5, None),
            ("Pricing display on LP", "Showing a price band increases SQL quality", "google_search", "pricing_display", [{"label": "Price band shown", "exposures": 900, "conversions": 48}, {"label": "Hidden", "exposures": 910, "conversions": 52}], "running", 0.42, "", 0, "", 9, None),
            ("LinkedIn: founder vs company voice", "Founder-voice posts drive more profile-sourced leads", "linkedin", "voice", [{"label": "Founder", "exposures": 12, "conversions": 18}, {"label": "Company", "exposures": 12, "conversions": 6}], "running", 0.83, "", 0, "", 8, None),
            ("Hook: '40-minute window' curiosity angle", "Curiosity hook beats proof hook for cold LinkedIn audiences", "linkedin", "hook", [{"label": "Curiosity", "exposures": 0, "conversions": 0}, {"label": "Proof", "exposures": 0, "conversions": 0}], "proposed", 0, "", 0, "", None, None),
            ("GCC page: English vs Arabic hero", "Bilingual hero raises engagement for GCC programme directors", "linkedin", "language", [], "proposed", 0, "", 0, "", None, None),
            ("Sequence: LinkedIn touch at step 2 vs step 3", "Earlier LinkedIn touch lifts reply rate for Tier-1", "outbound", "cadence", [], "proposed", 0, "", 0, "", None, None),
            ("Search: exact vs phrase match on '753 compliance'", "Exact match lowers CPL without losing volume", "google_search", "match_type", [], "proposed", 0, "", 0, "", None, None),
        ]
        created = []
        for name, hyp, ch, var, variants, st, conf, win, lift, learn, started, concluded in exps:
            created.append(Experiment.objects.create(workspace=ws, name=name, hypothesis=hyp, channel=ch, variable=var, variants=variants, status=st, confidence=conf, winner=win, lift_pct=lift, learning=learn,
                                                     started_at=now - timedelta(days=started) if started else None, concluded_at=now - timedelta(days=concluded) if concluded else None,
                                                     owner_agent=rnd.choice(["experimentation", "cro", "creative_testing", "sequence"])))
        insights = [
            ("CFOs respond 38% better to cost-saving messaging than productivity messaging.", "messaging", 0.96, ["outbound", "linkedin", "meta", "landing_page", "sales_scripts"], created[0], 41, 9.2),
            ("3-field forms convert 27% better on high-intent pages with no loss in SQL rate.", "conversion", 0.97, ["landing_page", "cro"], created[1], 12, 7.4),
            ("15-second video wins on CPL for Operations audiences; 30s retains better for CFOs.", "creative", 0.95, ["meta", "youtube", "video"], created[2], 18, 6.1),
            ("Trigger-event openers (expansion, RFP, audit) roughly double positive reply rate vs generic openers.", "messaging", 0.9, ["outbound", "hyper_personalization"], None, 63, 8.8),
            ("Naming the incumbent BHS vendor in the first touch lifts replies for CIO personas.", "messaging", 0.84, ["outbound", "linkedin"], None, 22, 5.5),
            ("Tuesday 09:00 local sends produce +22% opens for Operations personas.", "timing", 0.78, ["outbound", "email_marketing"], created[4], 9, 3.9),
            ("Google Search delivers half the CAC of Meta prospecting; Meta works as a retargeting assist in 38% of won journeys.", "channel", 0.91, ["media_buyer", "paid_media"], None, 7, 8.1),
            ("Founder-voice LinkedIn posts drive 3x more profile-sourced leads than company posts.", "channel", 0.83, ["linkedin", "content_strategy"], created[6], 5, 4.7),
            ("Case-study format has the highest save rate; schedule mid-week.", "content", 0.8, ["content_strategy", "social"], None, 6, 3.2),
            ("Comparative claims against named competitors require a disclaimer to pass compliance; unqualified '%' claims get flagged.", "governance", 0.99, ["compliance", "brand_manager", "creative_director"], None, 31, 4.4),
        ]
        for st, cat, conf, applies, exp, times, impact in insights:
            MemoryInsight.objects.create(workspace=ws, statement=st, category=cat, confidence=conf, applies_to=applies, source_experiment=exp, times_applied=times, impact_score=impact,
                                         evidence=[{"type": "experiment", "ref": exp.name} if exp else {"type": "observational", "ref": "attribution + reply intelligence"}])

    # ------------------------------------------------------------------ agents
    def _agents_activity(self, ws, now):
        agents = {a.key: a for a in Agent.objects.filter(workspace=ws)}
        from apps.agents.simulations import simulate

        business = ws.business
        for i, (key, agent) in enumerate(agents.items()):
            n = rnd.randint(4, 30)
            agent.runs_count = n
            agent.success_rate = round(rnd.uniform(0.9, 1.0), 3)
            agent.health_score = int(agent.success_rate * 100)
            agent.last_run_at = now - timedelta(minutes=rnd.randint(2, 900))
            out = simulate(key, business)
            agent.last_summary = out["summary"][:300]
            agent.status = "running" if key in ("sdr", "media_buyer", "reply_intelligence") else "idle"
            agent.save()
            for r in range(3):
                started = now - timedelta(hours=rnd.randint(1, 96))
                AgentRun.objects.create(workspace=ws, agent=agent, trigger=rnd.choice(["schedule", "cmo", "manual", "event"]), status="succeeded", mode="simulation",
                                        input={"task": "scheduled pass"}, output=out, summary=out["summary"], log=[{"t": 0, "msg": "Loaded context"}, {"t": 1, "msg": "Executed"}, {"t": 2, "msg": "Wrote outputs"}],
                                        tokens_used=rnd.randint(1200, 9800), started_at=started, finished_at=started + timedelta(seconds=rnd.randint(8, 140)), duration_ms=rnd.randint(8000, 140000))
        events = [
            ("sdr", "run_finished", "AI SDR booked a meeting with Schiphol Group (Thu 10:00 CET)"), ("reply_intelligence", "classified", "Classified 6 new replies: 3 interested, 1 pricing, 2 not now"),
            ("media_buyer", "reallocation", "Shifted 25% of Meta prospecting budget to Google Search"), ("compliance", "flagged", "Flagged creative C-1043: comparative claim needs disclaimer"),
            ("lead_verification", "purged", "Purged 95 invalid contacts before outbound"), ("market_intelligence", "signal", "New signal: Riyadh Airports USD 1.2B modernization capex"),
            ("creative_testing", "winner", "Hook 'costing you EUR 100 per bag' won at 96% confidence"), ("crm", "sync", "Synced 1,912 records to HubSpot; merged 41 duplicates"),
            ("seo", "rank", "'baggage reconciliation software' moved 12 -> 7"), ("memory", "insight", "New insight written: trigger-event openers ~2x positive replies"),
            ("linkedin", "published", "Founder POV post published: 'Baggage is a data problem...'"), ("cro", "experiment", "Form-length test concluded: 3 fields +27%"),
            ("icp_scoring", "scored", "Scored 4,200 accounts: 462 Tier-1"), ("competitor_intelligence", "signal", "SITA launched 'Bag Journey' campaign in EU"),
            ("attribution", "report", "92% of Q3 revenue attributed with confidence"), ("cmo", "plan", "Weekly plan reconciled: scale outbound, hold LinkedIn, trim YouTube"),
        ]
        for i, (key, kind, msg) in enumerate(events):
            ev = ActivityEvent.objects.create(workspace=ws, agent=agents.get(key), kind=kind, message=msg)
            ActivityEvent.objects.filter(pk=ev.pk).update(created_at=now - timedelta(minutes=7 * i + rnd.randint(0, 6)))

    # ------------------------------------------------------------------ decisions
    def _decisions(self, ws, now):
        agents = {a.key: a for a in Agent.objects.filter(workspace=ws)}
        cards = [
            ("creative_testing", "Campaign #42 is outperforming account average by 62%", "LinkedIn ABM Tier-1 hubs: CPL 3,100 vs account 4,900, meeting rate 2x. Recommend +30% daily budget while CAC stays under target.", "recommendation", "high", 0.91, True, {"type": "scale_campaign", "params": {"pct": 30}}, {"lift_pct": 62, "cpl": 3100}, "pending", 1),
            ("reply_intelligence", "17 Tier-1 prospects responded to the modernization campaign", "Positive intent across Munich, Schiphol, Vienna and 14 others. AI SDR is qualifying and proposing times; 4 meetings already booked.", "insight", "high", 0.93, False, {}, {"replies": 17, "meetings": 4}, "executed", 2),
            ("paid_media", "Google Search has a lower CAC than Meta this week", "Search CAC 2,100 vs Meta 4,200 while converting to meetings at 2x. Recommend shifting 25% of Meta prospecting budget to Search.", "recommendation", "high", 0.88, True, {"type": "apply_allocation", "params": {"meta": -25, "google_search": 40}}, {"meta_cac": 4200, "search_cac": 2100}, "pending", 3),
            ("competitor_intelligence", "Competitor SITA launched a new offer", "'Bag Journey' campaign targets European hubs with a '30% reduction' claim. Counter-positioning brief drafted: audited outcomes + savings calculator CTA.", "alert", "high", 0.86, True, {"type": "create_creative_brief", "params": {"angle": "audited_outcomes"}}, {}, "pending", 4),
            ("icp_scoring", "4,200 new prospects match ICP #2", "Fresh batch scored: 462 Tier-1, 1,134 Tier-2. Enrichment and verification queued; sequence 'Renewal window' has capacity.", "insight", "medium", 0.88, False, {}, {"tier1": 462, "tier2": 1134}, "executed", 5),
            ("sequence", "Approve sequence launch: ICP #3 · GCC greenfield", "196 verified contacts at Hamad, Dubai, Riyadh, Abu Dhabi and Muscat. Compliance gate passed. Daily cap 100.", "approval", "high", 0.9, True, {"type": "launch_sequence", "params": {"contacts": 196}}, {"contacts": 196}, "pending", 6),
            ("compliance", "2 ad creatives need human sign-off", "Both use a comparative claim against a named competitor. Approve with the disclaimer appended, or reject.", "approval", "medium", 0.95, True, {"type": "review_creatives", "params": {"count": 2}}, {}, "pending", 7),
            ("market_intelligence", "Emerging opportunity: GCC airport modernization capex +34% YoY", "Riyadh, Abu Dhabi and Muscat announced programmes. Recommend promoting ICP #3 from draft to approved and a 200-account discovery run.", "opportunity", "high", 0.78, True, {"type": "approve_icps", "params": {"ranks": [3]}}, {}, "pending", 8),
            ("revenue_intelligence", "Why did revenue fall this week?", "Two enterprise deals (Aena, Fraport) slipped to next month on procurement. Marketing-sourced pipeline is up 9% - no channel change recommended.", "insight", "medium", 0.9, False, {}, {"slipped_deals": 2, "pipeline_delta_pct": 9}, "executed", 9),
            ("growth_optimization", "Scale outbound: add 2 mailboxes and activate CIO sequence", "Outbound is the lowest-CAC channel (1,400) with headroom; verified pool supports +300 sends/day within the daily cap.", "recommendation", "high", 0.89, True, {"type": "scale_outbound", "params": {"mailboxes": 2}}, {"cac": 1400}, "pending", 10),
            ("landing_page", "GCC terminal-readiness page ready for review", "Channel-matched to the LinkedIn GCC campaign. Ad -> Page -> Offer -> CTA coherence verified.", "approval", "low", 0.87, True, {"type": "publish_landing_page", "params": {"slug": "gcc-terminal"}}, {}, "pending", 11),
            ("media_buyer", "Trim YouTube by 25%: view-through leads not converting to SQL", "YouTube CPL 3,600 with 0.3x pipeline per lead vs LinkedIn 3.4x. Move 3,000/day to LinkedIn ABM.", "recommendation", "medium", 0.82, True, {"type": "apply_allocation", "params": {"youtube": -25, "linkedin": 10}}, {}, "approved", 12),
            ("business_intelligence", "Knowledge gap: churn reasons missing", "No source describes why customers churn. Connect CRM closed-lost reasons or answer 3 questions so messaging agents can pre-empt objections.", "alert", "medium", 0.9, True, {"type": "request_context", "params": {"fields": ["churn_reasons"]}}, {}, "pending", 13),
            ("cro", "Form-length test concluded: 3 fields +27%", "97% confidence, SQL rate unchanged. Applied to all live pages and written to Marketing Memory.", "insight", "medium", 0.97, False, {}, {"lift_pct": 27}, "executed", 14),
        ]
        for key, title, body, cat, imp, conf, req, action, metrics, st, hrs in cards:
            d = Decision.objects.create(workspace=ws, agent=agents.get(key), title=title, body=body, category=cat, impact=imp, confidence=conf, requires_approval=req, action=action, metrics=metrics, status=st,
                                        resolved_at=now - timedelta(hours=hrs - 1) if st in ("approved", "executed") else None)
            Decision.objects.filter(pk=d.pk).update(created_at=now - timedelta(hours=hrs, minutes=rnd.randint(0, 50)))

    # ------------------------------------------------------------------ connectors
    def _connectors(self, ws):
        for key, label in [("hubspot", "SkyBag Systems (portal 8841203)"), ("google_ads", "SkyBag EU · 493-221-0087"), ("linkedin_ads", "SkyBag Systems company page"),
                           ("meta_ads", "act_2049112 · SkyBag"), ("apollo", "growth@skybag.example.com"), ("instantly", "4 mailboxes · warm"), ("stripe", "SkyBag Systems Ltd"), ("ga4", "GA4 · 3921003")]:
            c = Connector.objects.create(workspace=ws, provider=key, status="simulated", account_label=label,
                                         health={"ok": False, "message": "Simulated - add credentials in .env or here to go live", "checked_at": timezone.now().isoformat()})
