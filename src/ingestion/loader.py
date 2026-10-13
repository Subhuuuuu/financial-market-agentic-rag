
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "financial_faq.md"


def load_financial_documents() -> list[Document]:
    """Load the financial knowledge-base Markdown file."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Knowledge-base file not found: {DATA_PATH}"
        )

    text = DATA_PATH.read_text(encoding="utf-8")

    if not text.strip():
        raise ValueError("The financial knowledge base is empty.")

    return [
        Document(
            page_content=text,
            metadata={
                "source": DATA_PATH.name,
                "document_type": "educational_financial_knowledge",
            },
        )
    ]


def split_financial_documents(
    documents: list[Document],
    chunk_size: int = 500,
    chunk_overlap: int = 80,
) -> list[Document]:
    """Split documents into overlapping chunks for retrieval."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be non-negative and smaller than chunk_size."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,
    )

    return splitter.split_documents(documents)
