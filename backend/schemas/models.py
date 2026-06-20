from __future__ import annotations

import operator
from typing import Optional, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field, field_validator


# ─── REST Request / Response ──────────────────────────────────────────────────

class IdeaRequest(BaseModel):
    idea: Annotated[str, Field(min_length=20, max_length=2000)]

    @field_validator("idea")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class AnalyzeResponse(BaseModel):
    run_id: str


class ChatRequest(BaseModel):
    message: Annotated[str, Field(min_length=1, max_length=1000)]

    @field_validator("message")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class ChatResponse(BaseModel):
    response: str


# ─── Per-Agent Output Models ──────────────────────────────────────────────────

class ProcessedIdea(BaseModel):
    core_idea: str
    industry: str
    target_customer: str
    geography: str
    problem_solved: str
    proposed_solution: str


def _clamp(v, default: float = 5.0) -> float:
    try:
        return max(0.0, min(10.0, float(v)))
    except (TypeError, ValueError):
        return default


class MarketOutput(BaseModel):
    tam: str
    sam: str
    som_year1: str
    growth_rate: str
    demand_signals: list[str]
    market_score: float = 5.0
    summary: str

    @field_validator('market_score', mode='before')
    @classmethod
    def clamp_score(cls, v): return _clamp(v)


class CompetitorInfo(BaseModel):
    name: str
    strengths: list[str] = Field(max_length=2)
    weaknesses: list[str] = Field(max_length=2)
    funding: str = "Unknown"


class CompetitorOutput(BaseModel):
    competitors: list[CompetitorInfo]
    market_gap: str
    differentiation_opportunity: str
    competition_score: float = 5.0
    summary: str

    @field_validator('competition_score', mode='before')
    @classmethod
    def clamp_score(cls, v): return _clamp(v)


class RevenueProjection(BaseModel):
    year: str
    revenue_inr: float
    label: str


class FinancialOutput(BaseModel):
    revenue_model: str
    estimated_cac: str
    estimated_ltv: str
    ltv_cac_ratio: float
    breakeven_months: int
    financial_score: float = 5.0
    summary: str
    revenue_projections: list[RevenueProjection] = Field(default_factory=list)

    @field_validator('financial_score', mode='before')
    @classmethod
    def clamp_score(cls, v): return _clamp(v)


class RiskItem(BaseModel):
    level: str
    description: str
    mitigation: str


class RiskOutput(BaseModel):
    market_risk: RiskItem
    regulatory_risk: RiskItem
    technical_risk: RiskItem
    competitive_risk: RiskItem
    risk_score: float = 5.0
    summary: str

    @field_validator('risk_score', mode='before')
    @classmethod
    def clamp_score(cls, v): return _clamp(v)


class FinalReport(BaseModel):
    verdict: str = Field(pattern="^(GO|NO-GO)$")
    confidence: int = Field(ge=0, le=100)
    overall_score: float = 5.0
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    executive_summary: str
    top_3_strengths: list[str] = Field(min_length=1)
    top_3_risks: list[str] = Field(min_length=1)
    recommended_next_steps: list[str] = Field(min_length=1)

    @field_validator('overall_score', mode='before')
    @classmethod
    def clamp_overall(cls, v): return _clamp(v)

    @field_validator('confidence', mode='before')
    @classmethod
    def clamp_confidence(cls, v):
        try: return max(0, min(100, int(v)))
        except: return 50

    @field_validator('score_breakdown', mode='before')
    @classmethod
    def clamp_breakdown(cls, v):
        if not isinstance(v, dict): return {}
        return {k: _clamp(val) for k, val in v.items()}


class PivotSuggestion(BaseModel):
    title: str
    description: str
    key_change: str
    potential: str


class PivotOutput(BaseModel):
    reasoning: str
    pivots: list[PivotSuggestion]


# ─── LangGraph State ──────────────────────────────────────────────────────────

class StartupState(TypedDict):
    raw_idea: str
    processed_idea: Optional[ProcessedIdea]
    market_research: Optional[MarketOutput]
    competitor_analysis: Optional[CompetitorOutput]
    financial_feasibility: Optional[FinancialOutput]
    risk_assessment: Optional[RiskOutput]
    agent_errors: Annotated[list[str], operator.add]
    final_report: Optional[FinalReport]
    pivot_suggestions: Optional[PivotOutput]
    stream_events: Annotated[list[dict], operator.add]


# ─── WebSocket Event Models ───────────────────────────────────────────────────

class WSEvent(BaseModel):
    type: str
    agent: Optional[str] = None
    chunk: Optional[str] = None
    data: Optional[dict] = None
    message: Optional[str] = None
