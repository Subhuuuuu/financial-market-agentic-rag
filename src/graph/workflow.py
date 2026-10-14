
from langgraph.graph import END, START, StateGraph

from src.agents.analysis import analysis_agent
from src.agents.evaluator import evaluator
from src.agents.market_data_agent import market_data_agent
from src.agents.planner import planner
from src.agents.portfolio import portfolio_agent
from src.agents.retriever import retriever_agent
from src.agents.risk_assessment import risk_assessment_agent
from src.graph.state import AgentState


def route_after_planner(state: AgentState) -> str:
    """Route market calculations to tools and other queries to RAG."""
    if state.get("intent") == "market_data":
        return "market_data_agent"

    return "retriever_agent"


def route_after_retriever(state: AgentState) -> str:
    """Route retrieved evidence to the appropriate specialist."""
    intent = state.get("intent", "retriever")

    if intent == "risk":
        return "risk_assessment_agent"

    if intent == "analysis":
        return "analysis_agent"

    if intent == "portfolio":
        return "portfolio_agent"

    return "evaluator"


def route_after_evaluator(state: AgentState) -> str:
    """Retry once when the evaluator requests more evidence."""
    evaluation = state.get("evaluation", {})
    retry_count = state.get("retry_count", 0)

    if (
        evaluation.get("verdict") == "retry"
        and retry_count < 1
    ):
        return "retry_node"

    return END


def retry_node(state: AgentState) -> dict:
    """Clear previous outputs before retrying the workflow."""
    return {
        "retry_count": state.get("retry_count", 0) + 1,
        "agent_answer": "",
        "retrieved_context": "",
        "final_answer": "",
        "evaluation": {},
        "market_results": {},
    }


graph = StateGraph(AgentState)

# Register nodes.
graph.add_node("planner", planner)
graph.add_node("retriever_agent", retriever_agent)
graph.add_node("market_data_agent", market_data_agent)
graph.add_node("analysis_agent", analysis_agent)
graph.add_node("portfolio_agent", portfolio_agent)
graph.add_node("risk_assessment_agent", risk_assessment_agent)
graph.add_node("evaluator", evaluator)
graph.add_node("retry_node", retry_node)

# Entry point.
graph.add_edge(START, "planner")

# Planner routing.
graph.add_conditional_edges(
    "planner",
    route_after_planner,
    {
        "market_data_agent": "market_data_agent",
        "retriever_agent": "retriever_agent",
    },
)

# Retrieve evidence before specialist analysis.
graph.add_conditional_edges(
    "retriever_agent",
    route_after_retriever,
    {
        "risk_assessment_agent": "risk_assessment_agent",
        "analysis_agent": "analysis_agent",
        "portfolio_agent": "portfolio_agent",
        "evaluator": "evaluator",
    },
)

# All specialist agents proceed to evaluation.
graph.add_edge("market_data_agent", "evaluator")
graph.add_edge("analysis_agent", "evaluator")
graph.add_edge("portfolio_agent", "evaluator")
graph.add_edge("risk_assessment_agent", "evaluator")

# Evaluation and optional retry.
graph.add_conditional_edges(
    "evaluator",
    route_after_evaluator,
    {
        "retry_node": "retry_node",
        END: END,
    },
)

graph.add_edge("retry_node", "planner")

app = graph.compile()


if __name__ == "__main__":
    questions = [
        "Show historical prices of the S&P 500 in 2024",
        (
            "Compare S&P 500 and NIFTY 50 returns from "
            "2024-01-01 to 2024-12-31"
        ),
        "How can high debt increase financial risk?",
        "What is diversification?",
        "Analyze S&P 500 performance in 2024",
        "Compare portfolio allocation",
    ]

    for question in questions:
        print("\n" + "=" * 70)
        print(f"Question: {question}")

        result = app.invoke(
            {
                "query": question,
                "retry_count": 0,
            }
        )

        print("\nFinal Answer:")
        print(
            result.get("final_answer")
            or "No answer generated."
        )

        print("\nIntent:")
        print(result.get("intent", "unknown"))

        print("\nEvaluation:")
        print(result.get("evaluation", {}))
