"""Typed data contracts shared by the pipeline, API and UI."""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Intent(str, Enum):
    NEW_PROJECT = "new_project"
    PRODUCT_DEMO = "product_demo"
    TRAINING = "training"
    CAREER = "career"
    VENDOR = "vendor_solicitation"
    SPAM = "spam_or_irrelevant"
    UNCLEAR = "unclear"


class ServiceLine(str, Enum):
    AI_AUTOMATION = "ai_automation"
    SOFTWARE_DEV = "software_development"
    CLOUD = "cloud_infrastructure"
    DIGITAL_MARKETING = "digital_marketing_seo"
    PRODUCT = "proprietary_product"
    TRAINING = "training_bitelevate"
    UNKNOWN = "unknown"


class Urgency(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class Tier(str, Enum):
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"
    NOT_A_PROSPECT = "NOT_A_PROSPECT"


class Route(str, Enum):
    SALES = "sales"
    PRODUCT_TEAM = "product_team"
    BITELEVATE_TEAM = "bitelevate_team"
    HR = "hr"
    IGNORE = "ignore"


class Lead(BaseModel):
    name: str = ""
    company: str = ""
    email: str = ""
    message: str = Field(min_length=1, max_length=4000)


class Extraction(BaseModel):
    intent: Intent
    service_line: ServiceLine = ServiceLine.UNKNOWN
    industry: str = "unknown"
    budget_inr: Optional[float] = None
    budget_text: Optional[str] = None
    timeline_text: Optional[str] = None
    urgency: Urgency = Urgency.UNKNOWN
    requirements: list[str] = Field(default_factory=list)
    language: str = "en"
    summary: str = ""
    method: str = "rules"  # rules | rules+llm


class ScoreComponent(BaseModel):
    name: str
    points: int
    max_points: int
    reason: str


class LeadScore(BaseModel):
    score: int
    tier: Tier
    route: Route
    recommended_sla: str
    components: list[ScoreComponent]
    notes: list[str] = Field(default_factory=list)


class Evidence(BaseModel):
    id: str
    type: str
    title: str
    url: str = ""
    score: float
    snippet: str = ""


class Proposal(BaseModel):
    subject: str
    body: str
    discovery_questions: list[str] = Field(default_factory=list)
    cited_ids: list[str] = Field(default_factory=list)
    generated_by: str = "template"
    requires_human_review: bool = True
    guardrail_notes: list[str] = Field(default_factory=list)


class TraceStep(BaseModel):
    step: str
    ms: float
    method: str
    detail: str = ""


class CopilotResult(BaseModel):
    lead: Lead
    extraction: Extraction
    score: LeadScore
    evidence: list[Evidence]
    proposal: Optional[Proposal] = None
    trace: list[TraceStep] = Field(default_factory=list)
    llm_provider: str = "offline"
