
import re

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.graph.workflow import app as financial_app

app = FastAPI(
    title="Financial Market Intelligence API",
    description=(
        "Multi-agent financial intelligence using hybrid RAG "
        "and historical market data."
    ),
    version="1.0.0",
)


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    session_id: str = "default"


class FeedbackRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    feedback: str = Field(min_length=1, max_length=2000)


def extract_sources(context: str) -> list[str]:
    """Extract source names from retrieved document context."""
    sources = re.findall(
        r"(?m)^Source:\s*(.+?)\s*$",
        context or "",
    )
    return list(dict.fromkeys(sources))


@app.get("/")
def root():
    return {
        "name": "Financial Market Intelligence",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/query")
def query_financial_market(request: QueryRequest):
    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=422,
            detail="Please enter a financial question.",
        )

    try:
        result = financial_app.invoke(
            {
                "query": query,
                "retry_count": 0,
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="The financial analysis workflow failed.",
        ) from exc

    context = result.get("retrieved_context", "") or ""
    answer = (
        result.get("final_answer")
        or result.get("agent_answer")
        or "No answer was generated. Please try a more specific question."
    )

    return {
        "query": query,
        "session_id": request.session_id,
        "intent": result.get("intent", "unknown"),
        "answer": answer,
        "sources": extract_sources(context),
        "retrieved_context": context,
        "market_results": result.get("market_results", {}),
        "evaluation": result.get("evaluation", {}),
    }


@app.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    # Acknowledge feedback; persistent feedback storage is not
    # implemented by this endpoint yet.
    return {
        "status": "received",
        "query": request.query,
        "feedback": request.feedback,
    }
