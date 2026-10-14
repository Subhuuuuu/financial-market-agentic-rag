
import re
from functools import lru_cache

from rank_bm25 import BM25Okapi

from src.ingestion.loader import load_rag_documents
from src.retrieval.vector_store import load_vector_store

ASSET_ALIASES = {
    "s&p 500": "^GSPC",
    "s&p500": "^GSPC",
    "sp500": "^GSPC",
    "nifty 50": "^NSEI",
    "nifty50": "^NSEI",
}


@lru_cache(maxsize=1)
def load_bm25():
    """Build and cache BM25 over the complete RAG corpus."""
    documents = load_rag_documents()

    if not documents:
        raise ValueError("No documents available for keyword search.")

    tokenized_documents = [
        document.page_content.lower().split()
        for document in documents
    ]

    return documents, BM25Okapi(tokenized_documents)


def _document_key(document):
    """Return a stable key for document deduplication."""
    return (
        document.metadata.get("source", ""),
        document.metadata.get("start_index", -1),
        document.metadata.get("symbol", ""),
        document.metadata.get("period", ""),
        document.page_content.strip(),
    )


def extract_market_filters(query: str) -> dict:
    """Extract supported asset symbols and calendar years."""
    normalized_query = query.lower()
    filters = {}

    for alias, symbol in ASSET_ALIASES.items():
        if alias in normalized_query:
            filters["symbol"] = symbol
            break

    years = re.findall(r"\b(?:19|20)\d{2}\b", query)

    if years:
        filters["year"] = years[0]

    return filters


def hybrid_search(query: str, k: int = 3):
    """
    Search the financial RAG corpus using metadata filtering and RRF.

    Asset-and-year queries return matching monthly market summaries
    when available. Other queries use semantic and keyword retrieval.
    """
    if not query or not query.strip() or k <= 0:
        return []

    documents, bm25 = load_bm25()
    filters = extract_market_filters(query)

    # Prefer exact asset/year matches for historical market questions.
    if "symbol" in filters and "year" in filters:
        matching_documents = [
            document
            for document in documents
            if document.metadata.get("symbol") == filters["symbol"]
            and str(document.metadata.get("period", "")).startswith(
                filters["year"]
            )
        ]

        if matching_documents:
            return matching_documents[:k]

    # Standard hybrid retrieval for all other questions.
    vector_store = load_vector_store()
    candidate_k = min(max(k * 3, 6), len(documents))

    semantic_results = vector_store.similarity_search(
        query.strip(),
        k=candidate_k,
    )

    keyword_scores = bm25.get_scores(query.lower().split())

    keyword_indices = sorted(
        range(len(keyword_scores)),
        key=lambda index: keyword_scores[index],
        reverse=True,
    )[:candidate_k]

    keyword_results = [
        documents[index] for index in keyword_indices
    ]

    # Reciprocal Rank Fusion.
    fused_scores = {}
    documents_by_key = {}

    def add_ranked_results(results):
        for rank, document in enumerate(results, start=1):
            key = _document_key(document)
            documents_by_key[key] = document
            fused_scores[key] = (
                fused_scores.get(key, 0.0)
                + 1.0 / (60 + rank)
            )

    add_ranked_results(semantic_results)
    add_ranked_results(keyword_results)

    ranked_keys = sorted(
        fused_scores,
        key=lambda key: fused_scores[key],
        reverse=True,
    )

    results = []
    seen_text = set()

    for key in ranked_keys:
        document = documents_by_key[key]
        normalized_text = " ".join(
            document.page_content.lower().split()
        )

        if normalized_text in seen_text:
            continue

        seen_text.add(normalized_text)
        results.append(document)

        if len(results) >= k:
            break

    return results


if __name__ == "__main__":
    test_queries = [
        "How does high debt affect financial risk?",
        "What is diversification?",
        "How is the current ratio used to assess liquidity?",
        "Show S&P 500 performance in 2024",
        "What was the NIFTY 50 closing price in 2024?",
    ]

    for query in test_queries:
        print(f"\nQuestion: {query}")

        try:
            results = hybrid_search(query, k=12)

            if not results:
                print("No relevant documents found.")
                continue

            for result in results:
                print(
                    f"Source: "
                    f"{result.metadata.get('source', 'unknown')}"
                )
                print(
                    f"Symbol: "
                    f"{result.metadata.get('symbol', 'N/A')}"
                )
                print(
                    f"Period: "
                    f"{result.metadata.get('period', 'N/A')}"
                )
                print(result.page_content)
                print("-" * 40)

        except (FileNotFoundError, ValueError) as error:
            print(f"Search failed: {error}")
