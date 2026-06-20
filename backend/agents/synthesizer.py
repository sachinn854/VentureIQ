import logging
from backend.llm_factory import get_llm
from backend.schemas.models import (
    StartupState, FinalReport,
    MarketOutput, CompetitorOutput, FinancialOutput, RiskOutput,
)
logger = logging.getLogger(__name__)

_llm = get_llm(max_tokens=4096).with_structured_output(FinalReport)

_SYSTEM = """You are a senior startup investment analyst delivering a final verdict.
You have received reports from specialist agents. Some agents may have failed â€” use what is available.

CRITICAL RULES â€” you MUST follow these exactly:
1. verdict: "GO" if overall_score >= 6.0, else "NO-GO". Never return empty string.
2. confidence: integer 0-100. Never 0 unless you are completely uncertain.
3. overall_score: weighted average of available scores (market 30%, competition 25%, financial 25%, risk 20%). If an agent failed, use 5.0 as default for that dimension. Never return 0.0 unless the idea is truly terrible.
4. score_breakdown: dict with keys "market", "competition", "financial", "risk" â€” all must be floats 0-10.
5. top_3_strengths: list of EXACTLY 3 non-empty strings describing real strengths of this idea.
6. top_3_risks: list of EXACTLY 3 non-empty strings describing real risks.
7. recommended_next_steps: list of EXACTLY 3 non-empty, concrete action items.
8. executive_summary: 3-4 sentences. Must not be empty.

If agent data is missing, use your own knowledge about the startup idea to fill in the analysis.
Be direct and honest. Do not return zeros or empty strings â€” that is a failure."""
async def run_synthesizer(state: StartupState) -> dict:
    new_events = [{"type": "agent_start", "agent": "synthesizer"}]

    try:
        context = _build_context(state)
        logger.info(f"synthesizer context length: {len(context)} chars")

        result: FinalReport = await _llm.ainvoke([
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": context},
        ])

        logger.info(f"synthesizer result â€” verdict: {result.verdict}, score: {result.overall_score}, breakdown: {result.score_breakdown}")

        new_events.append({"type": "agent_complete", "agent": "synthesizer", "data": result.model_dump()})
        new_events.append({"type": "final_report", "data": result.model_dump()})
        return {"final_report": result, "stream_events": new_events, "agent_errors": []}

    except Exception as e:
        logger.error(f"synthesizer FAILED: {type(e).__name__}: {e}", exc_info=True)
        new_events.append({"type": "error", "agent": "synthesizer", "message": str(e)})
        return {"final_report": None, "stream_events": new_events, "agent_errors": [f"synthesizer: {e}"]}
def _build_context(state: StartupState) -> str:
    parts = [f"## Startup Idea\n{state['raw_idea']}\n"]

    available_agents = []

    market: MarketOutput = state.get("market_research")
    if market:
        available_agents.append("market_research")
        parts.append(
            f"## Market Research Agent (Score: {market.market_score}/10)\n"
            f"Summary: {market.summary}\n"
            f"TAM: {market.tam} | SAM: {market.sam} | SOM Year1: {market.som_year1}\n"
            f"Growth Rate: {market.growth_rate}\n"
            f"Demand Signals: {', '.join(market.demand_signals)}"
        )

    competitor: CompetitorOutput = state.get("competitor_analysis")
    if competitor:
        available_agents.append("competitor_analysis")
        comp_names = [c.name for c in competitor.competitors]
        parts.append(
            f"## Competitor Analysis Agent (Score: {competitor.competition_score}/10)\n"
            f"Summary: {competitor.summary}\n"
            f"Top Competitors: {', '.join(comp_names)}\n"
            f"Market Gap: {competitor.market_gap}\n"
            f"Differentiation: {competitor.differentiation_opportunity}"
        )

    financial: FinancialOutput = state.get("financial_feasibility")
    if financial:
        available_agents.append("financial_feasibility")
        parts.append(
            f"## Financial Feasibility Agent (Score: {financial.financial_score}/10)\n"
            f"Summary: {financial.summary}\n"
            f"Revenue Model: {financial.revenue_model}\n"
            f"CAC: {financial.estimated_cac} | LTV: {financial.estimated_ltv}\n"
            f"LTV:CAC Ratio: {financial.ltv_cac_ratio} | Break-even: {financial.breakeven_months} months"
        )

    risk: RiskOutput = state.get("risk_assessment")
    if risk:
        available_agents.append("risk_assessment")
        parts.append(
            f"## Risk Assessment Agent (Score: {risk.risk_score}/10)\n"
            f"Summary: {risk.summary}\n"
            f"Market Risk: {risk.market_risk.level} â€” {risk.market_risk.description}\n"
            f"Regulatory Risk: {risk.regulatory_risk.level} â€” {risk.regulatory_risk.description}\n"
            f"Technical Risk: {risk.technical_risk.level} â€” {risk.technical_risk.description}\n"
            f"Competitive Risk: {risk.competitive_risk.level} â€” {risk.competitive_risk.description}"
        )

    if state.get("agent_errors"):
        failed = [e.split(":")[0] for e in state["agent_errors"]]
        parts.append(f"## Note: These agents failed and their data is unavailable: {', '.join(failed)}. Use your own knowledge for those dimensions.")

    parts.append(f"\n## Available agent data: {', '.join(available_agents) if available_agents else 'none â€” use your own knowledge entirely'}")

    return "\n\n".join(parts)

