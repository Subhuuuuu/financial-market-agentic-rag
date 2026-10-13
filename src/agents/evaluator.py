
def evaluator(state):
    answer = state.get("agent_answer", "")
    context = state.get("retrieved_context", "")
    retry_count = state.get("retry_count", 0)

    if answer.strip() and (context.strip() or retry_count > 0):
        evaluation = {
            "verdict": "approved",
            "score": 5,
            "feedback": "Response contains information."
        }
        final_answer = answer

    elif retry_count < 1:
        evaluation = {
            "verdict": "retry",
            "score": 2,
            "feedback": "More information is required."
        }
        final_answer = ""

    else:
        evaluation = {
            "verdict": "approved",
            "score": 1,
            "feedback": "Insufficient information available."
        }
        final_answer = (
            "Insufficient financial information to provide "
            "a reliable answer."
        )

    return {
        "evaluation": evaluation,
        "final_answer": final_answer,
        "retry_count": retry_count
    }


if __name__ == "__main__":
    result = evaluator({
        "agent_answer": "High debt may increase financial risk.",
        "retrieved_context": "Debt and leverage information.",
        "retry_count": 0
    })

    print(result)
