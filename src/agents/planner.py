
def planner(state):
    query = state["query"].lower()

    if any(word in query for word in ["portfolio", "allocation", "investment mix"]):
        intent = "portfolio"

    elif any(word in query for word in ["risk", "volatility", "exposure", "debt"]):
        intent = "risk"

    elif any(word in query for word in ["analyze", "analysis", "compare", "insight"]):
        intent = "analysis"

    else:
        intent = "retriever"

    return {"intent": intent}


if __name__ == "__main__":
    result = planner({
        "query": "Analyze portfolio risk"
    })

    print(result)
