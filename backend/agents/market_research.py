import logging
from backend.llm_factory import get_llm
from backend.schemas.models import StartupState, MarketOutput, ProcessedIdea
from backend.tools.search_tool import search_many
logger = logging.getLogger(__name__)

_llm = get_llm(max_tokens=4096).with_structured_output(MarketOutput)

_SYSTEM = """You are a market research analyst. Be concise â€” short sentences only.
Estimate TAM/SAM/SOM as single values (e.g. "â‚¹12,000 Cr"), growth_rate as a short phrase (e.g. "28% CAGR").
demand_signals: exactly 3 items, max 10 words each. summary: 2 sentences max.
market_score: 0â€“10. Never return 0 unless market truly doesn't exist."""
async def run_market_research(state: StartupState) -> dict:
    new_events = [{"type": "agent_start", "agent": "market_research"}]

    try:
        idea: ProcessedIdea = state.get("processed_idea")
        industry = idea.industry if idea else "technology"
        problem  = idea.problem_solved if idea else state["raw_idea"]

        queries = [
            f"{industry} market size TAM India 2025 2026",
            f"{industry} industry growth rate trends 2025 2026",
            f"customer demand {problem} India startups",
        ]
        search_results = await search_many(queries, max_results=4)
        context = _format_results(queries, search_results)

        result: MarketOutput = await _llm.ainvoke([
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Startup Idea: {state['raw_idea']}\n\nSearch Results:\n{context}"},
        ])

        new_events.append({"type": "agent_complete", "agent": "market_research", "data": result.model_dump()})
        return {"market_research": result, "stream_events": new_events, "agent_errors": []}

    except Exception as e:
        logger.error(f"market_research FAILED: {type(e).__name__}: {e}", exc_info=True)
        new_events.append({"type": "error", "agent": "market_research", "message": str(e)})
        return {"market_research": None, "stream_events": new_events, "agent_errors": [f"market_research: {e}"]}
def _format_results(queries: list[str], results: list[list[dict]]) -> str:
    lines = []
    for query, hits in zip(queries, results):
        lines.append(f"\n### Query: {query}")
        if not hits:
            lines.append("No results found.")
        for h in hits:
            lines.append(f"- [{h['title']}]: {h['content'][:300]}")
    return "\n".join(lines)

