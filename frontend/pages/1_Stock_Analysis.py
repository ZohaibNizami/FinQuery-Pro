import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Set the title of the app
st.title("FinQuery Pro")

# Input box for ticker symbol
ticker = st.text_input("Enter Stock Ticker", "AAPL")

# Define API base URL
API_URL = "http://127.0.0.1:8000/api/v1"

# Button to fetch data
if st.button("Fetch Data"):

    # Show a loading spinner while fetching data
    with st.spinner("Fetching data..."):

        # Fetch stock info
        try:
            # Send GET request to fetch stock info
            stock_info_response = requests.get(f"{API_URL}/stocks/{ticker}/info_from_db")
            stock_info_response.raise_for_status()  # Will raise HTTPError for bad responses
            stock_info = stock_info_response.json()
            
            # Extract and display stock info
            company_name = stock_info.get("company_name", None)
            sector = stock_info.get("sector", None)
            industry = stock_info.get("industry", None)
            st.write(f"**Company Name:** {company_name}")
            st.write(f"**Ticker:** {ticker}")
            st.write(f"**Sector:** {sector}")
            st.write(f"**Industry:** {industry}")

           
            # Fetch stock price data
            price_response = requests.get(f"{API_URL}/stocks/{ticker}/prices_from_db?skip=0&limit=100")
            price_response.raise_for_status()
            price_data = price_response.json()
            
            # Convert the price data to a pandas DataFrame
            df = pd.DataFrame(price_data)
            
            # Ensure 'date' column is in datetime format
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # Display a line chart of the adjusted close prices
            
            st.subheader("Stock Prices (Open Price)")
            st.line_chart(df['open_price'])

            st.subheader("Stock Prices (Adjusted Close Price)")
            st.line_chart(df['close_price'])

            st.subheader("Stock Prices (High Price)")
            st.line_chart(df['high_price'])

            st.subheader("Stock Prices (Low Price)")
            st.line_chart(df['low_price'])


            
        except requests.exceptions.HTTPError as errh:
            st.error(f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            st.error(f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            st.error(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            st.error(f"An Error Occurred: {err}")

