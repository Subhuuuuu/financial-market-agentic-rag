
from functools import lru_cache
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "global_financial_markets_2000_Now.csv"
)


@lru_cache(maxsize=1)
def load_market_data() -> pd.DataFrame:
    """Load and validate the historical market dataset."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Market dataset not found: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    required = {
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

    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing columns: {sorted(missing)}"
        )

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    for column in [
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df = df.dropna(
        subset=["date", "symbol", "close"]
    ).copy()

    df["symbol"] = (
        df["symbol"].astype(str).str.strip()
    )
    df["asset_name"] = (
        df["asset_name"].astype(str).str.strip()
    )

    df = df.drop_duplicates(
        subset=["date", "symbol"]
    )

    return (
        df.sort_values(["symbol", "date"])
        .reset_index(drop=True)
    )


def list_assets(
    asset_type: str | None = None,
) -> list[dict]:
    """Return available symbols and their descriptions."""
    df = load_market_data()

    if asset_type:
        df = df[
            df["asset_type"].str.casefold()
            == asset_type.strip().casefold()
        ]

    return (
        df[
            ["symbol", "asset_name", "asset_type", "region"]
        ]
        .drop_duplicates()
        .sort_values(["asset_type", "asset_name"])
        .to_dict(orient="records")
    )


def get_historical_prices(
    symbol: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    """Retrieve OHLCV observations for a symbol."""
    symbol = symbol.strip().upper()

    # Validate the date range before filtering.
    start = (
        pd.to_datetime(start_date, errors="raise")
        if start_date
        else None
    )
    end = (
        pd.to_datetime(end_date, errors="raise")
        if end_date
        else None
    )

    if start is not None and end is not None and start > end:
        return {
            "error": "start_date must be on or before end_date"
        }

    df = load_market_data()
    df = df[df["symbol"].str.upper() == symbol]

    if df.empty:
        return {
            "error": f"Unknown asset symbol: {symbol}"
        }

    if start is not None:
        df = df[df["date"] >= start]

    if end is not None:
        df = df[df["date"] <= end]

    if df.empty:
        return {
            "symbol": symbol,
            "records": [],
            "message": "No records found for this date range.",
        }

    result = df.copy()
    result["date"] = result["date"].dt.strftime("%Y-%m-%d")

    return {
        "symbol": symbol,
        "asset_name": result["asset_name"].iloc[0],
        "record_count": len(result),
        "records": result.to_dict(orient="records"),
    }


def compare_returns(
    symbols: list[str],
    start_date: str,
    end_date: str,
) -> dict:
    """
    Compare close-to-close price returns.

    Uses the last available close on or before the start
    date and the last available close on or before the
    end date. Returns are not dividend-adjusted.
    """
    start = pd.to_datetime(start_date, errors="raise")
    end = pd.to_datetime(end_date, errors="raise")

    if start > end:
        return {
            "error": "start_date must be on or before end_date"
        }

    df = load_market_data()
    results = []

    for requested_symbol in symbols:
        symbol = requested_symbol.strip().upper()

        asset = df[
            df["symbol"].str.upper() == symbol
        ].sort_values("date")

        if asset.empty:
            results.append(
                {
                    "symbol": symbol,
                    "error": "Unknown asset symbol",
                }
            )
            continue

        baseline = asset[asset["date"] <= start].tail(1)
        endpoint = asset[asset["date"] <= end].tail(1)

        if baseline.empty or endpoint.empty:
            results.append(
                {
                    "symbol": symbol,
                    "error": "Insufficient data for this period",
                }
            )
            continue

        initial = float(baseline["close"].iloc[0])
        final = float(endpoint["close"].iloc[0])

        if initial == 0:
            results.append(
                {
                    "symbol": symbol,
                    "error": (
                        "Cannot calculate return from zero baseline"
                    ),
                }
            )
            continue

        results.append(
            {
                "symbol": symbol,
                "asset_name": asset["asset_name"].iloc[0],
                "actual_start_date": (
                    baseline["date"].iloc[0].strftime("%Y-%m-%d")
                ),
                "actual_end_date": (
                    endpoint["date"].iloc[0].strftime("%Y-%m-%d")
                ),
                "initial_close": initial,
                "final_close": final,
                "return_pct": round(
                    (final / initial - 1) * 100,
                    4,
                ),
            }
        )

    return {
        "requested_start_date": start_date,
        "requested_end_date": end_date,
        "method": (
            "Close-to-close price return; excludes dividends, "
            "fees and taxes."
        ),
        "results": results,
    }
