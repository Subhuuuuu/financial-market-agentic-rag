
from langgraph.graph import END, START, StateGraph

from src.agents.analysis import analysis_agent
from src.agents.evaluator import evaluator
from src.agents.planner import planner
from src.agents.portfolio import portfolio_agent
from src.agents.retriever import retriever_agent
from src.agents.risk_assessment import risk_assessment_agent
from src.graph.state import AgentState


def route_after_planner(state):
    intent = state.get("intent", "retriever")

    if intent == "portfolio":
        return "portfolio_agent"
    elif intent == "risk" or intent == "analysis":
        return "retriever_agent"

    return "retriever_agent"


def select_specialist(state):
    intent = state.get("intent", "retriever")

    if intent == "portfolio":
        return "portfolio_agent"
    elif intent == "risk":
        return "risk_assessment_agent"
    elif intent == "analysis":
        return "analysis_agent"

    return "retriever_agent"


def route_after_retriever(state):
    intent = state.get("intent", "retriever")

    if intent == "risk":
        return "risk_assessment_agent"
    elif intent == "analysis":
        return "analysis_agent"

    return "evaluator"


graph = StateGraph(AgentState)

graph.add_node("planner", planner)
graph.add_node("retriever_agent", retriever_agent)
graph.add_node("analysis_agent", analysis_agent)
graph.add_node("portfolio_agent", portfolio_agent)
graph.add_node("risk_assessment_agent", risk_assessment_agent)
graph.add_node("evaluator", evaluator)

graph.add_edge(START, "planner")

graph.add_conditional_edges(
    "planner",
    route_after_planner,
    {
        "retriever_agent": "retriever_agent",
        "portfolio_agent": "portfolio_agent",
    }
)

graph.add_conditional_edges(
    "retriever_agent",
    route_after_retriever,
    {
        "risk_assessment_agent": "risk_assessment_agent",
        "analysis_agent": "analysis_agent",
        "evaluator": "evaluator",
    }
)

graph.add_edge("analysis_agent", "evaluator")
graph.add_edge("portfolio_agent", "evaluator")
graph.add_edge("risk_assessment_agent", "evaluator")

def route_after_evaluator(state):
    evaluation = state.get("evaluation", {})
    retry_count = state.get("retry_count", 0)

    if evaluation.get("verdict") == "retry" and retry_count < 1:
        return "planner"

    return END


def retry_node(state):
    return {
        "retry_count": state.get("retry_count", 0) + 1
    }


graph.add_node("retry_node", retry_node)

graph.add_conditional_edges(
    "evaluator",
    route_after_evaluator,
    {
        "planner": "retry_node",
        END: END,
    },
)

graph.add_edge("retry_node", "planner")

app = graph.compile()


if __name__ == "__main__":
    result = app.invoke({
        "query": "How can high debt increase financial risk?",
        "retry_count": 0,
    })

    print("Final Answer:")
    print(result.get("final_answer", "No answer generated."))

    print("\nEvaluation:")
    print(result.get("evaluation", {}))
