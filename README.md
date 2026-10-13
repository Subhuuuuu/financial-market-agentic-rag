
# Financial Market Intelligence — Agentic RAG

A Financial Market Intelligence application built using Retrieval-Augmented Generation (RAG), LangGraph, FastAPI, Streamlit, and Docker.

## Features

- Financial document ingestion and text chunking
- Semantic retrieval using FAISS
- Hybrid retrieval using BM25 and vector search
- Multi-agent workflow using LangGraph
- Financial analysis, portfolio guidance, and risk assessment
- Response evaluation and retry workflow
- FastAPI endpoints for querying, health checks, and feedback
- Streamlit chat interface
- Docker containerization
- GitHub Actions CI pipeline for linting, testing, and Docker build validation

## Architecture

```text
Financial FAQ Documents
        |
        v
Document Loading and Chunking
        |
        v
FAISS Vector Store + BM25 Retrieval
        |
        v
LangGraph Workflow
        |
        +--> Planner
        +--> Retriever
        +--> Analysis Agent
        +--> Portfolio Agent
        +--> Risk Assessment Agent
        +--> Evaluator
        |
        v
FastAPI Backend
        |
        v
Streamlit User Interface
```

## Technology Stack

- Python 3.11
- LangChain and LangGraph
- Hugging Face sentence-transformer embeddings
- FAISS and BM25
- FastAPI and Uvicorn
- Streamlit
- Pytest and Ruff
- Docker
- GitHub Actions

## Project Structure

```text
financial-market-agentic-rag/
├── .github/workflows/ci.yml
├── api/
│   └── main.py
├── data/
│   └── financial_faq.md
├── src/
│   ├── agents/
│   ├── graph/
│   ├── ingestion/
│   ├── retrieval/
│   └── tools/
├── tests/
├── ui/
│   └── main.py
├── Dockerfile
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Subhuuuuu/financial-market-agentic-rag.git
cd financial-market-agentic-rag
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install --index-url https://download.pytorch.org/whl/cpu torch
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and configure the variables required by `src/config.py`.

Do not commit `.env` or expose API keys.

### 5. Run the application

Build the FAISS index:

```bash
python -c "from src.retrieval.vector_store import build_vector_store; build_vector_store()"
```

Start the API:

```bash
uvicorn api.main:app --reload
```

Open the API documentation at http://127.0.0.1:8000/docs.

In a separate terminal, activate the virtual environment and start the UI:

```bash
python -m streamlit run ui/main.py
```

Open the Streamlit URL displayed in the terminal, usually http://localhost:8501.

## Docker

Build the image:

```bash
docker build -t financial-market-rag .
```

Run the container:

```bash
docker run -d --name financial-market-rag-container --env-file .env -p 8000:8000 financial-market-rag
```

Open http://127.0.0.1:8000/docs to test the API.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/query` | Query the financial intelligence workflow |
| POST | `/feedback` | Submit feedback |

Use the Swagger interface to inspect request schemas and test each endpoint.

## Testing and CI

Run lint checks:

```bash
ruff check api src tests ui
```

Run automated tests:

```bash
python -m pytest -q
```

GitHub Actions automatically runs lint checks, tests, and a Docker image build when code is pushed to `main` or a pull request targets `main`.

## Limitations

- The current knowledge base uses the available financial FAQ documents.
- Responses do not use live financial market data.
- Portfolio allocations are illustrative and should not be treated as personalized financial advice.
- Evaluation is a basic application-level check, not a comprehensive financial accuracy benchmark.

## Disclaimer

This project is intended for educational and demonstration purposes only. It does not provide personalized investment advice or guarantee financial outcomes.
