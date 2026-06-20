import logging
from backend.llm_factory import get_llm
from backend.schemas.models import StartupState, CompetitorOutput, CompetitorInfo, ProcessedIdea
from backend.tools.search_tool import search_many
logger = logging.getLogger(__name__)

_llm = get_llm(max_tokens=4096).with_structured_output(CompetitorOutput)

_SYSTEM = """You are a competitive intelligence analyst. Be concise â€” short sentences only.
Identify exactly 3 competitors for the given startup idea.
Each competitor: name, exactly 2 strengths (max 8 words each), exactly 2 weaknesses (max 8 words each), funding.
market_gap: 1 sentence. differentiation_opportunity: 1 sentence. summary: 2 sentences max.
competition_score: 0â€“10 where 10 = almost no competition. Must be 0â€“10, never negative."""
async def run_competitor_analysis(state: StartupState) -> dict:
    new_events = [{"type": "agent_start", "agent": "competitor_analysis"}]

    try:
        idea: ProcessedIdea = state.get("processed_idea")
        industry = idea.industry if idea else "technology"
        core     = idea.core_idea if idea else state["raw_idea"]

        queries = [
            f"top competitors {core} startups India 2025",
            f"best {industry} startups India funding valuation 2025",
            f"{core} alternatives existing solutions market",
        ]
        search_results = await search_many(queries, max_results=4)
        context = _format_results(queries, search_results)

        result: CompetitorOutput = await _llm.ainvoke([
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Startup Idea: {state['raw_idea']}\n\nSearch Results:\n{context}"},
        ])

        new_events.append({"type": "agent_complete", "agent": "competitor_analysis", "data": result.model_dump()})
        return {"competitor_analysis": result, "stream_events": new_events, "agent_errors": []}

    except Exception as e:
        logger.error(f"competitor_analysis FAILED: {type(e).__name__}: {e}", exc_info=True)
        new_events.append({"type": "error", "agent": "competitor_analysis", "message": str(e)})
        return {"competitor_analysis": None, "stream_events": new_events, "agent_errors": [f"competitor_analysis: {e}"]}
def _format_results(queries: list[str], results: list[list[dict]]) -> str:
    lines = []
    for query, hits in zip(queries, results):
        lines.append(f"\n### Query: {query}")
        if not hits:
            lines.append("No results found.")
        for h in hits:
            lines.append(f"- [{h['title']}]: {h['content'][:300]}")
    return "\n".join(lines)

