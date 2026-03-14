import collections
import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf


@st.cache_data(ttl="1d", show_spinner="Fetching Option Chain Data...")
def fetch_option_data():
    stock_data = collections.defaultdict(dict)

    sp_tickers = pd.read_csv("./data/sp500_companies.csv", sep=",")
    sp_tickers = np.array(sp_tickers["Symbol"].tolist())[:50]

    for ticker in sp_tickers:
        try:
            t = yf.Ticker(ticker)
            expirations = t.options
            if not expirations:
                continue

            stock_data[ticker] = {}
            for exp in expirations:
                chain = t.option_chain(exp)
                calls = chain.calls.copy()
                puts = chain.puts.copy()

                calls["mid"] = (calls["bid"] + calls["ask"]) / 2
                puts["mid"] = (puts["bid"] + puts["ask"]) / 2

                calls = calls[(calls["openInterest"] >= 10) & (calls["bid"] >= 0.05)]
                puts = puts[(puts["openInterest"] >= 10) & (puts["bid"] >= 0.05)]

                exp_date = pd.to_datetime(exp).date()
                stock_data[ticker][exp_date] = {"calls": calls, "puts": puts}

        except Exception:
            stock_data.pop(ticker, None)

    st.session_state["stock_data"] = stock_data
    return stock_data


@st.cache_resource(show_spinner="Getting Stock Price...")
def get_stock_price(ticker):
    t = yf.Ticker(ticker)
    price = t.fast_info["last_price"]
    if not price:
        raise ValueError(f"No price data for {ticker}")
    return np.float64(price)
