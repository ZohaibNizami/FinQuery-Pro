import streamlit as st
import requests
import pandas as pd


API_URL = "http://localhost:8000/api/v1"

st.title("📊 Analyst Ratings")
ticker = st.text_input("Enter Ticker Symbol")

if st.button("Get Analyst Ratings Data"):
    try:
        response = requests.get(f"{API_URL}/analysts/{ticker}")
        response.raise_for_status()  # Raises an error for non-200 responses

        records = response.json()
        df = pd.DataFrame(records)
        st.subheader("📋 Analyst Ratings Table")
        st.dataframe(df)

        rating_counts = df["rating"].value_counts()
        st.subheader("📊 Ratings Distribution")
        st.bar_chart(rating_counts)

    except Exception as e:
        st.error(f"❌ Error fetching or processing data: {e}")
