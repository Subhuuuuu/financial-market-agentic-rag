
def risk_assessment_agent(state):
    query = state.get("query", "").lower()
    context = state.get("retrieved_context", "").lower()

    risks = []

    if "debt" in query or "leverage" in context:
        risks.append("High debt may increase financial risk.")

    if "volatility" in query or "market risk" in context:
        risks.append("Market volatility may cause investment losses.")

    if "concentration" in context or "concentration" in query:
        risks.append("Concentration in a few assets increases exposure.")

    if not risks:
        risks.append(
            "Insufficient information for a detailed risk assessment."
        )

    answer = "Risk Assessment:\n"

    for risk in risks:
        answer += "- " + risk + "\n"

    answer += (
        "\nThis assessment is based on the available text. "
        "It does not use live market data."
    )

    return {"agent_answer": answer}


if __name__ == "__main__":
    result = risk_assessment_agent({
        "query": "Assess debt and market risk",
        "retrieved_context": (
            "Leverage can increase financial risk. "
            "Market risk refers to losses caused by market movements."
        )
    })

    print(result["agent_answer"])
