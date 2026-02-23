import yfinance as yf
import pandas as pd
import numpy as np
import collections
from datetime import datetime, timezone
from functools import lru_cache
import streamlit as st
from zoneinfo import ZoneInfo

@st.fragment
@st.cache_data(show_spinner=False)
def fetch_option_data(_day_key=None):
    stock_data = collections.defaultdict(dict)
    
    sp_tickers = pd.read_csv('./data/sp500_companies.csv', sep=',')
    sp_tickers = np.array(sp_tickers['Symbol'].tolist())[:20]

    for ticker in sp_tickers:
        yf_icker = yf.Ticker(ticker)
        try:
            options = yf_icker.options
            
            for exp in options:
                opt = yf_icker.option_chain(exp)
                calls = opt.calls
                puts = opt.puts
                
                stock_data[ticker][exp] = {
                    'calls': calls,
                    'puts': puts
                }
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")

    st.session_state['stock_data'] = stock_data
    return stock_data

@st.fragment
def get_stock_price(ticker):
    stock_data = st.session_state.get('stock_data', {})
    if ticker in stock_data:
        exp_dates = list(stock_data[ticker].keys())
        if exp_dates:
            first_exp = exp_dates[0]
            calls = stock_data[ticker][first_exp]['calls']
            if not calls.empty:
                return calls['lastPrice'].iloc[0]
    return None