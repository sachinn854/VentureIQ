from pydantic import BaseModel
from backend.llm_factory import get_llm
from backend.schemas.models import StartupState, FinancialOutput, RevenueProjection, ProcessedIdea
from backend.tools.search_tool import search_many
from backend.tools.calculator_tool import ltv_cac_ratio, breakeven_months, score_financials

class _FinancialRaw(BaseModel):
    revenue_model: str
    estimated_cac_inr: float
    estimated_ltv_inr: float
    year1_revenue_inr: float
    year2_revenue_inr: float
    year3_revenue_inr: float
    summary: str
_llm = get_llm(max_tokens=2048).with_structured_output(_FinancialRaw)

_SYSTEM = """You are a startup financial analyst.
Based on the idea and search results, estimate:
- The most suitable revenue model (SaaS / Marketplace / B2B Services / D2C / etc.)
- estimated_cac_inr: Customer Acquisition Cost in INR (realistic estimate)
- estimated_ltv_inr: Lifetime Value per customer in INR
- year1_revenue_inr: Realistic Year 1 total revenue in INR (conservative estimate)
- year2_revenue_inr: Year 2 total revenue in INR (assuming 2-3x growth)
- year3_revenue_inr: Year 3 total revenue in INR (assuming continued growth)
- summary: 2-3 sentence financial outlook

Use Indian market benchmarks. Be realistic, not optimistic. All values must be numbers (no currency symbols)."""
def _fmt_inr(val: float) -> str:
    if val >= 1e7:
        return f"â‚¹{val / 1e7:.1f}Cr"
    elif val >= 1e5:
        return f"â‚¹{val / 1e5:.1f}L"
    return f"â‚¹{val:,.0f}"
async def run_financial_feasibility(state: StartupState) -> dict:
    events = list(state.get("stream_events", []))
    errors = list(state.get("agent_errors", []))

    events.append({"type": "agent_start", "agent": "financial_feasibility"})

    try:
        idea: ProcessedIdea = state.get("processed_idea")
        industry = idea.industry if idea else "technology"

        queries = [
            f"average CAC LTV {industry} startup India benchmark 2025",
            f"{industry} SaaS pricing revenue model India",
        ]
        search_results = await search_many(queries, max_results=4)
        context = _format_results(queries, search_results)

        raw: _FinancialRaw = await _llm.ainvoke([
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Startup Idea: {state['raw_idea']}\n\nSearch Results:\n{context}"},
        ])

        ratio = ltv_cac_ratio(raw.estimated_ltv_inr, raw.estimated_cac_inr)
        bm = breakeven_months(
            revenue_per_customer=raw.estimated_ltv_inr / 12,
            cac=raw.estimated_cac_inr,
        )
        fscore = score_financials(ratio, bm)

        result = FinancialOutput(
            revenue_model=raw.revenue_model,
            estimated_cac=_fmt_inr(raw.estimated_cac_inr),
            estimated_ltv=_fmt_inr(raw.estimated_ltv_inr),
            ltv_cac_ratio=ratio,
            breakeven_months=bm,
            financial_score=fscore,
            summary=raw.summary,
            revenue_projections=[
                RevenueProjection(year="Year 1", revenue_inr=raw.year1_revenue_inr, label=_fmt_inr(raw.year1_revenue_inr)),
                RevenueProjection(year="Year 2", revenue_inr=raw.year2_revenue_inr, label=_fmt_inr(raw.year2_revenue_inr)),
                RevenueProjection(year="Year 3", revenue_inr=raw.year3_revenue_inr, label=_fmt_inr(raw.year3_revenue_inr)),
            ],
        )

        events.append({"type": "agent_complete", "agent": "financial_feasibility", "data": result.model_dump()})
        return {"financial_feasibility": result, "stream_events": events, "agent_errors": errors}

    except Exception as e:
        errors.append(f"financial_feasibility: {str(e)}")
        events.append({"type": "error", "agent": "financial_feasibility", "message": str(e)})
        return {"financial_feasibility": None, "stream_events": events, "agent_errors": errors}
def _format_results(queries: list[str], results: list[list[dict]]) -> str:
    lines = []
    for query, hits in zip(queries, results):
        lines.append(f"\n### Query: {query}")
        if not hits:
            lines.append("No results found.")
        for h in hits:
            lines.append(f"- [{h['title']}]: {h['content'][:300]}")
    return "\n".join(lines)

