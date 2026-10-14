
from src.agents.analysis import _relevant_sentences


def risk_assessment_agent(state):
    query = state.get("query", "").strip()
    context = state.get("retrieved_context", "").strip()

    if not context:
        return {
            "agent_answer": (
                "Risk assessment could not be completed because "
                "the RAG system did not retrieve supporting evidence."
            )
        }

    findings = _relevant_sentences(query, context, limit=5)

    if not findings:
        findings = [
            line.strip()
            for line in context.splitlines()
            if line.strip() and not line.strip().startswith("Source:")
        ][:3]

    answer = "Risk Assessment Based on Retrieved Evidence\n\n"
    answer += "\n".join(f"- {finding}" for finding in findings)
    answer += (
        "\n\nLimitations: This assessment reflects the retrieved "
        "dataset and knowledge base. It is not a personalized "
        "investment recommendation and does not use live market data."
    )

    return {"agent_answer": answer}


if __name__ == "__main__":
    result = risk_assessment_agent({
        "query": "How can high debt increase financial risk?",
        "retrieved_context": (
            "Higher leverage can increase financial risk, "
            "particularly when earnings or cash flows decline."
        ),
    })
    print(result["agent_answer"])
