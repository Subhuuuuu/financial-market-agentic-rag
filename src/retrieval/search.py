
from langchain_core.documents import Document

from src.config import TOP_K
from src.retrieval.vector_store import load_vector_store


def semantic_search(
    query: str,
    k: int = TOP_K,
) -> list[Document]:
    """Retrieve the most relevant financial knowledge-base chunks."""
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if k <= 0:
        raise ValueError("k must be greater than zero.")

    vector_store = load_vector_store()

    return vector_store.similarity_search(
        query=query.strip(),
        k=k,
    )


def format_search_results(documents: list[Document]) -> str:
    """Format retrieved chunks with source information."""
    if not documents:
        return "No relevant financial information was found."

    results = []

    for index, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "Unknown source")
        start_index = document.metadata.get("start_index", "Unknown")

        results.append(
            f"[Result {index}]\n"
            f"Source: {source}\n"
            f"Start index: {start_index}\n"
            f"Content:\n{document.page_content}"
        )

    return "\n\n".join(results)
