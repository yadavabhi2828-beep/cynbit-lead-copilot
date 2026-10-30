"""REST API:  uvicorn api:app --reload   ->  POST /v1/triage"""
from __future__ import annotations

from fastapi import FastAPI

from copilot.pipeline import LeadCopilot
from copilot.schemas import CopilotResult, Lead

app = FastAPI(title="Cynbit Lead-to-Proposal Copilot", version="1.0.0")
_copilot = LeadCopilot()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "llm_provider": _copilot.provider, "kb_documents": len(_copilot.kb.docs)}


@app.post("/v1/triage", response_model=CopilotResult)
def triage(lead: Lead) -> CopilotResult:
    """Classify, score, ground and draft a first response for one inbound lead."""
    return _copilot.process(lead)
