
def evaluator(state: dict) -> dict:
    """Evaluate whether an agent answer has supporting context."""

    answer = state.get("agent_answer", "").strip()
    context = state.get("retrieved_context", "").strip()
    retry_count = state.get("retry_count", 0)

    insufficient_markers = (
        "could not find supporting information",
        "could not be completed because",
        "no relevant information was found",
        "insufficient supporting evidence",
        "couldn't find enough relevant information",
        "does not contain enough relevant detail",
        "could not find enough relevant information",
    )

    answer_lower = answer.lower()

    answer_is_insufficient = any(
        marker in answer_lower
        for marker in insufficient_markers
    )

    # Approve only non-empty answers with supporting context.
    if answer and context and not answer_is_insufficient:
        evaluation = {
            "verdict": "approved",
            "score": 4,
            "feedback": (
                "An answer was generated with retrieved context. "
                "This support check does not guarantee factual accuracy."
            ),
        }
        final_answer = answer

    # Allow one retry when evidence or the answer is insufficient.
    elif retry_count < 1:
        evaluation = {
            "verdict": "retry",
            "score": 1,
            "feedback": (
                "The answer or supporting retrieval context is "
                "missing or insufficient. Retry the workflow."
            ),
        }
        final_answer = ""

    # Stop retrying and return a safe fallback.
    else:
        evaluation = {
            "verdict": "insufficient_evidence",
            "score": 0,
            "feedback": (
                "A reliable answer could not be produced from "
                "the available evidence after retrying."
            ),
        }
        final_answer = (
            "Insufficient supporting evidence was retrieved to "
            "answer this question reliably. Please try a more "
            "specific question."
        )

    return {
        "evaluation": evaluation,
        "final_answer": final_answer,
        "retry_count": retry_count,
    }


if __name__ == "__main__":
    result = evaluator({
        "agent_answer": "High leverage can increase financial risk.",
        "retrieved_context": (
            "Higher leverage can increase financial risk."
        ),
        "retry_count": 0,
    })

    print(result)
