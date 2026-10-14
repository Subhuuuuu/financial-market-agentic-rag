
from pathlib import Path

import pandas as pd
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FAQ_PATH = PROJECT_ROOT / "data" / "financial_faq.md"
MARKET_DATA_PATH = (
    PROJECT_ROOT / "data" / "global_financial_markets_2000_Now.csv"
)


def load_financial_documents() -> list[Document]:
    """Load the educational financial Markdown knowledge base."""
    if not FAQ_PATH.exists():
        raise FileNotFoundError(
            f"Knowledge-base file not found: {FAQ_PATH}"
        )

    text = FAQ_PATH.read_text(encoding="utf-8")

    if not text.strip():
        raise ValueError("The financial knowledge base is empty.")

    return [
        Document(
            page_content=text,
            metadata={
                "source": FAQ_PATH.name,
                "document_type": "educational_financial_knowledge",
            },
        )
    ]


def split_financial_documents(
    documents: list[Document],
    chunk_size: int = 500,
    chunk_overlap: int = 80,
) -> list[Document]:
    """Split text documents into overlapping retrieval chunks."""
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


def load_market_dataframe() -> pd.DataFrame:
    """Load and validate historical market data as a DataFrame."""
    if not MARKET_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Market dataset not found: {MARKET_DATA_PATH}"
        )

    df = pd.read_csv(MARKET_DATA_PATH)

    required_columns = {
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "symbol",
        "asset_name",
        "asset_type",
        "region",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Market dataset is missing columns: {sorted(missing)}"
        )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for column in ["open", "high", "low", "close", "volume"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["symbol"] = df["symbol"].astype("string").str.strip()
    df["asset_name"] = df["asset_name"].astype("string").str.strip()

    df = df.dropna(
        subset=["date", "symbol", "close"]
    ).copy()

    df = df.drop_duplicates(
        subset=["date", "symbol"]
    )

    return df.sort_values(
        ["symbol", "date"]
    ).reset_index(drop=True)


def market_dataframe_to_documents(
    df: pd.DataFrame,
    frequency: str = "monthly",
) -> list[Document]:
    """
    Optionally convert market records into summary documents
    for semantic search. This is separate from numerical analysis.
    """
    if frequency not in {"daily", "monthly", "yearly"}:
        raise ValueError(
            "frequency must be daily, monthly, or yearly."
        )

    if df.empty:
        return []

    data = df.copy()
    data["date"] = pd.to_datetime(data["date"], errors="raise")

    if frequency == "daily":
        data["period"] = data["date"].dt.strftime("%Y-%m-%d")
    elif frequency == "monthly":
        data["period"] = data["date"].dt.strftime("%Y-%m")
    else:
        data["period"] = data["date"].dt.strftime("%Y")

    documents = []

    for (symbol, period), group in data.groupby(
        ["symbol", "period"], sort=True
    ):
        group = group.sort_values("date")
        first = group.iloc[0]
        last = group.iloc[-1]

        start_close = float(first["close"])
        end_close = float(last["close"])

        return_pct = (
            ((end_close / start_close) - 1) * 100
            if start_close != 0
            else None
        )

        content = (
            f"Asset: {first['asset_name']} ({symbol})\n"
            f"Asset type: {first['asset_type']}\n"
            f"Region: {first['region']}\n"
            f"Period: {period}\n"
            f"First observation date: {first['date'].date()}\n"
            f"Last observation date: {last['date'].date()}\n"
            f"First observed close: {start_close}\n"
            f"Last observed close: {end_close}\n"
            f"Period price change percentage: "
            f"{return_pct:.4f}%\n"
            if return_pct is not None
            else (
                f"Asset: {first['asset_name']} ({symbol})\n"
                f"Asset type: {first['asset_type']}\n"
                f"Region: {first['region']}\n"
                f"Period: {period}\n"
                f"First observed close: {start_close}\n"
                f"Last observed close: {end_close}\n"
                "Period price change percentage: unavailable\n"
            )
        )

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": MARKET_DATA_PATH.name,
                    "document_type": "historical_market_summary",
                    "symbol": str(symbol),
                    "period": str(period),
                    "frequency": frequency,
                },
            )
        )

    return documents


def load_rag_documents() -> list[Document]:
    """Load chunked FAQ content and monthly market summaries."""
    faq_documents = split_financial_documents(
        load_financial_documents()
    )

    market_df = load_market_dataframe()
    market_documents = market_dataframe_to_documents(
        market_df,
        frequency="monthly",
    )

    return faq_documents + market_documents
