
from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    # Existing workflow fields
    query: str
    intent: str
    retrieved_context: str
    agent_answer: str
    final_answer: str
    evaluation: dict
    retry_count: int

    # Market-data integration
    market_data_required: bool
    market_operation: str
    market_symbols: list[str]
    market_start_date: str
    market_end_date: str
    market_results: dict[str, Any]
