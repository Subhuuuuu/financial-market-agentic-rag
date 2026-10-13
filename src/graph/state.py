
from typing import TypedDict


class AgentState(TypedDict, total=False):
    query: str
    intent: str
    retrieved_context: str
    agent_answer: str
    final_answer: str
    evaluation: dict
    retry_count: int
