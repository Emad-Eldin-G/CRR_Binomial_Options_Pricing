import streamlit as st


st.set_page_config(
    page_title="Binomial Option Pricing",
    layout="wide",
    initial_sidebar_state="expanded",
)

TERMINAL_CSS = """
<style>
.block-container { padding-top: 0.8rem; padding-bottom: 1rem; max-width: 1700px;}
html, body, [class*="css"] {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}
[data-testid="stAppViewContainer"] { background: #0b0f14; }
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
[data-testid="stSidebar"] { background: #0b0f14; border-right: 1px solid rgba(255,255,255,0.08); }

.term-panel {
    min-height: 250px;
    border: 1px solid rgba(255,255,255,0.10);
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    padding: 12px 14px;
}
.term-title {
    font-size: 1.25rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.60);
    margin-bottom: 8px;
}
.term-row {
    display: flex; justify-content: space-between; align-items: baseline;
    padding: 6px 0;
    border-top: 1px dashed rgba(255,255,255,0.10);
}
.term-row:first-of-type { border-top: none; }
.term-k { color: rgba(255,255,255,0.62); font-size: 1.0rem; }
.term-v { color: rgba(255,255,255,0.92); font-size: 2rem; font-weight: 600; }
.term-muted { color: rgba(255,255,255,0.45); font-weight: 650; }

.v-green { color: #2fe47b; }
.v-red   { color: #ff4d4d; }
.v-blue  { color: #57a6ff; }

.tile-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 10px;
}
.term-tile {
    border: 1px solid rgba(255,255,255,0.10);
    background: rgba(255,255,255,0.02);
    border-radius: 10px;
    padding: 10px 12px;
}
.tile-label { color: rgba(255,255,255,0.60); font-size: 1.25rem; }
.tile-value { color: rgba(255,255,255,0.92); font-size: 1.5rem; font-weight: 800; margin-top: 6px; }
</style>
"""
st.markdown(TERMINAL_CSS, unsafe_allow_html=True)

from components.input_components import (
    stock_inputs,
    option_inputs,
    market_inputs,
    algorithm_inputs,
)
from components.output_components import (
    price_output,
    metrics_output,
    iv_graph_output,
    greeks_output,
)
from algorithm.algorithm_manager import alogorithm_manager
from data.stock_option_chain_data import fetch_option_data

# session defaults
st.session_state.setdefault("option_price", None)
st.session_state.setdefault("price_compute_on", False)
st.session_state.setdefault("runtime", None)
st.session_state.setdefault("arb_metrics", None)
st.session_state.setdefault("greeks", None)
st.session_state.setdefault("binomial_tree", None)

fetch_option_data()

st.write("")
st.title("Cox, Ross and Rubinstein Binomial Method for Options Pricing 💲📈")
st.write("--------")

st.sidebar.markdown("## Created by [Emadeldin Osman](https://www.linkedin.com/in/emad-gasser/)")

with st.sidebar:
    stock_ticker, S0 = stock_inputs()
    exercise, K = option_inputs()
    r = market_inputs()
    T, N = algorithm_inputs()

    st.write("")
    if st.button("Compute Option Price", type="primary", width="content"):
        st.session_state.price_compute_on = True

        # Reset previous results for new computation
        st.session_state.option_price = None
        st.session_state.runtime = None
        st.session_state.greeks = None
        st.session_state.binomial_tree = None

        try:
            alogorithm_manager(
                ticker=stock_ticker, S0=S0, K=K, T=T, r=r, N=N, optclass=exercise
            )
        except ValueError:
            with st.sidebar:
                st.warning("No sufficient option chain data")

c1, c2 = st.columns([60, 40], gap="small")
with c1:
    price_output()
with c2:
    metrics_output()

st.write("")

panel = st.container()
with panel:
    c1, c2 = st.columns([45, 55], gap="small")
    with c1:
        greeks_output()
    with c2:
        iv_graph_output()
    
st.write("")
