
def portfolio_agent(state):
    query = state.get("query", "").lower()

    if "low" in query or "conservative" in query:
        allocation = {
            "Bonds": 60,
            "Equity": 25,
            "Cash": 15
        }

    elif "high" in query or "aggressive" in query:
        allocation = {
            "Equity": 70,
            "Bonds": 20,
            "Cash": 10
        }

    else:
        allocation = {
            "Equity": 50,
            "Bonds": 35,
            "Cash": 15
        }

    answer = "Illustrative Portfolio Allocation:\n"

    for asset, percentage in allocation.items():
        answer += f"{asset}: {percentage}%\n"

    answer += (
        "\nThis is an educational example, not personalized "
        "investment advice. Actual allocations depend on "
        "individual circumstances and market conditions."
    )

    return {"agent_answer": answer}


if __name__ == "__main__":
    result = portfolio_agent({
        "query": "Suggest a conservative portfolio"
    })

    print(result["agent_answer"])
