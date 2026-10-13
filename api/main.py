
from fastapi import FastAPI
from pydantic import BaseModel

from src.graph.workflow import app as financial_app

app = FastAPI(
    title="Financial Market Intelligence API",
    description="Agentic RAG for financial information",
    version="1.0.0",
)


class QueryRequest(BaseModel):
    query: str
    session_id: str = "default"


class FeedbackRequest(BaseModel):
    query: str
    feedback: str


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/query")
def query_financial_market(request: QueryRequest):
    result = financial_app.invoke({
        "query": request.query,
        "retry_count": 0,
    })

    return {
        "query": request.query,
        "answer": result.get("final_answer", ""),
        "sources": ["financial_faq.md"],
        "retrieved_context": result.get("retrieved_context", ""),
        "evaluation": result.get("evaluation", {}),
    }


@app.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    return {
        "message": "Feedback received",
        "query": request.query,
        "feedback": request.feedback,
    }
