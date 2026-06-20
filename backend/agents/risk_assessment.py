import logging
from backend.llm_factory import get_llm
from backend.schemas.models import StartupState, RiskOutput, RiskItem, ProcessedIdea
from backend.tools.search_tool import search_many
logger = logging.getLogger(__name__)

_llm = get_llm(max_tokens=4096).with_structured_output(RiskOutput)

_SYSTEM = """You are a startup risk analyst.
Assess the following 4 risk dimensions for the given startup idea:
- market_risk: Is there enough demand? Is the timing right?
- regulatory_risk: Are there legal/compliance/government hurdles in India?
- technical_risk: How hard is the technology to build or maintain?
- competitive_risk: Can well-funded incumbents easily copy or crush this?

Each risk must have: level (Low/Medium/High), description (1-2 sentences), mitigation (1 sentence on how to reduce it).
risk_score: 0â€“10 where 10 = very low overall risk, 0 = extremely risky. Must be 0â€“10, never negative.
summary: 2â€“3 sentence overall risk overview."""
async def run_risk_assessment(state: StartupState) -> dict:
    new_events = [{"type": "agent_start", "agent": "risk_assessment"}]

    try:
        idea: ProcessedIdea = state.get("processed_idea")
        industry = idea.industry if idea else "technology"

        queries = [
            f"regulatory compliance laws {industry} startup India 2025",
            f"risks challenges {industry} startup failure reasons India",
        ]
        search_results = await search_many(queries, max_results=4)
        context = _format_results(queries, search_results)

        result: RiskOutput = await _llm.ainvoke([
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Startup Idea: {state['raw_idea']}\n\nSearch Results:\n{context}"},
        ])

        new_events.append({"type": "agent_complete", "agent": "risk_assessment", "data": result.model_dump()})
        return {"risk_assessment": result, "stream_events": new_events, "agent_errors": []}

    except Exception as e:
        logger.error(f"risk_assessment FAILED: {type(e).__name__}: {e}", exc_info=True)
        new_events.append({"type": "error", "agent": "risk_assessment", "message": str(e)})
        return {"risk_assessment": None, "stream_events": new_events, "agent_errors": [f"risk_assessment: {e}"]}
def _format_results(queries: list[str], results: list[list[dict]]) -> str:
    lines = []
    for query, hits in zip(queries, results):
        lines.append(f"\n### Query: {query}")
        if not hits:
            lines.append("No results found.")
        for h in hits:
            lines.append(f"- [{h['title']}]: {h['content'][:300]}")
    return "\n".join(lines)

