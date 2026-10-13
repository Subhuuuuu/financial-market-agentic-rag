
from src.retrieval.hybrid_search import hybrid_search


def retriever_agent(state):
    query = state["query"]

    results = hybrid_search(query, k=3)

    context = "\n\n".join(
        [document.page_content for document in results]
    )

    return {
        "retrieved_context": context,
        "agent_answer": context
    }


if __name__ == "__main__":
    result = retriever_agent({
        "query": "How does high debt affect financial risk?"
    })

    print(result["retrieved_context"])
