
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
)

st.title("📈 Financial Market Intelligence")
st.caption(
    "Agentic RAG · Historical market data · Risk and portfolio analysis"
)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.header("About this application")
    st.write(
        "Ask financial questions using the project's knowledge base "
        "and historical market dataset."
    )
    st.info(
        "Historical dataset only. This application does not provide "
        "live market prices or personalized investment advice."
    )
    st.caption(f"API: {API_BASE_URL}")

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# Render conversation history.
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
            with st.expander("Market-data output"):
                st.json(message["market_results"])

        if message.get("evaluation"):
            with st.expander("Evaluation"):
                st.json(message["evaluation"])

        if message["role"] == "assistant" and message.get("query"):
            feedback_key = f"feedback_{message['id']}"
            col1, col2, _ = st.columns([1, 1, 5])

            for column, label, value in [
                (col1, "👍 Helpful", "helpful"),
                (col2, "👎 Not helpful", "not_helpful"),
            ]:
                if column.button(
                    label,
                    key=f"{feedback_key}_{value}",
                ):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/feedback",
                            json={
                                "query": message["query"],
                                "feedback": value,
                            },
                            timeout=10,
                        )
                        response.raise_for_status()
                        st.toast("Feedback received.")
                    except requests.RequestException:
                        st.error(
                            "Could not submit feedback to the API."
                        )


prompt = st.chat_input(
    "Ask about market history, financial concepts, risk, or allocation..."
)

if prompt and prompt.strip():
    prompt = prompt.strip()

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with (
        st.chat_message("assistant"),
        st.spinner("Running the financial intelligence workflow..."),
    ):
        try:
            response = requests.post(
                f"{API_BASE_URL}/query",
                json={
                    "query": prompt,
                    "session_id": st.session_state.session_id,
                },
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()

            answer = data.get("answer") or (
                "No answer was returned by the workflow."
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
                with st.expander("Market-data output"):
                    st.json(market_results)

            if evaluation:
                with st.expander("Evaluation"):
                    st.json(evaluation)

            st.session_state.messages.append(
                {
                    "id": str(uuid.uuid4()),
                    "role": "assistant",
                    "content": answer,
                    "query": prompt,
                    "intent": intent,
                    "sources": sources,
                    "market_results": market_results,
                    "evaluation": evaluation,
                }
            )

        except requests.Timeout:
            error_message = (
                "The analysis timed out. Try a more specific question "
                "or increase the API timeout."
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
                "Unable to reach the API. Confirm that FastAPI is "
                f"running at {API_BASE_URL}. Details: {exc}"
            )
            st.error(error_message)
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )
