import streamlit as st

# ------------------------
# Callback functions
# ------------------------
def update_from_decimal():
    st.session_state.vol_percent = st.session_state.vol_decimal * 100

def update_from_percent():
    st.session_state.vol_decimal = st.session_state.vol_percent / 100


# ------------------------
# Main Input Component
# ------------------------
def stock_inputs():
    st.title("Stock Input Parameters")

    S0 = st.number_input("Initial Stock Price (S₀)", min_value=1.0, value=100.0)

    col1, col2 = st.columns(2)

    with col1:
        st.number_input(
            "Volatility (decimal)",
            key="vol_decimal",
            min_value=0.001,
            max_value=2.0,
            step=0.001,
            format="%.4f",
            on_change=update_from_decimal
        )

    with col2:
        st.number_input(
            "Volatility (%)",
            key="vol_percent",
            min_value=0.1,
            max_value=200.0,
            step=0.05,
            format="%.2f",
            on_change=update_from_percent,
            help="0 ≤ σ ≤ 3."
        )

    with st.expander("About Volatility"):
        st.markdown("""
        Volatility represents the degree of variation in asset prices over time.
        It is typically measured as the standard deviation of returns.
        """)

    return S0, st.session_state.vol_decimal
