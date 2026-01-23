import streamlit as st


def stock_inputs():
    st.title("Stock Input Parameters")

    S0 = st.number_input("Initial Stock Price (S₀)", min_value=1.0, value=100.0)

    st.number_input(
        "Volatility (%)",
        key="volatity",
        min_value=0.1,
        max_value=200.0,
        step=0.05,
        format="%.2f",
        help="0 ≤ σ ≤ 3."
    )

    with st.expander("About Volatility"):
        st.markdown("""
        Volatility represents the degree of variation in asset prices over time.
        It is typically measured as the standard deviation of returns.
        """)

    return S0, st.session_state.volatity


def option_inputs():
    st.title("Option Input Parameters")

    exercise = st.selectbox("Exercise Type", ["European", "American"])
    option_type = st.selectbox("Option Type", ["Call", "Put"])
    K = st.number_input(
        "Strike Price (K)",
        min_value=1.0,
        value=100.0,
        help="The price at which the option can be exercised | K > 0"
    )
    T = st.number_input(
        "Time to Maturity (T)",
        min_value=0.03,
        max_value=50.00,
        value=1.00,
        step=0.01,
        help="Time in years until option expiration | T > 0"
    )
    N = st.number_input(
        "Number of Steps (N)",
        min_value=1,
        max_value=5000,
        value=50,
        help="Higher values increase accuracy but also computation time."
    )

    exercise_code = "E" if exercise == "European" else "A"
    option_code = "C" if option_type == "Call" else "P"

    return exercise_code, option_code, K, T, N


def market_inputs():
    st.title("Market Input Parameters")
    r = st.number_input(
        "Risk-Free Rate (r)",
        min_value=0.001,
        max_value=0.50,
        value=0.001,
        step=0.01
    )
    return round(r, 10)


def algorithm_inputs():
    st.title("Algorithm Parameters")

    options = [
        ("Python DP", 1),
        ("NumPy Vectorization", 2),
        ("C++", 3)
    ]

    method = st.selectbox(
        "Computation Method",
        options,
        format_func=lambda x: x[0]
    )

    with st.expander("About Computation Methods"):
        st.markdown("""
        - **Python DP**: Basic dynamic programming approach  
        - **NumPy Vectorization**: Uses array operations for speed  
        - **C++**: High-performance compiled implementation  
        """)

    return method
