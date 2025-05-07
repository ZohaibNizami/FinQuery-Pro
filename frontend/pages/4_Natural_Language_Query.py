import streamlit as st
import requests
import pandas as pd



API_URL = "http://127.0.0.1:8000/api/v1"

st.title("Ask a Question (Natural Language)")

user_query = st.text_area("Enter your question:")

if st.button("Submit Question"):
    if user_query:
        with st.spinner("Thinking..."):
            payload = {"query": user_query}
            try:
                response = requests.post(f"{API_URL}/nlq/nlq/generate-sql", json=payload)
                response.raise_for_status()
                data = response.json()

                st.subheader("Generated SQL:")
                st.code(data.get("generated_sql", ""), language="sql")

                st.subheader("Results:")
                results = data.get("results", [])
                if results:
                    st.dataframe(pd.DataFrame(results))
                else:
                    st.info("No results found.")
            except requests.exceptions.RequestException as e:
                try:
                    error_msg = response.json().get("detail", "An error occurred.")
                except Exception:
                    error_msg = str(e)
                st.error(f"Error: {error_msg}")
    else:
        st.warning("Please enter a question before submitting.")



# Query History Section
API_URL = "http://127.0.0.1:8000/api/v1"

with st.expander("Query History"):
    if st.button("Refresh History"):
        st.experimental_rerun()

    limit = st.number_input("Limit", min_value=1, max_value=20, value=5)

    try:
        # ✅ Now this URL will be correct
        history_response = requests.get(f"{API_URL}/nlq/history?limit={limit}")
        history_response.raise_for_status()
        history_data = history_response.json()
        if history_data:
            df = pd.DataFrame(history_data)
            st.dataframe(df[["user_input", "execution_status", "timestamp"]])
        else:
            st.info("No query history available.")
    except Exception as e:
        st.error(f"Failed to load query history: {e}")
