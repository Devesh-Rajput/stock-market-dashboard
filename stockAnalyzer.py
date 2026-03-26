# app_dashboard_button.py

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Stock Dashboard", layout="wide")

st.title("📊 Stock Market Dashboard (5 Years)")

# -------------------------------
# Sidebar
# -------------------------------
st.sidebar.header("📌 Controls")

mode = st.sidebar.selectbox(
    "Select Mode",
    ["Single Stock", "Compare Stocks"]
)

# -------------------------------
# Fetch Data
# -------------------------------
@st.cache_data
def fetch_data(ticker):
    data = yf.download(ticker, period="5y", interval="1d")

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    return data

# -------------------------------
# Indicators
# -------------------------------
def add_indicators(data):
    data['MA100'] = data['Close'].rolling(100).mean()
    data['MA200'] = data['Close'].rolling(200).mean()
    return data

# -------------------------------
# Plot Function
# -------------------------------
def plot_chart(data, title):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close'))
    fig.add_trace(go.Scatter(x=data.index, y=data['MA100'], name='MA100'))
    fig.add_trace(go.Scatter(x=data.index, y=data['MA200'], name='MA200'))

    fig.update_layout(
        title=title,
        template="plotly_dark",
        height=600
    )

    return fig

# -------------------------------
# SINGLE STOCK
# -------------------------------
if mode == "Single Stock":

    ticker = st.sidebar.text_input("Enter Stock Ticker", "AAPL").upper()

    run = st.sidebar.button("Analyze Stock")

    if run:
        data = fetch_data(ticker)

        if not data.empty:
            data = add_indicators(data)

            st.subheader(f"📊 {ticker} Stats")

            col1, col2, col3 = st.columns(3)

            col1.metric("Current Price", round(data['Close'].iloc[-1], 2))
            col2.metric("5Y High", round(data['Close'].max(), 2))
            col3.metric("5Y Low", round(data['Close'].min(), 2))

            # Signal
            if data['MA100'].iloc[-1] > data['MA200'].iloc[-1]:
                st.success("📈 BUY SIGNAL (Uptrend)")
            else:
                st.error("📉 SELL SIGNAL (Downtrend)")

            # Chart
            st.plotly_chart(
                plot_chart(data, f"{ticker} - 5Y Analysis"),
                use_container_width=True
            )
        else:
            st.error("❌ Invalid ticker!")

# -------------------------------
# MULTI STOCK
# -------------------------------
elif mode == "Compare Stocks":

    tickers = st.sidebar.text_input(
        "Enter tickers (comma-separated)", 
        "AAPL,MSFT,GOOGL"
    )

    run = st.sidebar.button("Compare Stocks")

    if run:
        tick_list = [t.strip().upper() for t in tickers.split(",")]

        data = yf.download(tick_list, period="5y")['Close']

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        if not data.empty:
            st.subheader("📊 Stock Comparison")

            fig = go.Figure()

            for t in tick_list:
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=data[t],
                    name=t
                ))

            fig.update_layout(
                template="plotly_dark",
                height=600
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("❌ Error fetching data")