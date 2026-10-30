"""Stage 2 - transparent, deterministic lead scoring (the LLM never sets the score)."""
from __future__ import annotations

import re

from .config import Settings
from .schemas import Extraction, Intent, Lead, LeadScore, Route, ScoreComponent, Tier, Urgency
from .extract import SERVICE_KW, hits

FREE_DOMAINS = {"gmail.com", "yahoo.com", "yahoo.in", "outlook.com", "hotmail.com", "rediffmail.com",
                "icloud.com", "proton.me", "mail.ru", "aol.com"}
EXPLICIT_ASK = re.compile(r"\b(proposal|quote|quotation|estimate|demo|meeting|schedule a|set up a call|"
                          r"book a call|have a call|a call|discuss)\b", re.I)
ROUTES = {Intent.NEW_PROJECT: Route.SALES, Intent.PRODUCT_DEMO: Route.PRODUCT_TEAM,
          Intent.TRAINING: Route.BITELEVATE_TEAM, Intent.CAREER: Route.HR, Intent.VENDOR: Route.IGNORE,
          Intent.SPAM: Route.IGNORE, Intent.UNCLEAR: Route.SALES}
SLA = {Tier.HOT: "Respond within 1 hour; assign a senior owner.",
       Tier.WARM: "Respond the same business day.",
       Tier.COLD: "Respond within 2 business days; add to nurture list.",
       Tier.NOT_A_PROSPECT: "No sales action; route or archive."}


def _budget_points(budget: float | None, floor: float) -> tuple[int, str]:
    if budget is None:
        return 0, "No budget stated."
    if budget < floor:
        return 0, f"Budget (~INR {budget:,.0f}) is below the minimum viable engagement."
    if budget < 100_000:
        return 5, f"Small budget (~INR {budget:,.0f})."
    if budget < 500_000:
        return 15, f"Moderate budget (~INR {budget:,.0f})."
    return 25, f"Strong budget (~INR {budget:,.0f})."


def score_lead(lead: Lead, ex: Extraction, settings: Settings) -> LeadScore:
    route = ROUTES[ex.intent]
    if ex.intent in (Intent.CAREER, Intent.VENDOR, Intent.SPAM):
        reason = {"career": "Job/internship enquiry - forward to HR.",
                  "vendor_solicitation": "Inbound vendor pitch - not a buyer.",
                  "spam_or_irrelevant": "Spam or irrelevant message."}[ex.intent.value]
        return LeadScore(score=0, tier=Tier.NOT_A_PROSPECT, route=route, recommended_sla=SLA[Tier.NOT_A_PROSPECT],
                         components=[ScoreComponent(name="intent", points=0, max_points=100, reason=reason)])

    comps: list[ScoreComponent] = []
    b_pts, b_reason = _budget_points(ex.budget_inr, settings.budget_floor_inr)
    comps.append(ScoreComponent(name="budget", points=b_pts, max_points=25, reason=b_reason))

    u_pts = {Urgency.HIGH: 20, Urgency.MEDIUM: 12, Urgency.LOW: 4, Urgency.UNKNOWN: 5}[ex.urgency]
    comps.append(ScoreComponent(name="urgency", points=u_pts, max_points=20,
                                reason=f"Urgency {ex.urgency.value}" + (f" ('{ex.timeline_text}')." if ex.timeline_text else ".")))

    group = SERVICE_KW.get(ex.service_line, [])
    n_hits = len(hits(lead.message, group))
    s_pts = min(20, 5 * n_hits + (5 if len(lead.message.split()) >= 30 else 0))
    comps.append(ScoreComponent(name="specificity", points=s_pts, max_points=20,
                                reason=f"{n_hits} relevant requirement signal(s); {len(lead.message.split())} words."))

    base = {Intent.NEW_PROJECT: 15, Intent.PRODUCT_DEMO: 15, Intent.TRAINING: 8, Intent.UNCLEAR: 0}[ex.intent]
    asks = bool(EXPLICIT_ASK.search(lead.message)) and ex.intent in (Intent.NEW_PROJECT, Intent.PRODUCT_DEMO)
    comps.append(ScoreComponent(name="intent_strength", points=base + (5 if asks else 0), max_points=20,
                                reason=f"Intent '{ex.intent.value}'" + ("; explicit ask for proposal/demo/call." if asks else ".")))

    domain = lead.email.split("@")[-1].lower() if "@" in lead.email else ""
    c_pts = (5 if lead.company.strip() else 0) + (7 if domain and domain not in FREE_DOMAINS else 0) + (3 if domain else 0)
    comps.append(ScoreComponent(name="contact_quality", points=c_pts, max_points=15,
                                reason=f"Company {'given' if lead.company.strip() else 'missing'}; "
                                       f"{'business' if domain and domain not in FREE_DOMAINS else 'free/missing'} e-mail domain."))

    total = sum(c.points for c in comps)
    tier = Tier.HOT if total >= 65 else Tier.WARM if total >= 40 else Tier.COLD
    notes: list[str] = []
    if ex.budget_inr is not None and ex.budget_inr < settings.budget_floor_inr and tier != Tier.COLD:
        tier = Tier.COLD
        notes.append("Tier capped at COLD by budget floor rule.")
    return LeadScore(score=total, tier=tier, route=route, recommended_sla=SLA[tier], components=comps, notes=notes)
