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
    min-height: 200px;
    border: 1px solid rgba(255,255,255,0.10);
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    padding: 12px 14px;
}
.term-title {
    font-size: 0.85rem;
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
.term-k { color: rgba(255,255,255,0.62); font-size: 0.85rem; }
.term-v { color: rgba(255,255,255,0.92); font-size: 1.05rem; font-weight: 750; }
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
.tile-label { color: rgba(255,255,255,0.60); font-size: 0.78rem; }
.tile-value { color: rgba(255,255,255,0.92); font-size: 1.05rem; font-weight: 800; margin-top: 6px; }
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
    arb_metrics_output,
    iv_output,
    greeks_output,
    binomial_tree_output,
)
from algorithm.algorithm_manager import alogorithm_manager

# session defaults
st.session_state.setdefault("option_price", None)
st.session_state.setdefault("price_compute_on", False)
st.session_state.setdefault("runtime", None)
st.session_state.setdefault("arb_metrics", None)
st.session_state.setdefault("greeks", None)
st.session_state.setdefault("binomial_tree", None)

st.write("")
st.title("Cox, Ross and Rubinstein Binomial Method for Options Pricing 💲📈")
st.write("")

st.sidebar.markdown("""
## Created by Emadeldin Osman
""")

with st.sidebar:
    S0 = stock_inputs()
    exercise, option_type, K, T, N = option_inputs()
    r = market_inputs()
    method = algorithm_inputs()

    st.write("")
    if st.button("Compute Option Price", type="primary", use_container_width=True):
        st.session_state.price_compute_on = True

        # Reset previous results for new computation
        st.session_state.option_price = None
        st.session_state.runtime = None
        st.session_state.greeks = None
        st.session_state.binomial_tree = None

        alogorithm_manager(S0, K, T, r, N, exercise, method=method)

c1, c2 = st.columns([2, 1], gap="small")
with c1:
    price_output()
    st.write("")  
with c2:
    arb_metrics_output()

iv_output()
st.write("")  
greeks_output()
st.write("")  
binomial_tree_output()
st.write("")  
