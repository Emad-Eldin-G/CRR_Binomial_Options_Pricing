import numpy as np
import streamlit as st
from datetime import date, timedelta
from data.stock_option_chain_data import fetch_option_data, get_stock_price


@st.fragment
def stock_inputs():
    st.title("Stock Input Parameters")

    stocks = fetch_option_data()

    stock_ticker = st.selectbox(
        "Stock Ticker",
        options=stocks.keys(),
        help="Select a stock ticker to pre-fill option parameters based on real market data.",
    )

    if not stock_ticker:
        st.warning("No stock data available. Check API connection.")
        st.stop()

    stock_price = get_stock_price(ticker=stock_ticker)

    S0 = st.number_input(
        "Initial Stock Price (S₀)",
        min_value=1.0,
        value=stock_price,
        help="Current stock price in the market",
        disabled=True,
    )

    K = st.number_input(
        "Strike Price (K)",
        min_value=1.0,
        value=stock_price,
        help="The price at which the option can be exercised | K > 0",
    )

    with st.expander("About Volatility"):
        st.markdown("""
        Volatility represents the degree of variation in asset prices over time.
        The implied volatility is the volatility that is equivilent to the market price of the option.
        """)

    st.session_state["stock_ticker"] = stock_ticker
    return stock_ticker, S0, K

@st.fragment
def option_inputs():
    st.title("Option Input Parameters")

    exercise = st.selectbox("Exercise Type", ["European", "American"])

    exercise_code = "E" if exercise == "European" else "A"

    with st.expander("About the Risk-Free Rate"):
        st.markdown("""
        The risk-free rate used in this engine is the closest matching rate based on the time to maturity of the option, sourced from current market data.
        """)

    return exercise_code

@st.fragment
def algorithm_inputs():
    st.title("Algorithm Parameters")

    T_picker = st.date_input(
        "Option Expiry Date (T)",
        min_value=date.today() + timedelta(days=1),
        help="Select the option's expiry date. T is automatically calculated from today.",
    )

    T = (T_picker - date.today()).days / 365.25

    N = st.number_input(
        "Number of Steps (N)",
        min_value=1,
        max_value=5000,
        value=1000,
        help="Higher values increase accuracy but also computation time.",
    )

    return T, N
