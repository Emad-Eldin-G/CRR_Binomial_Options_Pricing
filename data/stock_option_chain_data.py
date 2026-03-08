import yfinance as yf
import pandas as pd
import numpy as np
import collections
import streamlit as st


@st.cache_data(ttl="1d", show_spinner="Fetching Option Chain Data...")
def fetch_option_data():
    stock_data = collections.defaultdict(dict)

    sp_tickers = pd.read_csv("./data/sp500_companies.csv", sep=",")
    sp_tickers = np.array(sp_tickers["Symbol"].tolist())[:20]

    for ticker in sp_tickers:
        yf_icker = yf.Ticker(ticker)
        try:
            options = yf_icker.options

            for exp in options:
                opt = yf_icker.option_chain(exp)
                calls = opt.calls
                puts = opt.puts

                if len(calls) == 0 and len(puts) == 0:
                    continue

                stock_data[ticker][exp] = {"calls": calls, "puts": puts}
        except Exception as e:
            del stock_data[ticker]  # don't include tickers that don't get data
            print(f"Error fetching data for {ticker}: {e}")

    st.session_state["stock_data"] = stock_data
    return stock_data


@st.cache_resource(show_spinner=False)
@st.spinner("Getting Stock Price")
def get_stock_price(ticker):
    t = yf.Ticker(ticker)
    hist = t.history(period="1d")
    if not hist.empty:
        return float(hist["Close"].iloc[-1])
    return None
