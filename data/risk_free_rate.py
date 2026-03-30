import numpy as np
import streamlit as st
import yfinance as yf

TREASURY_TICKERS = {
    30: "^IRX",   # 13-week (~3 months) for options <= 30 days
    90: "^IRX",   # 13-week for options <= 90 days
    365: "^FVX",  # 5-year for options <= 1 year
    float("inf"): "^TNX",  # 10-year for anything longer
}

@st.cache_data(ttl="1d")
def get_risk_free_rate(days_to_expiry: int = 365) -> np.float64:
    try:
        ticker = next(v for k, v in TREASURY_TICKERS.items() if days_to_expiry <= k)
        t = yf.Ticker(ticker)
        data = t.history(period="1d")

        if data.empty:
            raise ValueError(f"No data returned for {ticker}")
        risk_free_rate = data["Close"].iloc[0] / 100.0

        return risk_free_rate
    except Exception as e:
        return np.float64(0.04)