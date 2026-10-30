"""Orchestrates the four stages and records a trace for observability."""
from __future__ import annotations

import time

from .config import Settings
from .draft import draft_offline, draft_with_llm
from .extract import extract_rules, refine_with_llm
from .knowledge import KnowledgeBase
from .llm import LLM, get_llm
from .schemas import CopilotResult, Evidence, Extraction, Intent, Lead, ServiceLine, TraceStep
from .score import score_lead


class LeadCopilot:
    def __init__(self, settings: Settings | None = None, llm: LLM | None = None, use_llm: bool = True):
        self.settings = settings or Settings.from_env()
        self.kb = KnowledgeBase.load()
        self.llm = llm if llm is not None else (get_llm(self.settings) if use_llm else None)

    @property
    def provider(self) -> str:
        return self.llm.name if self.llm else "offline"

    def _retrieve(self, lead: Lead, ex: Extraction) -> list[Evidence]:
        if ex.intent in (Intent.CAREER, Intent.VENDOR, Intent.SPAM, Intent.UNCLEAR):
            return []
        query = " ".join([ex.service_line.value.replace("_", " "), ex.industry.replace("_", " "),
                          *ex.requirements, lead.message])
        offers = self.kb.search(query, self.settings.top_k_offers, {"service", "product", "program"})
        cases = self.kb.search(query, self.settings.top_k_cases, {"case_study"})
        extra = self.kb.search("discovery audit lifecycle", 1, {"process"}) if ex.intent == Intent.NEW_PROJECT else []
        return offers + cases + extra

    def process(self, lead: Lead) -> CopilotResult:
        trace: list[TraceStep] = []

        def timed(step, method, fn, detail=""):
            t0 = time.perf_counter()
            out = fn()
            trace.append(TraceStep(step=step, ms=round((time.perf_counter() - t0) * 1000, 1), method=method, detail=detail))
            return out

        ex = timed("extract", "rules", lambda: extract_rules(lead, self.settings))
        if self.llm and ex.intent not in (Intent.SPAM,):
            refined = timed("extract_llm", self.llm.name, lambda: refine_with_llm(self.llm, lead, ex))
            ex = refined
        score = timed("score", "deterministic", lambda: score_lead(lead, ex, self.settings))
        evidence = timed("retrieve", "tfidf", lambda: self._retrieve(lead, ex), "knowledge base search")
        proposal = timed("draft", "template", lambda: draft_offline(lead, ex, score, evidence))
        if proposal and self.llm:
            proposal = timed("draft_llm", self.llm.name, lambda: draft_with_llm(self.llm, lead, ex, score, evidence, proposal))
        return CopilotResult(lead=lead, extraction=ex, score=score, evidence=evidence, proposal=proposal,
                             trace=trace, llm_provider=self.provider)
