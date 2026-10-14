
from src.tools.market_data import (
    compare_returns,
    get_historical_prices,
    list_assets,
)


def test_assets_are_available():
    assets = list_assets()
    assert len(assets) == 34


def test_s_and_p_500_prices():
    result = get_historical_prices("^GSPC")

    assert "error" not in result
    assert result["record_count"] > 0
    assert result["records"][-1]["close"] > 0


def test_unknown_symbol():
    result = get_historical_prices("INVALID_SYMBOL")
    assert "error" in result


def test_return_comparison():
    result = compare_returns(
        ["^GSPC", "^NSEI"],
        "2024-01-01",
        "2024-12-31",
    )

    assert len(result["results"]) == 2
    assert all(
        "return_pct" in row
        for row in result["results"]
    )
