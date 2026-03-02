import streamlit as st
from data.stock_option_chain_data import fetch_option_data, get_stock_price


def stock_inputs():
    st.title("Stock Input Parameters")

    stocks = fetch_option_data()

    stock_ticker = st.selectbox(
        "Stock Ticker",
        options=stocks.keys(),
        help="Select a stock ticker to pre-fill option parameters based on real market data.",
    )

    S0 = st.number_input(
        "Initial Stock Price (S₀)",
        min_value=1.0,
        value=get_stock_price(ticker=stock_ticker),
        help="Current stock price in the market",
        disabled=True,
    )

    with st.expander("About Volatility"):
        st.markdown("""
        Volatility represents the degree of variation in asset prices over time.
        The implied volatility is the volatility that is equivilent to the market price of the option.
        """)

    st.session_state["stock_ticker"] = stock_ticker
    return stock_ticker, S0


def option_inputs():
    st.title("Option Input Parameters")

    exercise = st.selectbox("Exercise Type", ["European", "American"])

    K = st.number_input(
        "Strike Price (K)",
        min_value=1.0,
        value=get_stock_price(ticker=st.session_state.get("stock_ticker", None)),
        help="The price at which the option can be exercised | K > 0",
    )

    exercise_code = "E" if exercise == "European" else "A"

    return exercise_code, K


def market_inputs():
    st.title("Market Input Parameters")
    r = st.number_input(
        "Risk-Free Rate (r)", min_value=0.001, max_value=0.50, value=0.001, step=0.01
    )
    return round(r, 10)


def algorithm_inputs():
    st.title("Algorithm Parameters")

    T = st.number_input(
        "Time to Maturity (T)",
        min_value=0.03,
        max_value=50.00,
        value=1.00,
        step=0.01,
        help="Time in years until option expiration | T > 0",
    )
    N = st.number_input(
        "Number of Steps (N)",
        min_value=1,
        max_value=5000,
        value=1000,
        help="Higher values increase accuracy but also computation time.",
    )

    return T, N
