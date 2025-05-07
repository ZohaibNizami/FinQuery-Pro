import streamlit as st
import requests

API_URL = "http://localhost:8000/api/v1"

st.title("SEC Filings")
ticker = st.text_input("Enter Ticker Symbol")

if st.button("Fetch Filings"):
    try:
        response = requests.get(f"{API_URL}/filings/{ticker}/from_db")
        if response.status_code == 200:
            data = response.json()
            for record in data:
                record['document_url'] = f"{record['document_url']})"
            st.data_editor(data, use_container_width=True, column_config={
                "document_url": st.column_config.LinkColumn("Document")
            })
        else:
            st.error("❌ Failed to fetch filings")
    except Exception as e:
        st.error(f"Error: {e}")


