import streamlit as st
import requests


API_URL = "http://localhost:8000/api/v1"

st.title("Insider Trading")
ticker = st.text_input("Enter Ticker Symbol")


if st.button("Get Insider Trading Data"):
    try:
        response = requests.get(f"{API_URL}/insider/{ticker}")
        if response.status_code == 200:
            records = response.json()
            st.dataframe(records)
        else:
            st.error("❌ Failed to fetch Insider Trading")
    except Exception as e:
        st.error(f"Error: {e}")

   