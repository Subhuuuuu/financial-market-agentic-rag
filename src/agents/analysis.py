
import re


def _relevant_sentences(
    context: str,
    query: str,
    limit: int = 4,
) -> list[str]:
    """Return the most relevant sentences using keyword overlap."""

    if not context or not query:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", context.strip())
    query_terms = set(
        re.findall(r"\b[a-z]{3,}\b", query.lower())
    )

    scored_sentences = []
    seen = set()

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        # Ignore source labels and repeated section headings.
        if sentence.lower().startswith("source:"):
            continue

        if re.fullmatch(
            r"(?:\d+\.\s*)?source limitations",
            sentence,
            re.IGNORECASE,
        ):
            continue

        normalized = re.sub(r"\s+", " ", sentence).lower()

        if normalized in seen:
            continue

        seen.add(normalized)

        sentence_terms = set(
            re.findall(r"\b[a-z]{3,}\b", sentence.lower())
        )

        score = len(query_terms & sentence_terms)

        if score > 0:
            scored_sentences.append((score, sentence))

    scored_sentences.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        sentence
        for _, sentence in scored_sentences[:limit]
    ]


def analysis_agent(state: dict) -> dict:
    """Generate a concise answer from retrieved context."""

    query = state.get("query", "").strip()
    context = state.get("retrieved_context", "").strip()

    if not context:
        return {
            "agent_answer": (
                "Could not find supporting information "
                "in the available knowledge base."
            )
        }

    relevant_sentences = _relevant_sentences(
        context=context,
        query=query,
        limit=4,
    )

    if not relevant_sentences:
        return {
            "agent_answer": (
                "Could not find supporting information "
                "relevant to this question."
            )
        }

    answer = " ".join(relevant_sentences)

    if len(answer) > 1200:
        answer = answer[:1200].rsplit(" ", 1)[0] + "..."

    return {"agent_answer": answer}


# Preserve compatibility with modules using the older function name.
run_analysis = analysis_agent


if __name__ == "__main__":
    test_state = {
        "query": (
            "What is diversification, and how does it "
            "reduce investment risk?"
        ),
        "retrieved_context": (
            "Diversification spreads investments across different assets. "
            "It can reduce concentration risk because different investments "
            "may perform differently. Diversification cannot eliminate "
            "all market risk or guarantee returns."
        ),
    }

    print(analysis_agent(test_state))
