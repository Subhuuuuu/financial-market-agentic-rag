
import re
from collections import defaultdict
from datetime import date

from src.tools.market_data import (
    compare_returns,
    get_historical_prices,
    list_assets,
)


def normalize_text(value: str) -> str:
    """Normalize names and symbols for flexible matching."""
    return re.sub(r"[^a-z0-9]", "", value.lower())


def find_matching_symbols(query: str) -> list[str]:
    """Find asset symbols using names or ticker symbols."""
    normalized_query = normalize_text(query)
    assets = list_assets()
    matches = []

    assets = sorted(
        assets,
        key=lambda asset: max(
            len(normalize_text(str(asset["symbol"]))),
            len(normalize_text(str(asset["asset_name"]))),
        ),
        reverse=True,
    )

    for asset in assets:
        symbol = str(asset["symbol"]).strip()
        name = str(asset["asset_name"]).strip()

        aliases = {
            normalize_text(symbol),
            normalize_text(name),
        }
        aliases.discard("")

        if (
            any(
                alias in normalized_query
                for alias in aliases
                if len(alias) >= 3
            )
            and symbol not in matches
        ):
            matches.append(symbol)

    return matches


def extract_date_range(
    query: str,
) -> tuple[str | None, str | None]:
    """Extract ISO dates or a four-digit calendar year."""
    dates = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", query)

    if len(dates) >= 2:
        start_date, end_date = dates[0], dates[1]
    else:
        years = re.findall(r"\b(?:19|20)\d{2}\b", query)

        if not years:
            return None, None

        year = int(years[0])
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    if start > end:
        raise ValueError(
            "The start date must be on or before the end date."
        )

    return start_date, end_date


def format_comparison(results: dict) -> str:
    """Format historical asset-return comparisons."""
    lines = [
        "Historical Market Return Comparison",
        (
            f"Requested period: {results['requested_start_date']} "
            f"to {results['requested_end_date']}"
        ),
        "",
    ]

    for item in results.get("results", []):
        symbol = item["symbol"]

        if "error" in item:
            lines.append(f"{symbol}: {item['error']}")
            continue

        lines.append(
            f"{item['asset_name']} ({symbol}): "
            f"{item['return_pct']:.2f}% price return, "
            f"from {item['actual_start_date']} "
            f"to {item['actual_end_date']}."
        )

    lines.extend([
        "",
        "Returns exclude dividends, fees, and taxes.",
        "Source: historical market CSV; not live market prices.",
    ])

    return "\n".join(lines)


def summarize_market_records(
    records: list[dict],
    asset_name: str,
    symbol: str,
    start_date: str | None,
    end_date: str | None,
) -> str:
    """Summarize historical prices and monthly performance."""
    if not records:
        return "No historical records were found."

    records = sorted(records, key=lambda row: row["date"])

    first = records[0]
    last = records[-1]

    first_close = float(first["close"])
    last_close = float(last["close"])

    if first_close == 0:
        annual_return = None
    else:
        annual_return = (
            (last_close - first_close) / first_close
        ) * 100

    highest_record = max(
        records,
        key=lambda record: float(record["high"]),
    )
    lowest_record = min(
        records,
        key=lambda record: float(record["low"]),
    )

    monthly_groups = defaultdict(list)

    for record in records:
        month = record["date"][:7]
        monthly_groups[month].append(record)

    lines = [
        f"Historical Performance Summary: {asset_name} ({symbol})",
        "",
        (
            f"Requested period: {start_date or 'dataset start'} "
            f"to {end_date or 'dataset end'}"
        ),
        f"Actual data period: {first['date']} to {last['date']}",
        f"Trading-day observations: {len(records)}",
        "",
        "Overall Performance",
        f"First closing price: {first_close:,.2f} ({first['date']})",
        f"Last closing price: {last_close:,.2f} ({last['date']})",
    ]

    if annual_return is not None:
        lines.append(f"Price return: {annual_return:+.2f}%")
    else:
        lines.append(
            "Price return: unavailable because the first close is zero."
        )

    lines.extend([
        (
            f"Highest daily high: "
            f"{float(highest_record['high']):,.2f} "
            f"({highest_record['date']})"
        ),
        (
            f"Lowest daily low: "
            f"{float(lowest_record['low']):,.2f} "
            f"({lowest_record['date']})"
        ),
        "",
        "Monthly Performance",
    ])

    for month, month_records in sorted(monthly_groups.items()):
        month_records.sort(key=lambda row: row["date"])

        month_first = float(month_records[0]["close"])
        month_last = float(month_records[-1]["close"])

        if month_first == 0:
            monthly_return_text = "unavailable"
        else:
            monthly_return = (
                (month_last - month_first) / month_first
            ) * 100
            monthly_return_text = f"{monthly_return:+.2f}%"

        lines.append(
            f"- {month}: {monthly_return_text} "
            f"({month_records[0]['date']} close "
            f"{month_first:,.2f} → "
            f"{month_records[-1]['date']} close "
            f"{month_last:,.2f})"
        )

    lines.extend([
        "",
        (
            "Method: price return is calculated from the first and "
            "last available closing prices in the selected period. "
            "Monthly returns use the first and last available close "
            "within each calendar month."
        ),
        (
            "Limitations: returns exclude dividends, fees and taxes. "
            "Historical results do not predict future performance."
        ),
        "Source: historical market CSV; not live market prices.",
    ])

    return "\n".join(lines)


def market_data_agent(state: dict) -> dict:
    """Answer historical market questions using CSV-backed tools."""
    query = state.get("query", "").strip()
    query_lower = query.lower()

    if not query:
        message = "Please provide a market-data question."
        return {
            "agent_answer": message,
            "retrieved_context": message,
            "market_results": {},
        }

    try:
        start_date, end_date = extract_date_range(query)
        matched_symbols = find_matching_symbols(query)

        if not matched_symbols:
            message = (
                "I couldn't identify an asset in the dataset. "
                "Please specify an available asset name or ticker."
            )
            return {
                "agent_answer": message,
                "retrieved_context": message,
                "market_results": {},
            }

        comparison_requested = any(
            phrase in query_lower
            for phrase in (
                "compare",
                "comparison",
                "relative performance",
                "versus",
                " vs ",
            )
        )

        return_requested = any(
            phrase in query_lower
            for phrase in (
                "return",
                "returns",
                "performance",
                "performing",
            )
        )

        if comparison_requested or (
            return_requested and len(matched_symbols) > 1
        ):
            if len(matched_symbols) < 2:
                message = (
                    "Please specify at least two assets to compare."
                )
                return {
                    "agent_answer": message,
                    "retrieved_context": message,
                    "market_results": {},
                }

            if not start_date or not end_date:
                message = (
                    "Please specify a year or date range for "
                    "the comparison."
                )
                return {
                    "agent_answer": message,
                    "retrieved_context": message,
                    "market_results": {},
                }

            results = compare_returns(
                matched_symbols,
                start_date,
                end_date,
            )
            answer = format_comparison(results)

            return {
                "market_results": results,
                "agent_answer": answer,
                "retrieved_context": answer,
            }

        if len(matched_symbols) > 1:
            message = (
                "Multiple assets were identified: "
                + ", ".join(matched_symbols)
                + ". Please specify one asset or request a comparison."
            )
            return {
                "agent_answer": message,
                "retrieved_context": message,
                "market_results": {},
            }

        symbol = matched_symbols[0]

        results = get_historical_prices(
            symbol,
            start_date,
            end_date,
        )

        if "error" in results:
            answer = results["error"]
        elif not results.get("records"):
            answer = results.get(
                "message",
                "No historical records were found.",
            )
        else:
            answer = summarize_market_records(
                records=results["records"],
                asset_name=results["asset_name"],
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )

        return {
            "market_results": results,
            "agent_answer": answer,
            "retrieved_context": answer,
        }

    except (ValueError, TypeError, KeyError) as exc:
        message = f"Unable to process the request: {exc}"
        return {
            "agent_answer": message,
            "retrieved_context": message,
            "market_results": {},
        }


if __name__ == "__main__":
    test_queries = [
        "Show S&P 500 performance in 2024",
        "Show historical prices of the S&P 500 in 2024",
        (
            "Compare S&P 500 and NIFTY 50 returns "
            "from 2024-01-01 to 2024-12-31"
        ),
    ]

    for question in test_queries:
        print(f"\n{'=' * 70}\nQuestion: {question}")
        result = market_data_agent({"query": question})
        print(result["agent_answer"])
