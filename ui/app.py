
import os
import uuid

import requests
import streamlit as st

API_BASE_URL = os.getenv(
    "FINANCIAL_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

REQUEST_TIMEOUT = 180

st.set_page_config(
    page_title="Financial Market Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state.
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


# Header.
st.title("📈 Financial Market Intelligence")
st.markdown(
    """
    Explore historical financial markets using **Agentic RAG**,
    specialist AI agents, and structured market-data analysis.
    """
)

st.caption(
    "Historical market dataset · Hybrid retrieval · Multi-agent analysis"
)


# Sidebar.
with st.sidebar:
    st.header("About the Project")

    st.write(
        "This application combines a financial knowledge base, "
        "historical market data, and specialized agents for "
        "financial analysis, risk assessment, and portfolio allocation."
    )

    st.divider()

    st.subheader("Example Questions")

    examples = [
        "What is diversification?",
        "How can high debt increase financial risk?",
        "Explain the current ratio.",
        "Show S&P 500 performance in 2024",
        "Compare S&P 500 and NIFTY 50 returns in 2024",
        "Analyze my portfolio: Equity 60%, Bonds 30%, Cash 10%.",
    ]

    for example in examples:
        if st.button(
            example,
            key=f"example_{example}",
            use_container_width=True,
        ):
            st.session_state.pending_query = example
            st.rerun()

    st.divider()

    st.info(
        "The project dataset contains historical observations. "
        "Results are not live market quotes or personalized "
        "investment recommendations."
    )

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# Render previous conversation.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("intent"):
            st.caption(f"Agent route: {message['intent']}")

        if message.get("sources"):
            with st.expander("Sources"):
                for source in message["sources"]:
                    st.write(f"- {source}")

        if message.get("market_results"):
            with st.expander("Structured market-data results"):
                st.json(message["market_results"])

        if message.get("evaluation"):
            with st.expander("Answer evaluation"):
                st.json(message["evaluation"])


def ask_financial_question(query: str) -> None:
    """Send a question to the FastAPI multi-agent workflow."""

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"), st.spinner(
        "Analyzing your question with the financial agents..."
    ):
        try:
            response = requests.post(
                f"{API_BASE_URL}/query",
                json={
                    "query": query,
                    "session_id": st.session_state.session_id,
                },
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()
            data = response.json()

            answer = (
                data.get("answer")
                or "The workflow did not return a final answer."
            )

            intent = data.get("intent", "unknown")
            sources = data.get("sources") or []
            market_results = data.get("market_results") or {}
            evaluation = data.get("evaluation") or {}

            st.markdown(answer)
            st.caption(f"Agent route: {intent}")

            if sources:
                with st.expander("Sources"):
                    for source in sources:
                        st.write(f"- {source}")

            if market_results:
                with st.expander("Structured market-data results"):
                    st.json(market_results)

            if evaluation:
                with st.expander("Answer evaluation"):
                    st.json(evaluation)

            st.session_state.messages.append(
                {
                    "id": str(uuid.uuid4()),
                    "role": "assistant",
                    "content": answer,
                    "query": query,
                    "intent": intent,
                    "sources": sources,
                    "market_results": market_results,
                    "evaluation": evaluation,
                }
            )

        except requests.Timeout:
            error_message = (
                "The request timed out. Please try again with "
                "a more specific question."
            )
            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )

        except requests.RequestException as exc:
            error_message = (
                "Could not connect to the financial API. "
                "Make sure FastAPI is running at "
                f"{API_BASE_URL}.\n\nDetails: {exc}"
            )
            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )


# Chat input.
typed_query = st.chat_input(
    "Ask a question about financial markets, risk, or portfolios..."
)

pending_query = st.session_state.pop("pending_query", None)

if pending_query:
    ask_financial_question(pending_query)
elif typed_query and typed_query.strip():
    ask_financial_question(typed_query.strip())
