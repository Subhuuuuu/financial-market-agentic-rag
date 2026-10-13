
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_query_endpoint(monkeypatch):
    def fake_invoke(state):
        return {
            "final_answer": "High debt can increase financial risk.",
            "retrieved_context": "Higher leverage can increase risk.",
            "evaluation": {
                "verdict": "approved",
                "score": 5,
                "feedback": "Response contains information.",
            },
        }

    monkeypatch.setattr("api.main.financial_app.invoke", fake_invoke)

    response = client.post(
        "/query",
        json={"query": "How can high debt increase financial risk?"},
    )

    assert response.status_code == 200
    assert "answer" in response.json()


def test_feedback_endpoint():
    response = client.post("/feedback", json={})

    assert response.status_code in (200, 422)
