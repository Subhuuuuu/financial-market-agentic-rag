
from rank_bm25 import BM25Okapi

from src.ingestion.loader import (
    load_financial_documents,
    split_financial_documents,
)
from src.retrieval.vector_store import load_vector_store

documents = load_financial_documents()
chunks = split_financial_documents(documents)

tokenized_docs = [
    doc.page_content.lower().split()
    for doc in chunks
]

bm25 = BM25Okapi(tokenized_docs)


def hybrid_search(query, k=3):
    vector_store = load_vector_store()

    semantic_results = vector_store.similarity_search(query, k=k)

    scores = bm25.get_scores(query.lower().split())
    keyword_results = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )[:k]

    results = []

    for doc in semantic_results:
        if doc not in results:
            results.append(doc)

    for i in keyword_results:
        if chunks[i] not in results:
            results.append(chunks[i])

    return results[:k]


if __name__ == "__main__":
    query = "How does high debt affect financial risk?"

    results = hybrid_search(query)

    for result in results:
        print(result.page_content)
        print("Source:", result.metadata["source"])
        print("-" * 40)
