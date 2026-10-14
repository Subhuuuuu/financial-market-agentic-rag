
from src.agents.market_data_agent import (
    find_matching_symbols,
)

PORTFOLIO_PHRASES = (
    "portfolio",
    "allocation",
    "investment mix",
    "asset mix",
    "rebalance",
    "rebalancing",
)

RISK_PHRASES = (
    "risk assessment",
    "financial risk",
    "risk exposure",
    "risk analysis",
    "assess risk",
    "volatility",
    "concentration risk",
    "market risk",
    "leverage risk",
    "debt risk",
    "high debt",
    "debt",
    "leverage",
)

MARKET_DATA_PHRASES = (
    "historical price",
    "historical prices",
    "closing price",
    "close price",
    "stock price",
    "share price",
    "trading volume",
    "price history",
    "historical data",
    "market data",
    "price return",
    "percentage return",
    "asset return",
    "returns",
    "performance",
    "performing",
    "highest return",
    "lowest return",
    "best performing asset",
    "daily price",
    "monthly price",
    "yearly return",
    "annual return",
)

ANALYSIS_PHRASES = (
    "analyze",
    "analyse",
    "analysis",
    "compare",
    "comparison",
    "insight",
    "trend",
)


def planner(state: dict) -> dict:
    """Route questions to the appropriate specialist agent."""
    query = state.get("query", "").strip().lower()

    if not query:
        intent = "retriever"

    elif any(phrase in query for phrase in PORTFOLIO_PHRASES):
        intent = "portfolio"

    elif any(phrase in query for phrase in RISK_PHRASES):
        intent = "risk"

    else:
        has_market_phrase = any(
            phrase in query for phrase in MARKET_DATA_PHRASES
        )
        has_asset = bool(find_matching_symbols(query))

        explicit_price_request = any(
            phrase in query
            for phrase in (
                "historical price",
                "historical prices",
                "closing price",
                "close price",
                "stock price",
                "share price",
                "trading volume",
                "price history",
                "historical data",
                "market data",
                "daily price",
                "monthly price",
            )
        )

        if explicit_price_request or (
            has_asset and has_market_phrase
        ):
            intent = "market_data"

        elif any(
            phrase in query for phrase in ANALYSIS_PHRASES
        ):
            intent = "analysis"

        else:
            intent = "retriever"

    return {
        "intent": intent,
        "market_data_required": intent == "market_data",
    }


if __name__ == "__main__":
    tests = [
        (
            "What is diversification, and how does it reduce investment risk?",
            "retriever",
        ),
        ("How can high debt increase financial risk?", "risk"),
        ("Analyze my portfolio: Equity 60%, Bonds 30%, Cash 10%.", "portfolio"),
        ("Show S&P 500 performance in 2024", "market_data"),
        ("What is the current ratio?", "retriever"),
    ]

    for query, expected in tests:
        actual = planner({"query": query})["intent"]
        status = "PASS" if actual == expected else "FAIL"
        print(f"{status}: {query} -> {actual}; expected {expected}")
