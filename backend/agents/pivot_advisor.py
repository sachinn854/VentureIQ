import logging
from backend.llm_factory import get_llm
from backend.schemas.models import StartupState, PivotOutput, FinalReport
logger = logging.getLogger(__name__)

_llm = get_llm(max_tokens=4096).with_structured_output(PivotOutput)

_SYSTEM = """You are a startup pivot strategist. The startup idea has received a NO-GO verdict.
Your job is to suggest 3 concrete pivot strategies that could make this idea viable.

Each pivot must have:
- title: short name of the pivot (e.g. "B2B Enterprise Pivot", "Niche Down to Tier-2 Cities")
- description: 2-3 sentences explaining the pivot strategy
- key_change: the single most important thing that changes (target customer / business model / geography / product scope)
- potential: "High" / "Medium" / "Low" â€” how promising this pivot is

reasoning: 1-2 sentences explaining WHY the original idea needs pivoting.

Be specific to the Indian market. Suggest pivots that address the actual weaknesses identified."""
async def run_pivot_advisor(state: StartupState) -> dict:
    new_events = [{"type": "agent_start", "agent": "pivot_advisor"}]

    try:
        report: FinalReport = state.get("final_report")
        context = _build_context(state, report)

        result: PivotOutput = await _llm.ainvoke([
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": context},
        ])

        new_events.append({"type": "agent_complete", "agent": "pivot_advisor", "data": result.model_dump()})
        new_events.append({"type": "pivot_suggestions", "data": result.model_dump()})
        return {"pivot_suggestions": result, "stream_events": new_events, "agent_errors": []}

    except Exception as e:
        logger.error(f"pivot_advisor FAILED: {type(e).__name__}: {e}", exc_info=True)
        new_events.append({"type": "error", "agent": "pivot_advisor", "message": str(e)})
        return {"pivot_suggestions": None, "stream_events": new_events, "agent_errors": [f"pivot_advisor: {e}"]}
def _build_context(state: StartupState, report: FinalReport) -> str:
    parts = [f"## Original Idea\n{state['raw_idea']}\n"]

    if report:
        parts.append(f"## Verdict: {report.verdict} (Score: {report.overall_score}/10)")
        parts.append("## Top Risks\n" + "\n".join(f"- {r}" for r in report.top_3_risks))
        parts.append(f"## Executive Summary\n{report.executive_summary}")

    market = state.get("market_research")
    if market:
        parts.append(f"## Market Issue\n{market.summary} (Score: {market.market_score}/10)")

    competitor = state.get("competitor_analysis")
    if competitor:
        parts.append(f"## Competition Issue\n{competitor.summary} (Score: {competitor.competition_score}/10)")

    financial = state.get("financial_feasibility")
    if financial:
        parts.append(f"## Financial Issue\n{financial.summary} (Score: {financial.financial_score}/10)")

    return "\n\n".join(parts)

