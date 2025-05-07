import streamlit as st
import requests

# Set the title of the app
st.title("FinQuery Pro")


API_URL = "http://localhost:8000/api/v1"  

st.title("Company Fundamentals")
ticker = st.text_input("Enter Ticker Symbol")

if st.button("Fetch Fundamentals"):
    try:
        response = requests.get(f"{API_URL}/fundamentals?ticker={ticker}")
        if response.status_code == 200:
            records = response.json()
            st.dataframe(records)
        else:
            st.error("❌ Failed to fetch fundamentals")
    except Exception as e:
        st.error(f"Error: {e}")






