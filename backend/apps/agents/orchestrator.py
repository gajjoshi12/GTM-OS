"""
The AI CMO orchestration layer.

- `ensure_agents(workspace)`      materialise every registry agent for a workspace
- `run_agent(...)`                 run one specialist (live LLM or simulation)
- `interpret_command(...)`         natural-language command bar -> plan -> runs
- `derive_plan(business)`          founder sentence -> full GTM derivation (spec 1.3)
- `resolve_decision(...)`          Approve / Reject / Ask AI on a decision card
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

from django.db import transaction
from django.utils import timezone

from ai.client import llm
from apps.core.models import BrandGuidelines, BusinessProfile, ControlSettings

from .models import ActivityEvent, Agent, AgentRun, Command, Decision
from .registry import AGENT_BY_KEY, AGENTS, system_prompt_for
from .simulations import simulate

log = logging.getLogger(__name__)


# --------------------------------------------------------------------------- context
def business_context(workspace) -> str:
    b = getattr(workspace, "business", None)
    if not b:
        return "No business profile yet."
    return json.dumps(
        {
            "company": b.company_name, "website": b.website, "industry": b.industry,
            "description": b.description, "founder_brief": b.founder_brief, "currency": b.currency,
            "revenue_goal": float(b.revenue_goal), "marketing_budget": float(b.marketing_budget),
            "gross_margin_pct": float(b.gross_margin_pct), "target_geographies": b.target_geographies,
            "business_model": b.business_model, "average_deal_size": float(b.average_deal_size),
            "sales_cycle_days": b.sales_cycle_days, "derived_plan": b.derived_plan,
        },
        indent=2, default=str,
    )


def brand_rules(workspace) -> str:
    br = getattr(workspace, "brand", None)
    if not br:
        return "Default: confident, precise, outcome-led. No hype, no unverifiable claims."
    return json.dumps(
        {"tone": br.tone, "voice_rules": br.voice_rules, "preferred": br.vocabulary_preferred,
         "banned": br.vocabulary_banned, "forbidden_claims": br.forbidden_claims, "disclaimer": br.legal_disclaimer},
        indent=2,
    )


def ensure_agents(workspace) -> list[Agent]:
    existing = {a.key: a for a in Agent.objects.filter(workspace=workspace)}
    created = []
    for spec in AGENTS:
        if spec["key"] not in existing:
            created.append(Agent(workspace=workspace, key=spec["key"], name=spec["name"], group=spec["group"],
                                 description=spec["description"], judged_on=spec["judged_on"]))
    if created:
        Agent.objects.bulk_create(created)
    return list(Agent.objects.filter(workspace=workspace))


def ensure_settings(workspace):
    ControlSettings.objects.get_or_create(workspace=workspace)
    BrandGuidelines.objects.get_or_create(workspace=workspace)


def log_event(workspace, kind: str, message: str, agent: Agent | None = None, **meta):
    return ActivityEvent.objects.create(workspace=workspace, agent=agent, kind=kind, message=message[:300], meta=meta)


# --------------------------------------------------------------------------- running agents
def run_agent(workspace, key: str, payload: dict | None = None, trigger: str = AgentRun.Trigger.MANUAL) -> AgentRun:
    payload = payload or {}
    spec = AGENT_BY_KEY[key]
    agent, _ = Agent.objects.get_or_create(
        workspace=workspace, key=key,
        defaults={"name": spec["name"], "group": spec["group"], "description": spec["description"], "judged_on": spec["judged_on"]},
    )
    run = AgentRun.objects.create(workspace=workspace, agent=agent, trigger=trigger, input=payload,
                                  status=AgentRun.Status.RUNNING, started_at=timezone.now(),
                                  mode="live" if llm.live else "simulation")
    agent.status = Agent.Status.RUNNING
    agent.save(update_fields=["status"])
    log_event(workspace, "run_started", f"{agent.name} started ({run.mode})", agent, run_id=run.id)

    t0 = time.perf_counter()
    logs: list[dict] = [{"t": 0, "msg": f"Loaded business context and brand rules"}]
    try:
        if llm.live:
            logs.append({"t": 1, "msg": f"Calling {llm.model} via {llm.provider_name}"})
            output = llm.complete_json(
                system_prompt_for(spec, business_context(workspace), brand_rules(workspace)),
                json.dumps({"task": payload.get("task") or f"Run your standard operating pass for this business.", "input": payload}, default=str),
                max_tokens=8000,
            )
        else:
            logs.append({"t": 1, "msg": f"No {llm.key_env_var} - running deterministic simulation"})
            output = simulate(key, getattr(workspace, "business", None), payload)
        if not isinstance(output, dict):
            output = {"summary": str(output), "findings": [], "decisions": [], "artifacts": {}}

        decisions = _materialise_decisions(workspace, agent, output.get("decisions") or [])
        logs.append({"t": 2, "msg": f"Produced {len(output.get('findings', []))} findings, {len(decisions)} decision cards"})

        run.output = output
        run.summary = output.get("summary", "")[:2000]
        run.status = AgentRun.Status.SUCCEEDED
        agent.last_summary = run.summary[:300]
        agent.success_rate = round(agent.success_rate * 0.9 + 0.1, 3)
        agent.status = Agent.Status.IDLE
    except Exception as exc:  # noqa: BLE001
        log.exception("agent run failed")
        run.status = AgentRun.Status.FAILED
        run.summary = f"Failed: {exc}"
        logs.append({"t": 2, "msg": f"Error: {exc}"})
        agent.status = Agent.Status.ERROR
        agent.success_rate = round(agent.success_rate * 0.9, 3)
    finally:
        run.duration_ms = int((time.perf_counter() - t0) * 1000)
        run.finished_at = timezone.now()
        run.log = logs
        run.save()
        agent.runs_count += 1
        agent.last_run_at = run.finished_at
        agent.health_score = int(min(100, max(0, agent.success_rate * 100)))
        agent.save()
        log_event(workspace, "run_finished", f"{agent.name}: {run.summary[:200]}", agent, run_id=run.id, status=run.status)
    return run


def _materialise_decisions(workspace, agent: Agent, items: list[dict]) -> list[Decision]:
    controls = getattr(workspace, "controls", None)
    mode = controls.mode_for(agent.key) if controls else ControlSettings.Mode.APPROVAL
    out = []
    for d in items:
        requires = bool(d.get("requires_approval", True))
        if mode == ControlSettings.Mode.FULL and d.get("category") != "approval":
            requires = False  # full autonomy: informational unless explicitly gated
        if mode == ControlSettings.Mode.COPILOT:
            requires = True  # copilot: humans execute everything
        out.append(Decision(
            workspace=workspace, agent=agent, title=str(d.get("title", "Untitled"))[:200], body=str(d.get("body", "")),
            category=d.get("category") if d.get("category") in Decision.Category.values else Decision.Category.RECOMMENDATION,
            impact=d.get("impact") if d.get("impact") in Decision.Impact.values else Decision.Impact.MEDIUM,
            confidence=float(d.get("confidence", 0.8)), requires_approval=requires,
            action=d.get("action") or {}, metrics=d.get("metrics") or {},
            status=Decision.Status.PENDING if requires else Decision.Status.EXECUTED,
        ))
    return Decision.objects.bulk_create(out)


# --------------------------------------------------------------------------- command bar
INTENT_RULES = [
    ("find_prospects_and_launch", ["find", "companies", "launch"], ["lead_discovery", "icp_scoring", "lead_enrichment", "lead_verification", "research", "hyper_personalization", "sequence", "compliance"]),
    ("find_prospects", ["find", "prospect"], ["lead_discovery", "icp_scoring", "lead_enrichment", "lead_verification"]),
    ("find_prospects", ["find", "companies"], ["lead_discovery", "icp_scoring", "lead_enrichment", "lead_verification"]),
    ("generate_ads", ["ads"], ["creative_director", "video", "creative_testing", "paid_media", "compliance"]),
    ("generate_ads", ["ad ", "creative"], ["creative_director", "creative_testing", "compliance"]),
    ("diagnose_revenue", ["why", "revenue"], ["revenue_intelligence", "attribution", "analytics"]),
    ("diagnose_revenue", ["revenue", "fall"], ["revenue_intelligence", "attribution"]),
    ("new_segment", ["segment"], ["market_intelligence", "icp", "icp_scoring"]),
    ("book_meetings", ["meeting"], ["icp_scoring", "sequence", "sdr", "paid_media", "growth_optimization"]),
    ("content", ["content", "post", "linkedin", "blog", "seo"], ["content_strategy", "linkedin", "seo", "social", "brand_manager"]),
    ("budget", ["budget", "spend", "reallocate"], ["media_buyer", "paid_media", "revenue_intelligence"]),
    ("competitor", ["competitor"], ["competitor_intelligence", "creative_director"]),
    ("landing_page", ["landing", "page", "conversion"], ["landing_page", "cro"]),
]


def _rule_intent(text: str) -> tuple[str, list[str]]:
    t = text.lower()
    for intent, needles, agents in INTENT_RULES:
        if all(n in t for n in needles):
            return intent, agents
    return "general", ["cmo", "growth_optimization"]


def interpret_command(workspace, user, text: str) -> Command:
    cmd = Command.objects.create(workspace=workspace, user=user, text=text)
    intent, agent_keys = _rule_intent(text)
    plan: dict[str, Any] = {"intent": intent, "steps": [], "assumptions": []}

    if llm.live:
        try:
            spec = AGENT_BY_KEY["cmo"]
            available = ", ".join(a["key"] for a in AGENTS)
            planned = llm.complete_json(
                system_prompt_for(spec, business_context(workspace), brand_rules(workspace))
                + f"\n\nYou are interpreting a founder command. Available agent keys: {available}.\n"
                  "Return JSON: {\"intent\": str, \"response\": str (2-4 sentences to the founder), "
                  "\"agents\": [agent_key...] in execution order, \"assumptions\": [str], \"expected_outcome\": str}",
                text, max_tokens=3000, effort="medium",
            )
            intent = planned.get("intent", intent)
            agent_keys = [k for k in planned.get("agents", agent_keys) if k in AGENT_BY_KEY] or agent_keys
            plan["assumptions"] = planned.get("assumptions", [])
            plan["expected_outcome"] = planned.get("expected_outcome", "")
            cmd.response = planned.get("response", "")
        except Exception as exc:  # noqa: BLE001
            log.warning("CMO planning fell back to rules: %s", exc)

    cmd.intent = intent
    cmd.status = Command.Status.EXECUTING
    cmd.plan = plan
    cmd.save()
    log_event(workspace, "command", f"Founder command: {text}", None, intent=intent)

    runs = []
    for key in agent_keys:
        run = run_agent(workspace, key, {"task": text, "command_id": cmd.id}, trigger=AgentRun.Trigger.COMMAND)
        runs.append(run)
        plan["steps"].append({"agent": key, "run_id": run.id, "status": run.status, "summary": run.summary})

    cmd.runs.set(runs)
    if not cmd.response:
        names = ", ".join(AGENT_BY_KEY[k]["name"] for k in agent_keys)
        cmd.response = (
            f"Understood. I routed this to {names}. "
            + " ".join(r.summary for r in runs[:3] if r.summary)
        )[:3000]
    cmd.plan = plan
    cmd.status = Command.Status.DONE if all(r.status == AgentRun.Status.SUCCEEDED for r in runs) else Command.Status.FAILED
    cmd.save()
    return cmd


# --------------------------------------------------------------------------- onboarding derivation
def derive_plan(business: BusinessProfile) -> dict:
    """Founder sentence -> segments, accounts, personas, geos, messaging, channels, budget, experiments."""
    if llm.live:
        try:
            spec = AGENT_BY_KEY["cmo"]
            plan = llm.complete_json(
                system_prompt_for(spec, business_context(business.workspace), brand_rules(business.workspace))
                + "\n\nDerive the full go-to-market plan from the founder brief. Return JSON with keys: "
                  "segments[{name, why, priority}], target_accounts_estimate (int), decision_makers[{title, pain, angle}], "
                  "geographies[str], messaging{core_promise, proof_points[], objections[]}, "
                  "channels[{channel, role, budget_share_pct, expected_cac}], content_themes[str], "
                  "offers[str], landing_pages[{audience, headline}], experiment_backlog[{hypothesis, channel}], "
                  "monthly_targets{prospects, meetings, pipeline}.",
                business.founder_brief or business.description, max_tokens=8000,
            )
            if isinstance(plan, dict):
                return plan
        except Exception as exc:  # noqa: BLE001
            log.warning("derive_plan fell back to simulation: %s", exc)
    return _simulated_plan(business)


def _simulated_plan(b: BusinessProfile) -> dict:
    geo = (b.target_geographies or ["Europe"])[0]
    industry = b.industry or "enterprise software"
    goal = float(b.revenue_goal or 0)
    acv = float(b.average_deal_size or 0) or max(goal / 20, 1)
    budget = float(b.marketing_budget or 0)
    customers = max(1, int(goal / acv)) if goal else 12
    return {
        "segments": [
            {"name": f"{geo} enterprises with an active modernization project", "why": "Highest intent + budget already allocated", "priority": 1},
            {"name": "Mid-market operators on a legacy incumbent nearing renewal", "why": "Switching window every 3-5 years", "priority": 2},
            {"name": "Greenfield projects in emerging regions (GCC / SEA)", "why": "Rising capex, fewer incumbents", "priority": 3},
        ],
        "target_accounts_estimate": 4200,
        "decision_makers": [
            {"title": "Head of Operations", "pain": "Manual processes, error rates, SLA penalties", "angle": "Operational cost reduction with audited proof"},
            {"title": "CFO", "pain": "Cost of inaction, payback uncertainty", "angle": "Savings calculator + 90-day payback"},
            {"title": "CIO / Head of IT", "pain": "Integration risk with legacy systems", "angle": "Reference architecture + migration playbook"},
        ],
        "geographies": b.target_geographies or [geo, "Middle East"],
        "messaging": {
            "core_promise": f"Cut {industry} operating cost measurably within one quarter - proven with audited customer outcomes.",
            "proof_points": ["Audited customer outcomes", "90-day payback", "Integrates with incumbent systems"],
            "objections": ["We already have a vendor", "Integration effort", "Procurement timeline"],
        },
        "channels": [
            {"channel": "outbound", "role": "Primary pipeline engine", "budget_share_pct": 30, "expected_cac": 1400},
            {"channel": "google_search", "role": "High-intent inbound", "budget_share_pct": 25, "expected_cac": 2100},
            {"channel": "linkedin", "role": "Enterprise authority + ABM", "budget_share_pct": 25, "expected_cac": 3100},
            {"channel": "meta", "role": "Retargeting only", "budget_share_pct": 10, "expected_cac": 4200},
            {"channel": "organic", "role": "Compounding SEO + content", "budget_share_pct": 10, "expected_cac": 900},
        ],
        "content_themes": ["Industry insight", "Customer problem", "Case study", "Founder POV", "Product insight"],
        "offers": ["Free operational-cost audit", "Savings calculator", "Reference-architecture workshop"],
        "landing_pages": [
            {"audience": "LinkedIn / enterprise", "headline": "Modernize without the migration risk"},
            {"audience": "Google / high intent", "headline": f"The {industry} platform with audited 90-day payback"},
            {"audience": "Meta / education", "headline": "What your current system is really costing you"},
        ],
        "experiment_backlog": [
            {"hypothesis": "Cost-saving messaging beats productivity messaging for CFOs", "channel": "outbound"},
            {"hypothesis": "3-field forms convert better than 6-field on high-intent pages", "channel": "landing_page"},
            {"hypothesis": "15s video beats 30s on Meta retargeting", "channel": "meta"},
        ],
        "monthly_targets": {"prospects": 1500, "meetings": 30, "pipeline": round(goal / 4) if goal else 5000000, "customers": customers},
        "budget_total": budget,
    }


# --------------------------------------------------------------------------- decisions
def resolve_decision(decision: Decision, action: str, user, message: str = "") -> Decision:
    now = timezone.now()
    if action == "approve":
        decision.status = Decision.Status.APPROVED
        decision.resolved_at, decision.resolved_by = now, user
        _execute_action(decision)
        log_event(decision.workspace, "decision_approved", f"Approved: {decision.title}", decision.agent)
    elif action == "reject":
        decision.status = Decision.Status.REJECTED
        decision.resolved_at, decision.resolved_by = now, user
        log_event(decision.workspace, "decision_rejected", f"Rejected: {decision.title}", decision.agent)
    elif action == "ask":
        answer = _ask_ai(decision, message)
        decision.conversation = list(decision.conversation) + [
            {"role": "user", "text": message, "at": now.isoformat()},
            {"role": "ai", "text": answer, "at": timezone.now().isoformat()},
        ]
    decision.save()
    return decision


def _execute_action(decision: Decision):
    """Apply approved actions that have a concrete effect on domain state."""
    from apps.campaigns.models import BudgetAllocation, Campaign
    from apps.outbound.models import Sequence

    a = decision.action or {}
    kind = a.get("type")
    ws = decision.workspace
    try:
        if kind == "apply_allocation":
            for ch, pct in (a.get("params") or {}).items():
                for camp in Campaign.objects.filter(workspace=ws, channel=ch, status=Campaign.Status.ACTIVE):
                    new = float(camp.daily_budget) * (1 + float(pct) / 100)
                    BudgetAllocation.objects.create(workspace=ws, date=timezone.now().date(), channel=ch,
                                                    previous_daily=camp.daily_budget, new_daily=new,
                                                    reason=decision.title, decision=decision, applied=True)
                    camp.daily_budget = new
                    camp.save(update_fields=["daily_budget"])
        elif kind == "launch_sequence":
            Sequence.objects.filter(workspace=ws, status=Sequence.Status.PENDING_APPROVAL).update(status=Sequence.Status.ACTIVE)
        elif kind == "scale_campaign":
            pct = float((a.get("params") or {}).get("pct", 20))
            camp = Campaign.objects.filter(workspace=ws, status=Campaign.Status.ACTIVE).order_by("-revenue").first()
            if camp:
                camp.daily_budget = float(camp.daily_budget) * (1 + pct / 100)
                camp.save(update_fields=["daily_budget"])
        decision.status = Decision.Status.EXECUTED
    except Exception as exc:  # noqa: BLE001
        log.warning("action execution failed: %s", exc)


def _ask_ai(decision: Decision, question: str) -> str:
    if llm.live:
        try:
            spec = AGENT_BY_KEY[decision.agent.key if decision.agent else "cmo"]
            return llm.complete(
                system_prompt_for(spec, business_context(decision.workspace), brand_rules(decision.workspace))
                + "\n\nAnswer the founder's question about one of your decision cards in plain prose (no JSON), max 120 words.",
                json.dumps({"decision": {"title": decision.title, "body": decision.body, "metrics": decision.metrics}, "question": question}),
                max_tokens=1500, effort="medium",
            )
        except Exception as exc:  # noqa: BLE001
            log.warning("ask-ai fell back: %s", exc)
    return (
        f"This recommendation is based on {decision.confidence:.0%} confidence from the {decision.agent.name if decision.agent else 'AI CMO'}. "
        f"{decision.body} If you approve, the action `{(decision.action or {}).get('type', 'noop')}` is applied within your guardrails "
        f"and can be reversed from the Campaigns or Outbound views."
    )
