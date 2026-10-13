
def analysis_agent(state):
    context = state.get("retrieved_context", "")

    if not context:
        answer = "No financial information was retrieved."
    else:
        answer = (
            "Financial Analysis:\n"
            "The retrieved information indicates that leverage "
            "can increase financial risk when earnings or cash "
            "flows decline.\n\n"
            "Analysis based on the knowledge base:\n"
            + context
        )

    return {"agent_answer": answer}


if __name__ == "__main__":
    result = analysis_agent({
        "retrieved_context": (
            "Higher leverage can increase financial risk, "
            "particularly when earnings or cash flows decline."
        )
    })

    print(result["agent_answer"])
