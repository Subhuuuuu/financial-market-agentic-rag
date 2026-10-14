
from src.retrieval.hybrid_search import hybrid_search


def retriever_agent(state):
    query = state.get("query", "").strip()

    if not query:
        message = "Please enter a financial question."
        return {
            "retrieved_context": "",
            "agent_answer": message,
        }

    results = hybrid_search(query, k=2)

    if not results:
        message = (
            "No relevant information was found in the "
            "financial knowledge base."
        )
        return {
            "retrieved_context": "",
            "agent_answer": message,
        }

    context_parts = []

    for index, document in enumerate(results, start=1):
        source = document.metadata.get(
            "source",
            "financial knowledge base",
        )
        context_parts.append(
            f"Source: {source}\n{document.page_content.strip()}"
        )

    context = "\n\n---\n\n".join(context_parts)

    return {
        "retrieved_context": context,
        "agent_answer": context,
    }


if __name__ == "__main__":
    questions = [
        "What is diversification?",
        "How does high debt affect financial risk?",
        "How is liquidity measured?",
    ]

    for question in questions:
        result = retriever_agent({"query": question})
        print(f"\nQuestion: {question}")
        print(result["agent_answer"])
        print("=" * 60)
