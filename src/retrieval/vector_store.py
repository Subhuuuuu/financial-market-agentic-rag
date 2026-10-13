
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import EMBEDDING_MODEL
from src.ingestion.loader import (
    load_financial_documents,
    split_financial_documents,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = PROJECT_ROOT / "data" / "index"


def create_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def build_vector_store() -> FAISS:
    documents = load_financial_documents()
    chunks = split_financial_documents(documents)

    embeddings = create_embeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)

    INDEX_PATH.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(INDEX_PATH))

    return vector_store


def load_vector_store() -> FAISS:
    if not (INDEX_PATH / "index.faiss").exists():
        raise FileNotFoundError(
            "FAISS index not found. Run build_vector_store() first."
        )

    embeddings = create_embeddings()

    return FAISS.load_local(
        str(INDEX_PATH),
        embeddings,
        allow_dangerous_deserialization=True,
    )


if __name__ == "__main__":
    vector_store = load_vector_store()
    print("FAISS index loaded successfully!")
    print("Total vectors:", vector_store.index.ntotal)
