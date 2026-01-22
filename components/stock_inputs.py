import streamlit as st

# ------------------------
# Main Input Component
# ------------------------
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
