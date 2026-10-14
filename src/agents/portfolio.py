
import re


def _extract_allocations(query: str) -> dict[str, float]:
    """Extract allocations from formats such as Equity 60% or Equity: 60%."""
    allocation_text = query

    # Remove the instruction before the allocation list, if present.
    if ":" in query:
        allocation_text = query.split(":", maxsplit=1)[1]

    allocations = {}

    pattern = re.compile(
        r"^\s*([A-Za-z][A-Za-z0-9 _&/-]*?)"
        r"\s*(?::|=)?\s*"
        r"(\d+(?:\.\d+)?)\s*%\s*[.!]?\s*$"
    )

    for segment in re.split(r"[,;\n]+", allocation_text):
        match = pattern.match(segment)

        if not match:
            continue

        name = match.group(1).strip(" :=")
        percentage = float(match.group(2))

        if name:
            allocations[name] = percentage

    return allocations


def portfolio_agent(state: dict) -> dict:
    """Analyze user-provided allocations without inventing holdings."""
    query = state.get("query", "").strip()
    allocations = _extract_allocations(query)

    if not allocations:
        answer = (
            "Portfolio Analysis\n\n"
            "Please provide your asset allocation percentages.\n\n"
            "Example: Analyze my portfolio: "
            "Equity 60%, Bonds 30%, Cash 10%.\n\n"
            "No portfolio allocation has been assumed."
        )
        return {"agent_answer": answer}

    if any(
        percentage < 0 or percentage > 100
        for percentage in allocations.values()
    ):
        return {
            "agent_answer": (
                "Invalid allocation: each percentage must be "
                "between 0% and 100%."
            )
        }

    total = sum(allocations.values())

    lines = [
        "Portfolio Allocation Analysis",
        "",
        "Provided allocations:",
    ]

    for name, percentage in allocations.items():
        lines.append(f"- {name}: {percentage:.2f}%")

    lines.extend([
        "",
        f"Total allocation: {total:.2f}%",
    ])

    if abs(total - 100.0) > 0.01:
        lines.append(
            "Warning: allocations do not total 100%. "
            "Check for missing holdings or incorrect percentages."
        )
    else:
        lines.append("Allocation total is consistent with 100%.")

    largest_name, largest_weight = max(
        allocations.items(),
        key=lambda item: item[1],
    )

    lines.extend([
        "",
        "Concentration observations:",
        f"- Largest allocation: {largest_name} ({largest_weight:.2f}%).",
    ])

    if largest_weight >= 70:
        lines.append(
            "A single allocation represents at least 70% of the "
            "portfolio. Review concentration risk."
        )
    elif largest_weight >= 50:
        lines.append(
            "One allocation represents at least half the portfolio. "
            "Review its contribution to overall portfolio risk."
        )
    else:
        lines.append(
            "No single allocation exceeds 50%. This alone does not "
            "prove that the portfolio is adequately diversified."
        )

    lines.extend([
        "",
        (
            "Limitations: This analysis uses only the percentages "
            "provided. It does not calculate asset correlations, "
            "volatility, expected returns, or personalized investment advice."
        ),
    ])

    return {"agent_answer": "\n".join(lines)}
