import streamlit as st


st.set_page_config(
    page_title="Binomial Option Pricing",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom CSS for styling
with open("static/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.input_components import (
    stock_inputs,
    option_inputs,
    algorithm_inputs,
)
from components.output_components import (
    price_output,
    metrics_output,
    iv_graph_output,
    greeks_output,
    pnl_summary_output,
    pnl_heatmap_output,
)
from algorithm.algorithm_manager import algorithm_manager
from data.stock_option_chain_data import fetch_option_data

# session defaults
st.session_state.setdefault("option_price", None)
st.session_state.setdefault("price_compute_on", False)
st.session_state.setdefault("runtime", None)
st.session_state.setdefault("greeks", None)

# Pre-fetch option chain data on app load
fetch_option_data()

st.write("")
st.write("")

st.markdown(
    body=f"""
    <p class="term-title" style="font-size: 2rem; color: white">
        Cox, Ross and Rubinstein Binomial Method for Options Pricing 💲📈
    </p>

    <hr>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("""
### Created by Emadeldin Osman
""")


def sidebar() -> None:
    with st.sidebar:
        stock_ticker, S0, K = stock_inputs()
        exercise = option_inputs()
        T = algorithm_inputs()

        st.write("")
        if st.button("Compute Option Price", type="primary", width="content"):
            st.session_state.price_compute_on = True

            # Reset previous results for new computation
            st.session_state.option_price = None
            st.session_state.runtime = None
            st.session_state.greeks = None
            st.session_state.risk_free_rate = None

            try:
                algorithm_manager(
                    ticker=stock_ticker, S0=S0, K=K, T=T, optclass=exercise
                )
            except ValueError:
                with st.sidebar:
                    st.warning("No sufficient option chain data")


@st.fragment
def dashboard() -> None:
    # ── Row 1: price + model metrics ─────────────────────────────────
    c1, c2 = st.columns([50, 50], gap="small")
    with c1:
        price_output()
    with c2:
        metrics_output()

    st.write("")

    # ── Row 2: Greeks ─────────────────────────────────────────────────
    greeks_output()

    st.write("")

    # ── Row 3: Analysis tabs ──────────────────────────────────────────
    tab_pnl, tab_iv, tab_heatmap = st.tabs(
        ["P&L Summary", "Implied Volatility Surface", "P&L Scenario Matrix"]
    )

    with tab_pnl:
        pnl_summary_output()

    with tab_iv:
        iv_graph_output()

    with tab_heatmap:
        pnl_heatmap_output()

    st.write("")
    st.write("")


def main() -> None:
    sidebar()
    dashboard()


try:
    main()
except Exception as e:
    st.warning("Something went wrong, please check the error message below:")
    st.warning(e)
