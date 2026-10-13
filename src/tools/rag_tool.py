
from langchain_core.tools import tool

from src.retrieval.hybrid_search import hybrid_search


@tool
def rag_tool(query: str) -> str:
    """Retrieve relevant financial information from the knowledge base."""

    results = hybrid_search(query, k=3)

    if not results:
        return "No relevant financial information found."

    context = "\n\n".join(
        [document.page_content for document in results]
    )

    return context


if __name__ == "__main__":
    result = rag_tool.invoke({
        "query": "How does debt affect financial risk?"
    })

    print(result)
