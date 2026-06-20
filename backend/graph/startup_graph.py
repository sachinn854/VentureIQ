import asyncio
from langgraph.graph import StateGraph, END, START

from backend.schemas.models import StartupState
from backend.agents.input_processor import run_input_processor
from backend.agents.market_research import run_market_research
from backend.agents.competitor_analysis import run_competitor_analysis
from backend.agents.financial_feasibility import run_financial_feasibility
from backend.agents.risk_assessment import run_risk_assessment
from backend.agents.synthesizer import run_synthesizer
from backend.agents.pivot_advisor import run_pivot_advisor


def _route_after_synthesizer(state: StartupState) -> str:
    report = state.get("final_report")
    if report and report.verdict == "NO-GO":
        return "pivot_advisor"
    return END


def _build_graph() -> StateGraph:
    g = StateGraph(StartupState)

    g.add_node("input_processor", run_input_processor)
    g.add_node("market_research", run_market_research)
    g.add_node("competitor_analysis", run_competitor_analysis)
    g.add_node("financial_feasibility", run_financial_feasibility)
    g.add_node("risk_assessment", run_risk_assessment)
    g.add_node("synthesizer", run_synthesizer)
    g.add_node("pivot_advisor", run_pivot_advisor)

    g.add_edge(START, "input_processor")

    # Parallel fan-out
    g.add_edge("input_processor", "market_research")
    g.add_edge("input_processor", "competitor_analysis")
    g.add_edge("input_processor", "financial_feasibility")
    g.add_edge("input_processor", "risk_assessment")

    # Fan-in → synthesizer
    g.add_edge("market_research", "synthesizer")
    g.add_edge("competitor_analysis", "synthesizer")
    g.add_edge("financial_feasibility", "synthesizer")
    g.add_edge("risk_assessment", "synthesizer")

    # Conditional: NO-GO → pivot_advisor, GO → END
    g.add_conditional_edges("synthesizer", _route_after_synthesizer, {"pivot_advisor": "pivot_advisor", END: END})
    g.add_edge("pivot_advisor", END)

    return g.compile()


startup_graph = _build_graph()


async def run_graph(raw_idea: str, event_queue: asyncio.Queue) -> None:
    initial_state: StartupState = {
        "raw_idea": raw_idea,
        "processed_idea": None,
        "market_research": None,
        "competitor_analysis": None,
        "financial_feasibility": None,
        "risk_assessment": None,
        "agent_errors": [],
        "final_report": None,
        "pivot_suggestions": None,
        "stream_events": [],
    }

    try:
        async for state_chunk in startup_graph.astream(initial_state, stream_mode="updates"):
            for node_name, updates in state_chunk.items():
                new_events: list[dict] = updates.get("stream_events", [])
                for event in new_events:
                    await event_queue.put(event)

    except Exception as e:
        await event_queue.put({"type": "error", "agent": "graph", "message": str(e)})

    finally:
        await event_queue.put({"type": "done"})
