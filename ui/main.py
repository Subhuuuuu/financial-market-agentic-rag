
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Financial Market Intelligence",
    page_icon="📊",
)

st.title("Financial Market Intelligence")
st.write("Ask questions about financial analysis and risk.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

query = st.chat_input("Ask a financial question...")

if query:
    st.session_state.messages.append({
        "role": "user",
        "content": query,
    })

    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"), st.spinner(
        "Analyzing financial information..."
    ):
        try:
            response = requests.post(
                f"{API_URL}/query",
                json={
                    "query": query,
                    "session_id": "streamlit-session",
                },
                timeout=120,
            )

            response.raise_for_status()
            result = response.json()
            answer = result.get("answer", "No answer generated.")

            st.write(answer)

            with st.expander("Retrieved Context"):
                st.write(result.get("retrieved_context", ""))

            with st.expander("Evaluation"):
                st.json(result.get("evaluation", {}))

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
            })

        except requests.RequestException as error:
            st.error(f"API request failed: {error}")
